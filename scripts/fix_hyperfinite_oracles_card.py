#!/usr/bin/env python3
"""Keep Hyperfinite Oracles as card #2 and route its PDF through GitHub Pages."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
SEARCH = ROOT / "docs" / "search-index.json"
HREF = "papers/hyperfinite_oracles_data_mind_3_2/"
LOCAL_PDF = HREF + "The_Hyperfinite_Oracles_of_DATA_MIND_3_2.pdf"
QUOTE = "The oracle may direct attention; it may not manufacture certified knowledge."
ATTRIBUTION = "Brian Tenneson and ChatGPT"


def main() -> None:
    payload = json.loads(SEARCH.read_text(encoding="utf-8"))
    items = [dict(x) for x in payload.get("items", [])]
    matches = [x for x in items if str(x.get("href") or "") == HREF]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one Hyperfinite Oracles card, found {len(matches)}")
    item = matches[0]
    items = [x for x in items if x is not item]
    item["pdf"] = LOCAL_PDF
    item["quote"] = QUOTE
    item["quote_attribution"] = ATTRIBUTION
    item["search"] = " ".join([str(item.get("search") or ""), QUOTE, ATTRIBUTION]).strip()
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
    print("PDF route:", LOCAL_PDF)
    print("Featured quote:", QUOTE)


if __name__ == "__main__":
    main()
