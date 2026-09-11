#!/usr/bin/env python3
"""Build the current white portfolio into dist/."""

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def ignore_junk(_folder, names):
    return {name for name in names if name == ".DS_Store" or name.startswith("._")}


subprocess.run(["python3", "build-portfolio-manifest.py"], cwd=ROOT, check=True)
subprocess.run(["npm", "exec", "vite", "--", "build"], cwd=ROOT, check=True)

shutil.copy2(ROOT / "portfolio-manifest.json", DIST / "portfolio-manifest.json")
shutil.copy2(ROOT / "info.html", DIST / "info.html")
shutil.copytree(ROOT / "web-media", DIST / "web-media",
                dirs_exist_ok=True, ignore=ignore_junk)

for path in DIST.rglob("*"):
    if path.is_file() and (path.name == ".DS_Store" or path.name.startswith("._")):
        path.unlink()

size = sum(path.stat().st_size for path in DIST.rglob("*") if path.is_file())
print(f"OK → dist/: {size / 1024**2:.0f} МБ")
