#!/usr/bin/env python3
"""Validate the cloud resource catalog and, optionally, its external links."""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
CATEGORIES = frozenset({"compute", "storage", "network", "database"})
PROVIDERS = frozenset({"evolution", "advanced", "yandex"})
RESOURCE_FIELDS = frozenset({"id", "name", "category", "aliases", "providers"})
PROVIDER_FIELDS = frozenset({"service", "resource", "docs", "api"})
SNAKE_CASE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
USER_AGENT = "cloudmap-url-validator/1.0 (+https://github.com/)"


class CatalogError(Exception):
    """An error that makes the catalog invalid."""


class UniqueKeyLoader(yaml.SafeLoader):
    """A YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def _location(path: Path, resource_id: object | None = None) -> str:
    try:
        shown_path = path.relative_to(ROOT)
    except ValueError:
        shown_path = path
    if resource_id is None:
        return str(shown_path)
    return f"{shown_path} [{resource_id}]"


def _require_string(value: object, field: str, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{location}: поле {field!r} должно быть непустой строкой")
    return value


def _is_official_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    hostname = parsed.hostname.lower()
    return (
        hostname == "cloud.ru"
        or hostname.endswith(".cloud.ru")
        or hostname == "yandex.cloud"
        or hostname.endswith(".yandex.cloud")
    )


def _validate_provider(provider: object, data: object, location: str) -> None:
    if provider not in PROVIDERS:
        raise CatalogError(f"{location}: неизвестный провайдер {provider!r}")
    if not isinstance(data, dict):
        raise CatalogError(f"{location}: описание провайдера {provider!r} должно быть объектом")

    fields = set(data)
    missing = PROVIDER_FIELDS - fields
    unknown = fields - PROVIDER_FIELDS
    if missing:
        raise CatalogError(
            f"{location}: у провайдера {provider!r} отсутствуют поля: {', '.join(sorted(missing))}"
        )
    if unknown:
        raise CatalogError(
            f"{location}: у провайдера {provider!r} неизвестные поля: {', '.join(sorted(map(str, unknown)))}"
        )

    for field in sorted(PROVIDER_FIELDS):
        value = _require_string(data[field], f"providers.{provider}.{field}", location)
        if field in {"docs", "api"} and not _is_official_url(value):
            raise CatalogError(
                f"{location}: providers.{provider}.{field} должен быть HTTPS-ссылкой "
                "на официальный домен Cloud.ru или Yandex Cloud"
            )


def _validate_resource(resource: object, path: Path, category: str, index: int) -> dict[str, Any]:
    fallback_location = f"{_location(path)} [resources[{index}]]"
    if not isinstance(resource, dict):
        raise CatalogError(f"{fallback_location}: ресурс должен быть объектом")

    resource_id = resource.get("id", f"resources[{index}]")
    location = _location(path, resource_id)
    fields = set(resource)
    missing = RESOURCE_FIELDS - fields
    unknown = fields - RESOURCE_FIELDS
    if missing:
        raise CatalogError(f"{location}: отсутствуют поля: {', '.join(sorted(missing))}")
    if unknown:
        raise CatalogError(f"{location}: неизвестные поля: {', '.join(sorted(map(str, unknown)))}")

    resource_id = _require_string(resource["id"], "id", location)
    if not SNAKE_CASE.fullmatch(resource_id):
        raise CatalogError(f"{location}: id должен быть в английском snake_case")

    name = _require_string(resource["name"], "name", location)
    if not CYRILLIC.search(name):
        raise CatalogError(f"{location}: name должен содержать кириллицу")

    resource_category = _require_string(resource["category"], "category", location)
    if resource_category not in CATEGORIES:
        raise CatalogError(f"{location}: неизвестная категория {resource_category!r}")
    if resource_category != category:
        raise CatalogError(
            f"{location}: категория {resource_category!r} не совпадает с именем файла {category!r}"
        )

    aliases = resource["aliases"]
    if not isinstance(aliases, list):
        raise CatalogError(f"{location}: aliases должен быть списком")
    seen_aliases: set[str] = set()
    for alias in aliases:
        if not isinstance(alias, str) or not SNAKE_CASE.fullmatch(alias):
            raise CatalogError(f"{location}: каждый alias должен быть в английском snake_case")
        if alias in seen_aliases:
            raise CatalogError(f"{location}: повторяющийся alias {alias!r}")
        seen_aliases.add(alias)

    providers = resource["providers"]
    if not isinstance(providers, dict):
        raise CatalogError(f"{location}: providers должен быть объектом")
    for provider, data in providers.items():
        _validate_provider(provider, data, location)

    return resource


def load_catalog(catalog_dir: Path = CATALOG_DIR) -> list[dict[str, Any]]:
    """Load and structurally validate every category file."""
    if not catalog_dir.is_dir():
        raise CatalogError(f"{catalog_dir}: каталог не найден")

    paths = sorted(catalog_dir.glob("*.yaml"))
    actual_categories = {path.stem for path in paths}
    missing_categories = CATEGORIES - actual_categories
    unknown_categories = actual_categories - CATEGORIES
    if missing_categories:
        raise CatalogError(f"catalog: отсутствуют категории: {', '.join(sorted(missing_categories))}")
    if unknown_categories:
        raise CatalogError(f"catalog: неизвестные категории: {', '.join(sorted(unknown_categories))}")

    resources: list[dict[str, Any]] = []
    ids: dict[str, Path] = {}
    for path in paths:
        try:
            document = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise CatalogError(f"{_location(path)}: не удалось прочитать YAML: {exc}") from exc

        if not isinstance(document, dict):
            raise CatalogError(f"{_location(path)}: корнем YAML должен быть объект")
        if set(document) != {"resources"}:
            missing = {"resources"} - set(document)
            unknown = set(document) - {"resources"}
            details: list[str] = []
            if missing:
                details.append("отсутствует поле resources")
            if unknown:
                details.append(f"неизвестные поля: {', '.join(sorted(map(str, unknown)))}")
            raise CatalogError(f"{_location(path)}: {'; '.join(details)}")
        if not isinstance(document["resources"], list):
            raise CatalogError(f"{_location(path)}: resources должен быть списком")

        for index, raw_resource in enumerate(document["resources"]):
            resource = _validate_resource(raw_resource, path, path.stem, index)
            resource_id = resource["id"]
            if resource_id in ids:
                raise CatalogError(
                    f"{_location(path, resource_id)}: id уже используется в {_location(ids[resource_id])}"
                )
            ids[resource_id] = path
            resources.append(resource)

    return sorted(resources, key=lambda resource: (resource["category"], resource["id"]))


def catalog_urls(resources: list[dict[str, Any]]) -> list[str]:
    return sorted(
        {
            provider[field]
            for resource in resources
            for provider in resource["providers"].values()
            for field in ("docs", "api")
        }
    )


def _check_url(url: str, retries: int = 2, timeout: float = 15.0) -> str | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    last_error = "неизвестная ошибка"
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = response.status
                final_url = response.geturl()
                if not _is_official_url(final_url):
                    return f"редирект на неофициальный URL {final_url}"
                if 200 <= status < 300:
                    return None
                last_error = f"HTTP {status}"
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code < 500 and exc.code != 429:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc.reason if isinstance(exc, urllib.error.URLError) else exc)
        if attempt < retries:
            time.sleep(0.5 * (attempt + 1))
    return last_error


def check_urls(resources: list[dict[str, Any]]) -> None:
    urls = catalog_urls(resources)
    errors: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=min(8, len(urls) or 1)) as executor:
        futures = {executor.submit(_check_url, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            error = future.result()
            if error:
                errors.append((url, error))
    if errors:
        lines = ["проверка URL завершилась с ошибками:"]
        lines.extend(f"  {url}: {error}" for url, error in sorted(errors))
        raise CatalogError("\n".join(lines))
    print(f"Проверено URL: {len(urls)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-urls", action="store_true", help="проверить доступность всех ссылок")
    args = parser.parse_args(argv)

    try:
        resources = load_catalog()
        if args.check_urls:
            check_urls(resources)
    except CatalogError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1

    print(f"Каталог корректен: ресурсов — {len(resources)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
