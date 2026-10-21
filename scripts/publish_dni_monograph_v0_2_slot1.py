#!/usr/bin/env python3
"""Publish the audited DNI monograph v0.2 at library slot #1.

The monograph PDF bytes are supplied as a pre-existing, fixed publication input.
This script does not revise or recompile the mathematical work.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import fitz

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = "cs.LO_Logic_in_Computer_Science"
NAME = "determinism_possibility_and_certified_search_research_monograph_0_2"
SLUG = f"{SUBJECT}/{NAME}"
PDF = "Determinism_Possibility_and_Certified_Search_Research_Monograph_0_2_ATLAS_Repaired.pdf"
ARCHIVE = ROOT / SLUG / PDF
PUBLIC = ROOT / "docs" / SLUG / PDF
CATALOG = ROOT / "scripts" / "publications.json"
EXPECTED_SHA256 = "e7fec3971932056b97c50fdc0728b8880a2056e1218a2f9eee1f74750544b041"
TITLE = "Determinism, Possibility, and Certified Search: A Research Monograph on Exact Interfaces, Finite Resources, and Proof-Carrying Control"
QUOTE = "These size results refer to freely chosen mathematical implementations, not to a predetermined physical substrate."
assert ARCHIVE.is_file(), "Missing immutable monograph PDF in repository archive"
assert PUBLIC.is_file(), "Missing monograph PDF in GitHub Pages folder"
assert ARCHIVE.read_bytes() == PUBLIC.read_bytes(), "Archive and Pages PDF mismatch"
assert hashlib.sha256(PUBLIC.read_bytes()).hexdigest() == EXPECTED_SHA256, "PDF hash mismatch"
with fitz.open(PUBLIC) as doc:
    assert len(doc) == 46, ("Wrong page count", len(doc))
    assert all(p.get_text().strip() for p in doc), "A PDF page is blank"
    # The quotation is printed in the abstract (PDF page 2).
    assert QUOTE in " ".join(doc[1].get_text().split()), "Card quotation absent from monograph"

data = json.loads(CATALOG.read_text(encoding="utf-8"))
old = [x for x in data["items"] if x.get("id") != SLUG]
old_ids = [x["id"] for x in old]
position = min([x["order"] for x in old if isinstance(x.get("order"), int)] + [0]) - 1
card = {
    "id": SLUG, "href": SLUG + "/",
    "title": TITLE, "kind": "Research monograph", "subject": SUBJECT,
    "pdf": SLUG + "/" + PDF, "archive_path": SLUG + "/" + PDF,
    "sha256": EXPECTED_SHA256, "pages": 46, "order": position,
    "authors": "DATA MIND",
    "quote": QUOTE, "quote_page": 2,
    "card_quote": QUOTE, "quote_also_on_card": True,
    "card_quote_attribution": "DATA MIND, repaired research monograph 0.2, abstract, p. 2",
    "card_text": "A consolidated 46-page graduate-level research monograph for a skeptical physicist. It develops exact deterministic-possibilistic-stochastic interfaces; finite realization obstructions and optimal finite-horizon bounds; theorem search, generalized board games and authorized Player-0 control; and provenance-preserving proof transport. Brian Tenneson is curator and research interlocutor, not an author.",
    "status": "ATLAS-REPAIRED RESEARCH MONOGRAPH, VERSION 0.2 (20 OCTOBER 2026). Internal mathematical audit; not independent proof-assistant certification. Physical determinism and universal efficient proof search are not established.",
    "classification_note": "AI-authored by DATA MIND. Brian Tenneson is curator and interlocutor, not a coauthor. Incorporates existing work with appropriate citation and retains physical-scope limitations.",
}
data["items"] = [card] + old
assert [x["id"] for x in data["items"][1:]] == old_ids
CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
subprocess.run([sys.executable, "scripts/build_publications_106.py"], cwd=ROOT, check=True)
# The published index and subject reader are built from the canonical catalog.
root_index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
assert root_index.find('data-title="' + TITLE.replace("&", "&amp;")) >= 0
first = root_index.split('<article class="card"', 1)[1].split('</article>', 1)[0]
assert NAME in first and "DATA MIND" in first, "Not in slot 1"
reader = (ROOT / "docs" / SLUG / "index.html")
assert reader.is_file(), "Reader page not built"
assert [x["id"] for x in json.loads(CATALOG.read_text())["items"][1:]] == old_ids
print("PASS: The original audited PDF is published byte-for-byte.")
print("PASS: DATA MIND author, Brian Tenneson curator/interlocutor.")
print("PASS: new card at slot #1 without reordering any existing cards.")
