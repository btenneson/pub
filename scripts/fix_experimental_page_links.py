#!/usr/bin/env python3
"""Rewrite generated Experimental links to the GitHub Pages mirror."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
SEARCH = ROOT / "docs" / "search-index.json"
GITHUB_BLOB = "https://github.com/btenneson/pub/blob/main/pub.experimental/"
GITHUB_TREE = "https://github.com/btenneson/pub/tree/main/pub.experimental"
RAW = "https://raw.githubusercontent.com/btenneson/pub/main/pub.experimental/"
PAGES = "pub.experimental/"


def main() -> None:
    data = json.loads(SEARCH.read_text(encoding="utf-8"))
    for item in data.get("items", []):
        if item.get("kind") != "Experimental":
            continue
        archive = str(item.get("archive_path") or "")
        prefix = "pub.experimental/"
        if not archive.startswith(prefix):
            continue
        rel = archive[len(prefix):]
        href = PAGES + quote(rel, safe="/")
        item["href"] = href
        if str(item.get("pdf") or ""):
            item["pdf"] = href
        if str(item.get("source") or ""):
            item["source"] = href
    SEARCH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    page = INDEX.read_text(encoding="utf-8")
    page = page.replace(GITHUB_TREE, PAGES)
    page = page.replace(GITHUB_BLOB, PAGES)
    page = page.replace(RAW, PAGES)
    INDEX.write_text(page, encoding="utf-8")
    print("rewrote experimental links to GitHub Pages mirror")


if __name__ == "__main__":
    main()
