#!/usr/bin/env python3
"""Build and verify the site manifest from the portfolio folders."""

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / "web-media" / "Портфолио"
PHOTOS = MEDIA / "Фото"
OUT = ROOT / "portfolio-manifest.json"
EXTENSIONS = {".avif", ".jpeg", ".jpg", ".png", ".webp"}
COVER_OVERRIDES = {
    "Мастеркласс шары": "_MG_9681-compressed.webp",
    "Москвоская неделя моды": "0908.webp",
    "Предметная съемка чокеров": "Семка_Чекеры_-086-2-compressed.webp",
    "Проект SKINS": "_MG_5279-compressed.webp",
    "Показ FABRIKATOR": "_MG_0663-compressed.webp",
    "Фотосессия бекстейдж": "_MG_9765-compressed.webp",
    "Съемка в СитиМОЛЕ": "_MG_9533-compressed.webp",
    "Съемка энджел блесс с блогерами": "_MG_0020-compressed.webp",
    "Фотосесия \"Хогвартс\"": "_MG_9831-compressed.webp",
    "Фотосессия в центре ": "_MG_9887-compressed.webp",
}


def natural_key(value: str):
    return [int(part) if part.isdigit() else part.casefold()
            for part in re.split(r"(\d+)", value)]


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def image_files(folder: Path):
    return sorted(
        (path for path in folder.iterdir()
         if path.is_file()
         and not path.name.startswith(".")
         and not path.name.startswith("._")
         and path.suffix.casefold() in EXTENSIONS),
        key=lambda path: natural_key(path.name),
    )


def web_path(path: Path) -> str:
    # Git stores the published paths in NFC while macOS exposes filenames in a
    # decomposed form. Emit one stable form so the same manifest works locally,
    # in clean checkouts, and on case-sensitive static hosts.
    return nfc(path.relative_to(ROOT).as_posix())


def image_dimensions(path: Path):
    result = subprocess.run(
        ["identify", "-format", "%w %h", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    width, height = (int(value) for value in result.stdout.split())
    return [width, height]


def build_manifest():
    if not PHOTOS.is_dir():
        sys.exit("Не найдена папка web-media/Портфолио/Фото")

    projects = []
    for folder in sorted((p for p in PHOTOS.rglob("*") if p.is_dir()),
                         key=lambda path: natural_key(path.as_posix())):
        files = image_files(folder)
        if not files:
            continue
        relative = folder.relative_to(PHOTOS)
        parents = relative.parts[:-1]
        cover = COVER_OVERRIDES.get(nfc(folder.name), files[0].name)
        if cover not in {path.name for path in files}:
            sys.exit(f"Не найдена обложка {cover!r} для проекта {folder.name!r}")
        projects.append({
            "title": nfc(folder.name),
            "group": " / ".join(nfc(parent) for parent in parents),
            "dir": web_path(folder),
            "files": [path.name for path in files],
            "dimensions": {path.name: image_dimensions(path) for path in files},
            "cover": cover,
        })

    if not projects:
        sys.exit("Портфолио пусто")
    return {"projects": projects}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="проверить, что манифест актуален")
    args = parser.parse_args()
    expected = build_manifest()

    if args.check:
        if not OUT.is_file():
            sys.exit("portfolio-manifest.json не найден")
        current = json.loads(OUT.read_text(encoding="utf-8"))
        if current != expected:
            sys.exit("portfolio-manifest.json устарел: запустите генератор без --check")
        print(f"OK: {len(expected['projects'])} проектов, "
              f"{sum(len(p['files']) for p in expected['projects'])} фото")
        return

    OUT.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"OK → {OUT.name}: {len(expected['projects'])} проектов, "
          f"{sum(len(p['files']) for p in expected['projects'])} фото")


if __name__ == "__main__":
    main()
