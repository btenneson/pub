#!/usr/bin/env python3
"""Pin The Gedanbedai of Wake Island as story card #1."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "docs" / "index.html"
SEARCH = ROOT / "docs" / "search-index.json"

TITLE = "The Gedanbedai of Wake Island"
ARCHIVE = "stories/The_Gedanbedai_of_Wake_Island_001.pdf"
SOURCE_PATH = "stories/The_Gedanbedai_of_Wake_Island_001.tex"
PDF_URL = "https://raw.githubusercontent.com/btenneson/pub/main/" + quote(ARCHIVE, safe="/")
OPEN_URL = "https://github.com/btenneson/pub/blob/main/" + quote(ARCHIVE, safe="/")
SOURCE_URL = "https://github.com/btenneson/pub/blob/main/" + quote(SOURCE_PATH, safe="/")
QUOTE = "At last, you have asked a gedanbedai question."
ATTRIBUTION = "Brian Tenneson"


def matches_story(item: dict) -> bool:
    return (
        str(item.get("title") or "") == TITLE
        or str(item.get("archive_path") or "") == ARCHIVE
        or str(item.get("href") or "") in {OPEN_URL, PDF_URL}
    )


def sync_home(items: list[dict]) -> None:
    page = HOME.read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    # Current generated homepage can use either an embedded DATA payload or a
    # FEATURED + fetched search-index scheme. Prefer the DATA replacement when present.
    page2, n = re.subn(
        r"const DATA=.*?;\nconst q=",
        lambda _m: "const DATA=" + data + ";\nconst q=",
        page,
        count=1,
        flags=re.S,
    )
    if n == 1:
        HOME.write_text(page2, encoding="utf-8")
        return

    # Newer homepage: hard-code the story as the first featured item and keep
    # any existing FEATURED card immediately after it.
    story = items[0]
    js = json.dumps(story, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    if "const STORY_FEATURED=" in page:
        page, n = re.subn(r"const STORY_FEATURED=.*?;\n", "const STORY_FEATURED=" + js + ";\n", page, count=1, flags=re.S)
    else:
        page, n = re.subn(r"(const FEATURED=.*?;\n)", "const STORY_FEATURED=" + js + ";\n\\1", page, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError("Could not add STORY_FEATURED to homepage")
    page = page.replace("DATA=[FEATURED,...items.filter(", "DATA=[STORY_FEATURED,FEATURED,...items.filter(", 1)
    # Prevent accidental duplicate story entry from fetched index.
    page = page.replace(
        "x=>x.archive_path!==FEATURED.archive_path&&x.href!==FEATURED.href)",
        "x=>x.archive_path!==STORY_FEATURED.archive_path&&x.href!==STORY_FEATURED.href&&x.archive_path!==FEATURED.archive_path&&x.href!==FEATURED.href)",
        1,
    )
    HOME.write_text(page, encoding="utf-8")


def main() -> None:
    payload = json.loads(SEARCH.read_text(encoding="utf-8"))
    items = [dict(x) for x in payload.get("items", [])]
    found = [x for x in items if matches_story(x)]
    if len(found) > 1:
        raise RuntimeError(f"Expected at most one story card, found {len(found)}")
    if found:
        story = found[0]
        items.remove(story)
    else:
        story = {}

    story.update({
        "title": TITLE,
        "kind": "Story",
        "category": "Stories",
        "tags": ["logic parable", "AMLD", "self-description"],
        "href": OPEN_URL,
        "pdf": PDF_URL,
        "source": SOURCE_URL,
        "archive_path": ARCHIVE,
        "search": " ".join([TITLE, "Stories logic parable AMLD self-description Wake Island gedanbedai", ARCHIVE, QUOTE, ATTRIBUTION]),
        "quote": QUOTE,
        "quote_attribution": ATTRIBUTION,
    })

    items.insert(0, story)
    payload = {"schema_version": 1, "count": len(items), "items": items}
    SEARCH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sync_home(items)
    print("card 1:", story["title"])
    print("category:", story["category"])


if __name__ == "__main__":
    main()
