#!/usr/bin/env python3
"""Pin Dreamer + Four-Oracle as card #1 while preserving the established featured order."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "docs" / "index.html"
SEARCH = ROOT / "docs" / "search-index.json"

TITLE = "Dreamer and Four-Oracle Extension to DATA MIND 3.2"
SUBTITLE = "A Theoretical Synthesis of Counterfactual Replay, Hyperfinite Epistemic Guidance, and Verifier-Gated Settlement"
READER = "papers/dreamer_four_oracle_data_mind_3_2/"
PDF = READER + "DATA_MIND_3_2_Dreamer_Four_Oracle_Theoretical_Synthesis_2026_09_04.pdf"
SOURCE = READER + "source.html"
ARCHIVE = "cs.LO_Logic_in_Computer_Science/DATA_MIND_3_2_Dreamer_Four_Oracle_Theoretical_Synthesis_2026_09_04.pdf"
QUOTE = "Dream freely, route intelligently, verify exactly."
ATTRIBUTION = "Brian Tenneson"

NSA = "papers/nsa_and_trading_speedup/"
HF = "papers/hyperfinite_oracles_data_mind_3_2/"
DM3 = "papers/data_mind_3_0_module_interface_freeze/"


def matches_dreamer(item: dict) -> bool:
    return (
        str(item.get("title") or "") == TITLE
        or str(item.get("href") or "") in {READER, PDF}
        or str(item.get("archive_path") or "") == ARCHIVE
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

    existing = [x for x in items if matches_dreamer(x)]
    if len(existing) > 1:
        raise RuntimeError(f"Expected at most one Dreamer four-oracle card, found {len(existing)}")
    if existing:
        dreamer = existing[0]
        items.remove(dreamer)
    else:
        dreamer = {}

    dreamer.update({
        "title": TITLE,
        "kind": "Core paper",
        "category": "Research Papers",
        "tags": [],
        "href": READER,
        "pdf": PDF,
        "source": SOURCE,
        "archive_path": ARCHIVE,
        "search": " ".join([TITLE, SUBTITLE, "Research Papers", "DATA MIND 3.2 Dreamer four oracle", ARCHIVE, QUOTE, ATTRIBUTION]),
        "quote": QUOTE,
        "quote_attribution": ATTRIBUTION,
    })

    nsa = detach(items, NSA, "NSA/trading")
    hf = detach(items, HF, "Hyperfinite Oracles")
    dm3 = detach(items, DM3, "DATA MIND 3.0")

    items[0:0] = [dreamer, nsa, hf, dm3]
    payload = {"schema_version": 1, "count": len(items), "items": items}
    SEARCH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sync_home(items)

    print("card 1:", items[0]["title"])
    print("card 1 reader:", items[0]["href"])
    print("card 1 quote:", items[0]["quote"])
    print("card 2:", items[1]["title"])
    print("card 3:", items[2]["title"])
    print("card 4:", items[3]["title"])


if __name__ == "__main__":
    main()
