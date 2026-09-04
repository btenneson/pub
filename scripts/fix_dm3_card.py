#!/usr/bin/env python3
"""Keep the hyperfinite-oracles paper as card #2 and DATA MIND 3.0 as card #3."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
SEARCH = ROOT / "docs" / "search-index.json"

HYPERFINITE_HREF = "papers/hyperfinite_oracles_data_mind_3_2/"
HYPERFINITE_QUOTE = "The oracle may direct attention; it may not manufacture certified knowledge."
HYPERFINITE_ATTRIBUTION = "Brian Tenneson and ChatGPT"

DM3_HREF = "papers/data_mind_3_0_module_interface_freeze/"
DM3_QUOTE = "BANK = vertical reuse; Trading = horizontal movement."
DM3_ATTRIBUTION = "Brian Tenneson and ChatGPT"


def detach_one(items: list[dict], href: str, label: str) -> dict:
    matches = [x for x in items if str(x.get("href") or "") == href]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {label} card, found {len(matches)}")
    item = matches[0]
    items.remove(item)
    return item


def feature(item: dict, quote: str, attribution: str) -> None:
    item["quote"] = quote
    item["quote_attribution"] = attribution
    item["search"] = " ".join(
        [str(item.get("search") or ""), quote, attribution]
    ).strip()


def main() -> None:
    payload = json.loads(SEARCH.read_text(encoding="utf-8"))
    items = [dict(x) for x in payload.get("items", [])]

    hyperfinite = detach_one(items, HYPERFINITE_HREF, "hyperfinite-oracles")
    dm3 = detach_one(items, DM3_HREF, "DATA MIND 3.0")

    feature(hyperfinite, HYPERFINITE_QUOTE, HYPERFINITE_ATTRIBUTION)
    feature(dm3, DM3_QUOTE, DM3_ATTRIBUTION)

    # Card #1 remains the NSA/trading lead maintained by build_library_homepage_v5.py.
    items.insert(min(1, len(items)), hyperfinite)
    items.insert(min(2, len(items)), dm3)

    payload = {"schema_version": 1, "count": len(items), "items": items}
    SEARCH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    page = INDEX.read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pattern = re.compile(r"const DATA=.*?;\nconst q=", re.S)
    page, n = pattern.subn(lambda _m: "const DATA=" + data + ";\nconst q=", page, count=1)
    if n != 1:
        raise RuntimeError("Could not replace homepage DATA payload")
    INDEX.write_text(page, encoding="utf-8")

    print("Hyperfinite Oracles card position:", items.index(hyperfinite) + 1)
    print("Hyperfinite Oracles quote:", HYPERFINITE_QUOTE)
    print("DATA MIND 3.0 card position:", items.index(dm3) + 1)
    print("DATA MIND 3.0 quote:", DM3_QUOTE)


if __name__ == "__main__":
    main()
