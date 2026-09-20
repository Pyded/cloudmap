#!/usr/bin/env python3
"""Generate README.md and catalog.json from resources and sources."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from validate import ROOT, load_catalog


PROVIDER_COLUMNS = (
    ("cloudru_evolution", "Cloud.ru Evolution"),
    ("cloudru_advanced", "Cloud.ru Advanced"),
    ("yandex_cloud", "Yandex Cloud"),
)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _links(label: str, urls: list[str]) -> str:
    if len(urls) == 1:
        return f"[{label}]({urls[0]})"
    return ", ".join(f"[{label} {index}]({url})" for index, url in enumerate(urls, 1))


def _provider_cell(
    resource: dict[str, Any],
    provider_id: str,
    sources: dict[str, dict[str, Any]],
) -> str:
    mapping = resource["providers"].get(provider_id)
    if mapping is None:
        return "—"
    source_links = []
    for source_id in mapping["sources"]:
        source = sources[source_id]
        source_links.append(
            f"{_escape_table(source['name'])} "
            f"({_links('документация', source['docs'])}; {_links('API', source['api'])})"
        )
    return f"{_escape_table(mapping['name'])}<br>{'<br>'.join(source_links)}"


def render_readme(catalog: dict[str, list[dict[str, Any]]]) -> str:
    resources = catalog["resources"]
    sources_by_id = {source["id"]: source for source in catalog["sources"]}
    lines = [
        "<!-- Файл сгенерирован scripts/generate.py. Не редактируйте его вручную. -->",
        "",
        "# cloudmap",
        "",
        "Нейтральный каталог соответствий облачных ресурсов между Cloud.ru Evolution, "
        "Cloud.ru Advanced и Yandex Cloud.",
        "",
        "Источником истины служат отдельные YAML-файлы:",
        "",
        "- `resources/` — нейтральные ресурсы и их соответствия у провайдеров;",
        "- `sources/` — официальные страницы документации и API, на которые ссылаются ресурсы.",
        "",
        "`README.md` и `catalog.json` генерируются из них детерминированно.",
        "",
        "## Проверка и генерация",
        "",
        "```bash",
        "python -m pip install -r requirements.txt",
        "python scripts/validate.py",
        "python scripts/validate.py --check-urls",
        "python scripts/generate.py",
        "```",
        "",
        "## Каталог",
        "",
        "| Resource | Cloud.ru Evolution | Cloud.ru Advanced | Yandex Cloud |",
        "| --- | --- | --- | --- |",
    ]
    for resource in resources:
        cells = [f"`{resource['id']}` — {_escape_table(resource['name'])}"]
        cells.extend(
            _provider_cell(resource, provider_id, sources_by_id)
            for provider_id, _ in PROVIDER_COLUMNS
        )
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    catalog = load_catalog()
    _atomic_write(ROOT / "README.md", render_readme(catalog))
    _atomic_write(
        ROOT / "catalog.json",
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
    )
    print(
        f"Сгенерированы README.md и catalog.json: ресурсов — {len(catalog['resources'])}, "
        f"источников — {len(catalog['sources'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
