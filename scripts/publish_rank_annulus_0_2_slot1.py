#!/usr/bin/env python3
"""Publish DATA MIND's repaired Rank--Annulus paper as a verified slot-1 reader."""
from pathlib import Path
from html import escape
import base64, hashlib, json, shutil, subprocess, zipfile, zlib
import fitz

ROOT = Path(__file__).resolve().parents[1]
slug = "cs.LO_Logic_in_Computer_Science/from_guaranteed_basin_escape_to_certified_cost_optimality"
stem = "DataMind_Rank_Annulus_0_2_Repaired"
title = "From Guaranteed Basin Escape to Certified Cost Optimality"
quote = "Results are always relative to one frozen search model."
blob = ROOT / "incoming_publications/rank_annulus_0_2/source.zlib.b64"
source = zlib.decompress(base64.b64decode(blob.read_text().strip()))
expected = "7b8936731195defb592e1660c98d85b9ea29f09877b1e1004045f3fbb1a667c4"
assert hashlib.sha256(source).hexdigest() == expected, "Original LaTeX does not match supplied ZIP"
out = ROOT / ".build/rank_annulus_0_2"
out.mkdir(parents=True, exist_ok=True)
tex = out / (stem + ".tex")
tex.write_bytes(source)
for _ in range(2):
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                   cwd=out, check=True, stdout=subprocess.DEVNULL)
pdf = out / (stem + ".pdf")
raw = pdf.read_bytes()
doc = fitz.open(stream=raw, filetype="pdf")
assert len(doc) == 7, f"Expected 7 rendered pages; got {len(doc)}"
assert all(page.get_text().strip() for page in doc), "Unreadable PDF page"
assert quote in " ".join(doc[0].get_text().split()), "Card quote not found on cited page"
full = " ".join(p.get_text() for p in doc)
for phrase in (title, "DATA MIND", "Rank", "Annulus", "cost optimality", "Conclusion"):
    assert phrase.lower() in full.lower(), "Rendered PDF missing " + phrase
destination = ROOT / "docs" / slug
archive = ROOT / slug
for folder in (destination, archive):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / (stem + ".pdf")).write_bytes(raw)
    (folder / "source.tex").write_bytes(source)
with zipfile.ZipFile(destination / (stem + "_LaTeX_and_PDF.zip"), "w",
                     compression=zipfile.ZIP_DEFLATED) as pack:
    pack.write(destination / (stem + ".pdf"), stem + ".pdf")
    pack.write(destination / "source.tex", stem + ".tex")
catalog = ROOT / "scripts/publications.json"
data = json.loads(catalog.read_text(encoding="utf-8"))
prior = [x for x in data["items"] if x.get("id") != slug]
old_ids = [x["id"] for x in prior]
first = min([x.get("order", 0) for x in prior if isinstance(x.get("order"), int)] + [0]) - 1
card = {
    "id": slug, "href": slug + "/", "title": title,
    "kind": "Research paper", "subject": "cs.LO_Logic_in_Computer_Science",
    "pdf": slug + "/" + stem + ".pdf",
    "archive_path": slug + "/" + stem + ".pdf",
    "source": slug + "/source.html", "source_file": slug + "/source.tex",
    "source_package": slug + "/" + stem + "_LaTeX_and_PDF.zip",
    "sha256": hashlib.sha256(raw).hexdigest(),
    "sha256_tex": hashlib.sha256(source).hexdigest(),
    "pages": 7, "order": first, "authors": "DATA MIND (AI Research Collaborator)",
    "quote": quote, "quote_page": 1,
    "card_quote": quote, "card_quote_attribution": "DATA MIND, Version 0.2, p. 1",
    "quote_also_on_card": True,
    "card_text": "Standalone conditional theorem linking rank-decreasing guaranteed basin escape to certified minimum fully charged settlement cost. Develops the Rank--Annulus bridge, an exact three-gap decomposition, calibrated-potential optimality, local slack identities, and repaired policy-upper-potential bounds.",
    "status": "REPAIRED AND SIX-LENS ANALYTICALLY AUDITED · 19 OCTOBER 2026. Conditional results; no independent proof-assistant certification or measured speedup.",
    "classification_note": "DATA MIND paper, v0.2 (7 pages). Research context: Brian Tenneson's Foggy Multiarticle Metaworld. FORGE-6 denotes an analytical six-lens audit, not six separately executed theorem provers."
}
data["items"] = [card] + prior
catalog.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
assert [x["id"] for x in data["items"][1:]] == old_ids, "Original card ordering changed"
subprocess.run(["python", "scripts/build_publications_106.py"], cwd=ROOT, check=True)
search = json.loads((ROOT / "docs/search-index.json").read_text())
assert search["items"][0]["id"] == slug, "Publication is not in slot #1"
page = (ROOT / "docs/index.html").read_text(encoding="utf-8")
first_card = page.split('<article class="card"', 1)[1].split("</article>", 1)[0]
assert title in first_card and quote in first_card and "DATA MIND" in first_card
assert (destination / "index.html").is_file()
assert (destination / "source.html").is_file()
assert (destination / "source.tex").read_bytes() == source
assert (destination / (stem + ".pdf")).read_bytes() == raw
assert (destination / (stem + "_LaTeX_and_PDF.zip")).is_file()
print("PASS: DATA MIND paper is slot #1; 7-page PDF and exact provided LaTeX, source, reader, ZIP.")
print("PASS: every existing catalog card retains its relative order.")
