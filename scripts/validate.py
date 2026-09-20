#!/usr/bin/env python3
"""Validate evo_crossmap resources, sources, references, and external links."""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = ROOT / "resources"
SOURCES_DIR = ROOT / "sources"
PROVIDERS = frozenset({"cloudru_evolution", "cloudru_advanced", "yandex_cloud"})
RESOURCE_FIELDS = frozenset({"id", "name", "providers"})
RESOURCE_PROVIDER_FIELDS = frozenset({"name", "sources"})
SOURCE_FIELDS = frozenset({"id", "provider", "name", "docs", "api"})
SNAKE_CASE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
USER_AGENT = "evo-crossmap-url-validator/2.0 (+https://github.com/Pyded/evo_crossmap)"


class CatalogError(Exception):
    """An error that makes the catalog invalid."""


class UniqueKeyLoader(yaml.SafeLoader):
    """A YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(
    loader: UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
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


def _location(path: Path, item_id: object | None = None) -> str:
    try:
        shown_path = path.relative_to(ROOT)
    except ValueError:
        shown_path = path
    return str(shown_path) if item_id is None else f"{shown_path} [{item_id}]"


def _require_string(value: object, field: str, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{location}: поле {field!r} должно быть непустой строкой")
    return value


def _require_fields(
    document: dict[Any, Any],
    expected: frozenset[str],
    location: str,
) -> None:
    fields = set(document)
    missing = expected - fields
    unknown = fields - expected
    if missing:
        raise CatalogError(f"{location}: отсутствуют поля: {', '.join(sorted(missing))}")
    if unknown:
        raise CatalogError(
            f"{location}: неизвестные поля: {', '.join(sorted(map(str, unknown)))}"
        )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        document = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise CatalogError(f"{_location(path)}: не удалось прочитать YAML: {exc}") from exc
    if not isinstance(document, dict):
        raise CatalogError(f"{_location(path)}: корнем YAML должен быть объект")
    return document


def _validate_id(document: dict[str, Any], path: Path) -> tuple[str, str]:
    raw_id = document.get("id", path.stem)
    location = _location(path, raw_id)
    item_id = _require_string(raw_id, "id", location)
    if not SNAKE_CASE.fullmatch(item_id):
        raise CatalogError(f"{location}: id должен быть в английском snake_case")
    if item_id != path.stem:
        raise CatalogError(
            f"{location}: id {item_id!r} не совпадает с именем файла {path.stem!r}"
        )
    return item_id, location


def _validate_resource(path: Path) -> dict[str, Any]:
    resource = _load_yaml(path)
    _, location = _validate_id(resource, path)
    _require_fields(resource, RESOURCE_FIELDS, location)

    name = _require_string(resource["name"], "name", location)
    if not CYRILLIC.search(name):
        raise CatalogError(f"{location}: name должен содержать кириллицу")

    providers = resource["providers"]
    if not isinstance(providers, dict) or not providers:
        raise CatalogError(f"{location}: providers должен быть непустым объектом")
    for provider, mapping in providers.items():
        if provider not in PROVIDERS:
            raise CatalogError(f"{location}: неизвестный провайдер {provider!r}")
        if not isinstance(mapping, dict):
            raise CatalogError(f"{location}: providers.{provider} должен быть объектом")
        _require_fields(mapping, RESOURCE_PROVIDER_FIELDS, f"{location} providers.{provider}")
        _require_string(mapping["name"], f"providers.{provider}.name", location)
        source_ids = mapping["sources"]
        if not isinstance(source_ids, list) or not source_ids:
            raise CatalogError(
                f"{location}: providers.{provider}.sources должен быть непустым списком"
            )
        seen: set[str] = set()
        for source_id in source_ids:
            if not isinstance(source_id, str) or not SNAKE_CASE.fullmatch(source_id):
                raise CatalogError(
                    f"{location}: каждый source id у {provider!r} должен быть в snake_case"
                )
            if source_id in seen:
                raise CatalogError(f"{location}: повторяющийся source {source_id!r}")
            seen.add(source_id)
    return resource


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


def _validate_url_list(value: object, field: str, location: str) -> None:
    if not isinstance(value, list) or not value:
        raise CatalogError(f"{location}: {field} должен быть непустым списком")
    seen: set[str] = set()
    for url in value:
        if not isinstance(url, str) or not _is_official_url(url):
            raise CatalogError(
                f"{location}: каждый URL в {field} должен быть HTTPS-ссылкой "
                "на официальный домен Cloud.ru или Yandex Cloud"
            )
        if url in seen:
            raise CatalogError(f"{location}: повторяющийся URL в {field}: {url}")
        seen.add(url)


def _validate_source(path: Path) -> dict[str, Any]:
    source = _load_yaml(path)
    _, location = _validate_id(source, path)
    _require_fields(source, SOURCE_FIELDS, location)

    provider = _require_string(source["provider"], "provider", location)
    if provider not in PROVIDERS:
        raise CatalogError(f"{location}: неизвестный провайдер {provider!r}")
    _require_string(source["name"], "name", location)
    _validate_url_list(source["docs"], "docs", location)
    _validate_url_list(source["api"], "api", location)
    return source


def _load_directory(
    directory: Path,
    validator: Callable[[Path], dict[str, Any]],
) -> list[dict[str, Any]]:
    if not directory.is_dir():
        raise CatalogError(f"{directory}: каталог не найден")
    paths = sorted(directory.glob("*.yaml"))
    if not paths:
        raise CatalogError(f"{directory}: YAML-файлы не найдены")
    items = [validator(path) for path in paths]
    ids: dict[str, Path] = {}
    for path, item in zip(paths, items):
        item_id = item["id"]
        if item_id in ids:
            raise CatalogError(
                f"{_location(path, item_id)}: id уже используется в {_location(ids[item_id])}"
            )
        ids[item_id] = path
    return sorted(items, key=lambda item: item["id"])


def load_catalog(
    resources_dir: Path = RESOURCES_DIR,
    sources_dir: Path = SOURCES_DIR,
) -> dict[str, list[dict[str, Any]]]:
    """Load and validate resource files, source files, and all references."""
    resources = _load_directory(resources_dir, _validate_resource)
    sources = _load_directory(sources_dir, _validate_source)
    sources_by_id = {source["id"]: source for source in sources}
    referenced_sources: set[str] = set()

    for resource in resources:
        resource_path = resources_dir / f"{resource['id']}.yaml"
        location = _location(resource_path, resource["id"])
        for provider, mapping in resource["providers"].items():
            for source_id in mapping["sources"]:
                source = sources_by_id.get(source_id)
                if source is None:
                    raise CatalogError(f"{location}: неизвестный source {source_id!r}")
                if source["provider"] != provider:
                    raise CatalogError(
                        f"{location}: source {source_id!r} принадлежит {source['provider']!r}, "
                        f"а не {provider!r}"
                    )
                referenced_sources.add(source_id)

    unused_sources = set(sources_by_id) - referenced_sources
    if unused_sources:
        raise CatalogError(f"sources: неиспользуемые источники: {', '.join(sorted(unused_sources))}")
    return {"resources": resources, "sources": sources}


def catalog_urls(catalog: dict[str, list[dict[str, Any]]]) -> list[str]:
    return sorted(
        {
            url
            for source in catalog["sources"]
            for field in ("docs", "api")
            for url in source[field]
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


def check_urls(catalog: dict[str, list[dict[str, Any]]]) -> None:
    urls = catalog_urls(catalog)
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
        catalog = load_catalog()
        if args.check_urls:
            check_urls(catalog)
    except CatalogError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    print(
        f"Каталог корректен: ресурсов — {len(catalog['resources'])}, "
        f"источников — {len(catalog['sources'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
