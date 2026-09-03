#!/usr/bin/env python3
"""Keep the DATA MIND 3.0 architecture freeze as card #3 with a featured quote."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
SEARCH = ROOT / "docs" / "search-index.json"
HREF = "papers/data_mind_3_0_module_interface_freeze/"
QUOTE = "BANK = vertical reuse; Trading = horizontal movement."
ATTRIBUTION = "Brian Tenneson and ChatGPT"


def main() -> None:
    payload = json.loads(SEARCH.read_text(encoding="utf-8"))
    items = [dict(x) for x in payload.get("items", [])]
    matches = [x for x in items if str(x.get("href") or "") == HREF]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one DATA MIND 3.0 card, found {len(matches)}")
    item = matches[0]
    items = [x for x in items if x is not item]
    item["quote"] = QUOTE
    item["quote_attribution"] = ATTRIBUTION
    item["search"] = " ".join([str(item.get("search") or ""), QUOTE, ATTRIBUTION]).strip()
    items.insert(min(2, len(items)), item)

    payload = {"schema_version": 1, "count": len(items), "items": items}
    SEARCH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    page = INDEX.read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pattern = re.compile(r"const DATA=.*?;\nconst q=", re.S)
    page, n = pattern.subn(lambda _m: "const DATA=" + data + ";\nconst q=", page, count=1)
    if n != 1:
        raise RuntimeError("Could not replace homepage DATA payload")
    INDEX.write_text(page, encoding="utf-8")
    print("DATA MIND 3.0 card position:", items.index(item) + 1)
    print("Featured quote:", QUOTE)


if __name__ == "__main__":
    main()
