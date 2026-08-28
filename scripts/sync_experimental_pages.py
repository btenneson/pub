#!/usr/bin/env python3
"""Mirror repository-root pub.experimental into docs/pub.experimental for GitHub Pages.

The source archive remains pub.experimental/. GitHub Pages publishes docs/, so
this script copies the exact file bytes into the Pages tree and writes a small
landing page. It is safe to run repeatedly.
"""
from __future__ import annotations

import html
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pub.experimental"
DEST = ROOT / "docs" / "pub.experimental"


def included(path: Path) -> bool:
    rel = path.relative_to(SOURCE)
    return not any(part.startswith(".") or part.startswith("_") for part in rel.parts)


def main() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)

    files: list[Path] = []
    if SOURCE.exists():
        for src in sorted(SOURCE.rglob("*"), key=lambda p: p.as_posix().casefold()):
            if not src.is_file() or not included(src):
                continue
            rel = src.relative_to(SOURCE)
            dst = DEST / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            files.append(rel)

    rows = []
    for rel in files:
        href = quote(rel.as_posix(), safe="/")
        label = html.escape(rel.as_posix())
        rows.append(f'<li><a href="{href}">{label}</a></li>')

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>pub.experimental — Brian Tenneson</title>
<style>body{font:16px/1.5 system-ui,sans-serif;max-width:1000px;margin:auto;padding:24px}li{margin:.45rem 0}a{overflow-wrap:anywhere}</style>
</head><body><p><a href="../">← Publication Library</a></p><h1>pub.experimental</h1>
<p>Experimental research and working notes. These files are indexed in the main publication library.</p><ul>
""" + "\n".join(rows) + "\n</ul></body></html>\n"
    (DEST / "index.html").write_text(page, encoding="utf-8")
    print(f"mirrored {len(files)} experimental files into {DEST}")


if __name__ == "__main__":
    main()
