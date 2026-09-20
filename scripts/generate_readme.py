#!/usr/bin/env python3
"""Update the generated catalog table in README.md."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog.yaml"
README_PATH = ROOT / "README.md"
START_MARKER = "<!-- catalog-table:start -->"
END_MARKER = "<!-- catalog-table:end -->"
PROVIDERS = (
    ("evolution", "Evolution"),
    ("advanced", "Advanced"),
    ("yandex", "Yandex"),
)


def _escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _links(label: str, urls: list[str]) -> str:
    if len(urls) == 1:
        return f"[{label}]({urls[0]})"
    return ", ".join(
        f"[{label} {index}]({url})" for index, url in enumerate(urls, start=1)
    )


def _service(service: dict[str, Any]) -> str:
    links = []
    if service.get("docs"):
        links.append(_links("документация", service["docs"]))
    if service.get("api"):
        links.append(_links("API", service["api"]))
    suffix = f" ({'; '.join(links)})" if links else ""
    return f"{_escape(service['name'])}{suffix}"


def _provider_cell(resource: dict[str, Any], provider_id: str) -> str:
    provider = resource.get(provider_id)
    if provider is None:
        return "—"
    services = provider.get("services")
    if services is not None:
        return "<br>".join(_service(service) for service in services)
    return _service(provider)


def render_table(catalog: list[dict[str, Any]]) -> str:
    lines = [
        "| Resource | Evolution | Advanced | Yandex |",
        "| --- | --- | --- | --- |",
    ]
    for resource in catalog:
        cells = [f"`{resource['id']}` — {_escape(resource['name'])}"]
        cells.extend(_provider_cell(resource, provider_id) for provider_id, _ in PROVIDERS)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    catalog = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(catalog, list):
        raise ValueError("catalog.yaml must contain a root list")

    readme = README_PATH.read_text(encoding="utf-8")
    if readme.count(START_MARKER) != 1 or readme.count(END_MARKER) != 1:
        raise ValueError("README.md must contain exactly one generated table block")
    before, remainder = readme.split(START_MARKER, maxsplit=1)
    _, after = remainder.split(END_MARKER, maxsplit=1)
    generated = f"{START_MARKER}\n{render_table(catalog)}\n{END_MARKER}"
    README_PATH.write_text(f"{before}{generated}{after}", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
