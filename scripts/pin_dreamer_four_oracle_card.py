#!/usr/bin/env python3
"""Pin the Invariant Core synthesis as card #1 while preserving featured order."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "docs" / "index.html"
SEARCH = ROOT / "docs" / "search-index.json"

INVARIANT_TITLE = "The Invariant Core and the Geometry of Settlement"
INVARIANT_SUBTITLE = (
    "Trading, Induction, Formal Self-Awareness, Hyperfinite Epistemic Horizons, "
    "and Counterfactual Dreaming in DATA MIND"
)
INVARIANT_READER = "papers/invariant_core_geometry_settlement/"
INVARIANT_PDF = INVARIANT_READER + "The_Invariant_Core_and_the_Geometry_of_Settlement.pdf"
INVARIANT_ARCHIVE = "cs.LO_Logic_in_Computer_Science/The_Invariant_Core_and_the_Geometry_of_Settlement.pdf"
INVARIANT_SOURCE = (
    "https://github.com/btenneson/pub/blob/main/"
    "documents%20and%20their%20sources/The_Invariant_Core_and_the_Geometry_of_Settlement.tex"
)
INVARIANT_QUOTE = (
    "The deepest potential contribution of this combined framework is therefore not a claim that any one mechanism "
    "makes theorem proving faster. It is a framework in which such speedups can be located, decomposed, certified "
    "where possible, and experimentally attributed."
)
ATTRIBUTION = "Brian Tenneson"

DREAMER = "papers/dreamer_four_oracle_data_mind_3_2/"
NSA = "papers/nsa_and_trading_speedup/"
HF = "papers/hyperfinite_oracles_data_mind_3_2/"
DM3 = "papers/data_mind_3_0_module_interface_freeze/"


def matches_invariant(item: dict) -> bool:
    return (
        str(item.get("title") or "") == INVARIANT_TITLE
        or str(item.get("href") or "") in {INVARIANT_READER, INVARIANT_PDF}
        or str(item.get("archive_path") or "") == INVARIANT_ARCHIVE
    )


def detach(items: list[dict], href: str, label: str) -> dict:
    found = [x for x in items if str(x.get("href") or "") == href]
    if len(found) != 1:
        raise RuntimeError(f"Expected exactly one {label} card, found {len(found)}")
    item = found[0]
    items.remove(item)
    return item


def sync_home(items: list[dict]) -> None:
    page = HOME.read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page, n = re.subn(
        r"const DATA=.*?;\nconst q=",
        lambda _m: "const DATA=" + data + ";\nconst q=",
        page,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError("Could not replace homepage DATA payload")
    HOME.write_text(page, encoding="utf-8")


def main() -> None:
    payload = json.loads(SEARCH.read_text(encoding="utf-8"))
    items = [dict(x) for x in payload.get("items", [])]

    existing = [x for x in items if matches_invariant(x)]
    if len(existing) > 1:
        raise RuntimeError(f"Expected at most one invariant-core card, found {len(existing)}")
    if existing:
        invariant = existing[0]
        items.remove(invariant)
    else:
        invariant = {}

    invariant.update({
        "title": INVARIANT_TITLE,
        "kind": "Core paper",
        "category": "Research Papers",
        "tags": [],
        "href": INVARIANT_READER,
        "pdf": INVARIANT_PDF,
        "source": INVARIANT_SOURCE,
        "archive_path": INVARIANT_ARCHIVE,
        "search": " ".join([
            INVARIANT_TITLE,
            INVARIANT_SUBTITLE,
            "Research Papers DATA MIND invariant core geometry settlement",
            INVARIANT_ARCHIVE,
            INVARIANT_QUOTE,
            ATTRIBUTION,
        ]),
        "quote": INVARIANT_QUOTE,
        "quote_attribution": ATTRIBUTION,
    })

    dreamer = detach(items, DREAMER, "Dreamer four-oracle")
    nsa = detach(items, NSA, "NSA/trading")
    hf = detach(items, HF, "Hyperfinite Oracles")
    dm3 = detach(items, DM3, "DATA MIND 3.0")

    items[0:0] = [invariant, dreamer, nsa, hf, dm3]
    payload = {"schema_version": 1, "count": len(items), "items": items}
    SEARCH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sync_home(items)

    for i, item in enumerate(items[:5], 1):
        print(f"card {i}:", item["title"])
    print("card 1 reader:", invariant["href"])
    print("card 1 quote:", invariant["quote"])


if __name__ == "__main__":
    main()
