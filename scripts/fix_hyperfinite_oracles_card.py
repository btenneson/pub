#!/usr/bin/env python3
"""Keep Hyperfinite Oracles as card #2 with a true HTML Read target."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
SEARCH = ROOT / "docs" / "search-index.json"
TITLE = "The Hyperfinite Oracles of DATA MIND 3.2"
READER_HREF = "papers/hyperfinite_oracles_data_mind_3_2/"
DIRECT_PDF = READER_HREF + "The_Hyperfinite_Oracles_of_DATA_MIND_3_2.pdf"
ARCHIVE = "cs.LO_Logic_in_Computer_Science/The_Hyperfinite_Oracles_of_DATA_MIND_3_2.pdf"
SOURCE = READER_HREF + "source.html"
QUOTE = "The oracle may direct attention; it may not manufacture certified knowledge."
ATTRIBUTION = "Brian Tenneson and ChatGPT"


def is_match(item: dict) -> bool:
    return (
        str(item.get("href") or "") in {READER_HREF, DIRECT_PDF}
        or str(item.get("archive_path") or "") == ARCHIVE
        or str(item.get("title") or "") == TITLE
    )


def main() -> None:
    payload = json.loads(SEARCH.read_text(encoding="utf-8"))
    items = [dict(x) for x in payload.get("items", [])]
    matches = [x for x in items if is_match(x)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one Hyperfinite Oracles publication, found {len(matches)}")

    item = matches[0]
    items = [x for x in items if x is not item]

    item["title"] = TITLE
    item["kind"] = "Core paper"
    item["category"] = "Research Papers"
    item["tags"] = []
    item["href"] = READER_HREF
    item["pdf"] = DIRECT_PDF
    item["source"] = SOURCE
    item["archive_path"] = ARCHIVE
    item["quote"] = QUOTE
    item["quote_attribution"] = ATTRIBUTION
    item["search"] = " ".join(
        [TITLE, "Research Papers", "hyperfinite_oracles_data_mind_3_2", ARCHIVE, QUOTE, ATTRIBUTION]
    )
    items.insert(min(1, len(items)), item)

    payload = {"schema_version": 1, "count": len(items), "items": items}
    SEARCH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    page = INDEX.read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pattern = re.compile(r"const DATA=.*?;\nconst q=", re.S)
    page, n = pattern.subn(lambda _m: "const DATA=" + data + ";\nconst q=", page, count=1)
    if n != 1:
        raise RuntimeError("Could not replace homepage DATA payload")
    INDEX.write_text(page, encoding="utf-8")
    print("Hyperfinite Oracles card position:", items.index(item) + 1)
    print("Read target:", READER_HREF)
    print("PDF target:", DIRECT_PDF)
    print("Featured quote:", QUOTE)


if __name__ == "__main__":
    main()
