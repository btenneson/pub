#!/usr/bin/env python3
"""Publish the exact ATLAS-repaired v0.3 LaTeX source, compile it, and promote its card to slot 1.
Keeps existing publication cards in their current relative order. No other manuscript is changed.
"""
from pathlib import Path
import base64
import brotli
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "incoming_publications/formalized_awareness_amld_federations_v0_3"
SLUG = "cs.LO_Logic_in_Computer_Science/formalized_awareness_amld_federations_v0_3"
DEST = ROOT / "docs" / SLUG
SOURCE_NAME = "Formalized_Awareness_of_AMLD_Federations_v0_3_ATLAS_Repaired.tex"
PDF_NAME = "Formalized_Awareness_of_AMLD_Federations_v0_3_ATLAS_Repaired.pdf"
EXPECTED_SOURCE_SHA = "49dadc0ea65b9748abc23282873e8adfbea594df983b4f7378d21e0d730d0c69"
CATALOG = ROOT / "scripts/publications.json"

def validate_source():
    segments = [STAGE / f"manuscript.b64.part{i}" for i in range(6)]
    assert all(p.is_file() for p in segments), "Missing staged source segment"
    joined = "".join(p.read_text(encoding="ascii").strip() for p in segments)
    assert len(joined) == 24012, "Incorrect encoded source size"
    raw = brotli.decompress(base64.b64decode(joined, validate=True))
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SOURCE_SHA, f"Incorrect source digest {digest}"
    assert raw.startswith(b"\\documentclass"), "Unexpected TeX source"
    DEST.mkdir(parents=True, exist_ok=True)
    tex_path = DEST / SOURCE_NAME
    tex_path.write_bytes(raw)
    return tex_path

def compile_pdf(tex_path):
    work = ROOT / ".build/formalized_awareness_amld_v03"
    work.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
            "-output-directory", str(work), str(tex_path)], cwd=tex_path.parent, check=True,
            stdout=subprocess.DEVNULL)
    result = work / PDF_NAME
    assert result.is_file() and result.read_bytes().startswith(b"%PDF-"), "No valid PDF"
    target = DEST / PDF_NAME
    shutil.copyfile(result, target)
    pages = 0
    try:
        meta = subprocess.check_output(["pdfinfo", str(target)], text=True)
        m = re.search(r"(?m)^Pages:\s+(\d+)", meta)
        if m:
            pages = int(m.group(1))
    except FileNotFoundError:
        pass
    assert pages == 15, f"PDF pagination differs from audited edition: {pages}"
    return hashlib.sha256(target.read_bytes()).hexdigest(), pages

def publication_record(digest, pages):
    return {
      "id": SLUG, "href": SLUG + "/",
      "title": "Formalized Awareness of AMLD Federations and Board-Players",
      "kind": "Research paper", "subject": "cs.LO_Logic_in_Computer_Science",
      "authors": "Brian Tenneson (research direction); CAMI (drafting); ATLAS (repairs and re-audit)",
      "pdf": SLUG + "/" + PDF_NAME, "archive_path": "docs/" + SLUG + "/" + PDF_NAME,
      "source": SLUG + "/source.html", "source_file": SLUG + "/" + SOURCE_NAME,
      "card_text": ("Sibling to Formalized Self-Awareness: defines clocked AMLD federation profiles, "
        "verifier-grounded collective reflection, GBG/Player-0 and three B* controllers, "
        "Gestalt reflective surplus, and an explicit recurrently fair clock for countably many agents."),
      "quote": ("The passage from a semi-ideal computer (SIC) to an automated theorem prover (ATP), "
        "and then to an automated metalogical decider (AMLD), is not a lexical substitution."),
      "quote_attribution": "Formalized Awareness of AMLD Federations, v0.3 · Abstract",
      "quote_also_on_card": True,
      "status": ("PRELIMINARY RELEASE · ATLAS-repaired and conditionally re-audited v0.3 · 25 October 2026. "
        "Source-level mathematical pass under stated hypotheses; not formally machine-checked "
        "and not evidence of a live eight-ATP federation."),
      "classification_note": (f"Version 0.3 · 25 October 2026 · {pages} pages · "
        "LaTeX rebuilt from the verified v0.3 source; the manuscript retains its historical prerelease editorial note."),
      "sha256": digest, "pages": pages, "publication_date": "25 October 2026",
      "order": -10028
    }

def insert_first_card(path, record):
    import scripts.build_publications as builder
    html = path.read_text(encoding="utf-8")
    needle = f'/pub/{SLUG}/'
    if needle in html:
        assert html.index(needle) < html.index(
            '/pub/cs.LO_Logic_in_Computer_Science/camis_theorems_and_theories_volume_i/'
        ), "Article exists but is not before prior first card"
        return
    marker = '<div class="grid" id="grid">'
    assert html.count(marker) == 1, "Cannot find publication card grid"
    entry = dict(record)
    entry["category"] = "cs.LO — Logic in Computer Science"
    card = builder.card(entry)
    html = html.replace(marker, marker + card, 1)
    # Keep printed collection count accurate. The UI recalculates filter counts dynamically.
    html = re.sub(r'(<p id="count" role="status">)(\d+)( publications</p>)',
                  lambda m: m.group(1) + str(int(m.group(2)) + 1) + m.group(3),
                  html, count=1)
    path.write_text(html, encoding="utf-8")

def main():
    tex = validate_source()
    digest, pages = compile_pdf(tex)
    rec = publication_record(digest, pages)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    existing = [x for x in catalog["items"] if x["id"] == SLUG]
    if existing:
        assert len(existing) == 1, "Duplicated publication catalog entry"
        assert existing[0]["sha256"] == digest, "Existing published PDF differs"
    else:
        catalog["items"].insert(0, rec)
        CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    visible = [x for x in catalog["items"] if x.get("visibility") not in ("archive","hidden")]
    assert visible[0]["id"] == SLUG, "Publication not in slot 1"
    assert visible[1]["id"] == "cs.LO_Logic_in_Computer_Science/camis_theorems_and_theories_volume_i", "Earlier card order changed"
    insert_first_card(ROOT / "docs/index.html", rec)
    insert_first_card(ROOT / "docs/cs.LO_Logic_in_Computer_Science/index.html", rec)
    subprocess.run([sys.executable, str(ROOT / "scripts/build_publications.py")], cwd=ROOT, check=True)
    reader = DEST / "index.html"
    assert reader.is_file(), "Missing publication reader"
    assert (DEST / "source.html").is_file(), "Missing LaTeX source reader"
    index = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    assert index.index(f"/pub/{SLUG}/") < index.index(
       "/pub/cs.LO_Logic_in_Computer_Science/camis_theorems_and_theories_volume_i/"), "Slot 1 regression"
    assert index.count(f'data-title="{rec["title"]}"') == 1, "Duplicate main-page card"
    print(f"PUBLISHED {SLUG} | pages={pages} | PDF SHA256={digest} | slot=1")

if __name__ == "__main__":
    main()
