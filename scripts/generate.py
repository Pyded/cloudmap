#!/usr/bin/env python3
"""Generate README.md and catalog.json from the YAML catalog."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from validate import ROOT, load_catalog


PROVIDER_COLUMNS = (
    ("evolution", "Evolution"),
    ("advanced", "Advanced"),
    ("yandex", "Yandex"),
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


def _provider_cell(resource: dict[str, Any], provider_name: str) -> str:
    provider = resource["providers"].get(provider_name)
    if provider is None:
        return "—"
    service = _escape_table(provider["service"])
    provider_resource = _escape_table(provider["resource"])
    return (
        f"{service} — {provider_resource} "
        f"([документация]({provider['docs']}), [API]({provider['api']}))"
    )


def render_readme(resources: list[dict[str, Any]]) -> str:
    lines = [
        "<!-- Файл сгенерирован scripts/generate.py. Не редактируйте его вручную. -->",
        "",
        "# cloudmap",
        "",
        "Минимальный нейтральный каталог соответствий облачных ресурсов между Cloud.ru Evolution, "
        "Cloud.ru Advanced и Yandex Cloud.",
        "",
        "Источником истины служат YAML-файлы в `catalog/`. `README.md` и `catalog.json` "
        "генерируются из них детерминированно.",
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
        "| Resource | Evolution | Advanced | Yandex |",
        "| --- | --- | --- | --- |",
    ]
    for resource in resources:
        resource_cell = f"`{resource['id']}` — {_escape_table(resource['name'])}"
        cells = [resource_cell]
        cells.extend(_provider_cell(resource, provider) for provider, _ in PROVIDER_COLUMNS)
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    resources = load_catalog()
    readme = render_readme(resources)
    catalog_json = json.dumps({"resources": resources}, ensure_ascii=False, indent=2) + "\n"
    _atomic_write(ROOT / "README.md", readme)
    _atomic_write(ROOT / "catalog.json", catalog_json)
    print(f"Сгенерированы README.md и catalog.json: ресурсов — {len(resources)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
