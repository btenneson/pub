#!/usr/bin/env python3
"""Publish the immutable DATA MIND Volume I PDF to slot 1 after PDF upload."""
from pathlib import Path
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF_NAME = "DATA_MIND_Volume_I_Quicksand_Published_Preprint.pdf"
PDF_SRC = ROOT / PDF_NAME
REL = "cs.LO_Logic_in_Computer_Science/data_mind_frontiers_of_discovery_volume_i_quicksand"
PDF_DEST = ROOT / "docs" / REL / PDF_NAME
CATALOG = ROOT / "scripts/publications.json"
EXPECTED_SHA256 = "83775de2b660bdbc38f96925b4a0750450123cd9b4c1df10861495eeabcd51a4"

assert PDF_SRC.is_file(), "Upload the preprint PDF at the repository root first"
raw = PDF_SRC.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
assert digest == EXPECTED_SHA256, "PDF differs from the approved, immutable preprint"
with fitz.open(stream=raw, filetype="pdf") as doc:
    assert len(doc) == 15, "Expected 15-page published preprint"
    assert all(page.get_text().strip() for page in doc), "PDF has unreadable/empty pages"
    first_page = " ".join(doc[0].get_text().split())
    assert "When an AI Found the Mathematical Bridge but Not the Formal Certificate" in first_page
    assert "UNSETTLED" in " ".join(page.get_text() for page in doc), "Preserve the formal-unsettled finding"

PDF_DEST.parent.mkdir(parents=True, exist_ok=True)
PDF_DEST.write_bytes(raw)
data = json.loads(CATALOG.read_text(encoding="utf-8"))
existing = [x for x in data["items"] if x.get("id") != REL]
numeric_orders = [x["order"] for x in existing if isinstance(x.get("order"), int)]
item = {
    "title": "DATA MIND's Frontiers of Discovery — Volume I: The Quicksand Problem",
    "kind": "Research preprint",
    "subject": "cs.LO_Logic_in_Computer_Science",
    "id": REL,
    "href": REL + "/",
    "pdf": REL + "/" + PDF_NAME,
    "sha256": digest,
    "pages": 15,
    "order": min(numeric_orders + [0]) - 1,
    "authors": "Brian Tenneson; AI-assisted DATA MIND / AMLD-inspired analysis",
    "quote": "When an AI Found the Mathematical Bridge but Not the Formal Certificate",
    "quote_page": 1,
    "card_quote": "A mathematical bridge can be discovered before a proof is certified. The distinction is the discovery.",
    "card_quote_attribution": "Editorial card quotation · October 2026",
    "quote_also_on_card": True,
    "card_text": "A student receives 36 of 48 displayed Metamath proof rows, leaving the final quarter hidden. This illustrated case study follows an AMLD-inspired search that identified a candidate inequality bridge while formal Metamath verification remained incomplete. Illustrations are conceptual, not proof certificates. The exact experimental record and UNSETTLED conclusion are preserved.",
    "status": "PUBLISHED RESEARCH PREPRINT — Formal Metamath certificate not yet produced; settlement remains UNSETTLED (October 16, 2026).",
    "classification_note": "15-page technically illustrated working preprint. Describes an AMLD-inspired prompt-driven continuation, not an executed instance of the separate original AMLD+0 program. Mathematical bridge conditional; independent checker acceptance absent.",
}
data["items"] = [item] + existing
CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Registered immutable Volume I PDF in slot 1:", digest)
