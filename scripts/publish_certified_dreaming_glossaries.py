#!/usr/bin/env python3
"""Publish the four standalone certified-dreaming glossary editions in slots 1–4.

This script runs only in the repository publication workflow. It preserves all
existing catalog items, metadata, historical files and previous relative order.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
import re

import fitz

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CATALOG = ROOT / "scripts" / "publications.json"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
PAPERS = [
    {
        "level": "W0",
        "slug": "cooperative_gbg_plus_dreaming_w0_glossaries",
        "filename": "W0_Cooperative_GBG_Plus_Dreaming_Glossaries.pdf",
        "title": "Cooperative GBG+ Dreaming in a Singleton ATP",
        "quote": "Game play is operationally equivalent to dreaming",
        "card_text": "W0. An audited proposal for cooperative dreaming within one ATP: fourteen specialist players, Player 0 coordination, actor-attributed victories, typed surplus, and verified waking. This edition adds an argot and notation glossary with first-found references.",
    },
    {
        "level": "W1",
        "slug": "algebra_of_certified_dream_surplus_w1_glossaries",
        "filename": "W1_Algebra_of_Certified_Dream_Surplus_Glossaries.pdf",
        "title": "The Algebra of Certified Dream Surplus",
        "quote": "A singleton automated theorem prover can conduct a cooperative generalized-board game",
        "card_text": "W1. Level-1 FDWC research on fair cooperative games, typed evidence dependencies, certified learning, and traitwise waking. Includes separate argot and notation glossaries with first-found references.",
    },
    {
        "level": "W2",
        "slug": "certified_wake_sufficiency_w2_glossaries",
        "filename": "W2_Certified_Wake_Sufficiency_Glossaries.pdf",
        "title": "Certified Wake Sufficiency and Evidence Frontiers",
        "quote": "Choosing among witnesses becomes part of the mathematical problem.",
        "card_text": "W2. Level-2 FDWC research on alternative proof witnesses, minimum-cost retained evidence, compulsory memory, and answer-preserving frontiers. This edition includes argot and notation glossaries with first-found references.",
    },
    {
        "level": "W3",
        "slug": "certified_failure_geometry_w3_glossaries",
        "filename": "W3_Certified_Failure_Geometry_Glossaries.pdf",
        "title": "Certified Failure Geometry",
        "quote": "This article changes the question.",
        "card_text": "W3. Level-3 FDWC research on evidence-cut duality, destructive revocations, robust waking, and rare-fault reliability. This edition adds accessible argot and notation glossaries with first-found references.",
    },
]

def normalized(s):
    return " ".join(s.split())

def compile_paper(p):
    folder = DOCS / SUBJECT / p["slug"]
    src = folder / "source.tex"
    if not src.is_file():
        raise FileNotFoundError(src)
    build = folder / "_latex_build"
    build.mkdir(parents=True, exist_ok=True)
    try:
        command = [
            "latexmk", "-pdf", "-interaction=nonstopmode",
            "-halt-on-error", "-file-line-error", "-outdir=" + str(build),
            src.name,
        ]
        subprocess.run(command, cwd=folder, check=True)
        pdf_out = build / "source.pdf"
        if not pdf_out.is_file():
            raise FileNotFoundError(pdf_out)
        shutil.copyfile(pdf_out, folder / p["filename"])
    finally:
        shutil.rmtree(build, ignore_errors=True)

    pdf_path = folder / p["filename"]
    doc = fitz.open(pdf_path)
    if len(doc) < 5 or not all(page.get_text().strip() for page in doc):
        raise RuntimeError(f"{p['level']} contains empty PDF pages")
    last = doc[-1].get_text()
    if "AI Disclaimer" not in last or "Authorship" not in last:
        raise RuntimeError(f"{p['level']} AI disclaimer not found on FINAL PAGE")
    if "Glossar" not in " ".join(doc[min(2, len(doc)-1)].get_text() for _ in [0]):
        # The glossaries may begin on page 2, 3 or 4; check globally.
        if not any("Glossar" in pg.get_text() for pg in doc):
            raise RuntimeError(f"{p['level']} glossary not found")
    q = normalized(p["quote"])
    quote_pages = [i + 1 for i in range(len(doc)) if q in normalized(doc[i].get_text())]
    if not quote_pages:
        raise RuntimeError(f"{p['level']} selected quote absent from rendered PDF: {q}")
    pages = len(doc)
    doc.close()
    with zipfile.ZipFile(folder / (p["level"] + "_Source_and_PDF.zip"), "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(src, arcname=p["level"] + "_Glossaries.tex")
        z.write(pdf_path, arcname=p["filename"])
    return pdf_path, pages, quote_pages[0]

def main():
    created = []
    for p in PAPERS:
        pdf_path, pages, quote_page = compile_paper(p)
        relbase = f"{SUBJECT}/{p['slug']}"
        item = {
            "id": relbase,
            "href": relbase + "/",
            "subject": SUBJECT,
            "title": p["title"],
            "kind": "Research paper",
            "authors": "<Brian Tenneson>",
            "pdf": f"{relbase}/{p['filename']}",
            "archive_path": f"docs/{relbase}/{p['filename']}",
            "source": f"{relbase}/source.html",
            "source_file": f"{relbase}/source.tex",
            "source_package": f"{relbase}/{p['level']}_Source_and_PDF.zip",
            "quote": p["quote"],
            "quote_page": quote_page,
            "quote_attribution": f"{p['title']} — glossary edition, p. {quote_page}",
            "quote_also_on_card": True,
            "card_text": p["card_text"],
            "classification_note": (
                f"{p['level']} of four independent W0–W3 research manuscripts. "
                "31 October 2026. Glossary edition; the complete AI authorship disclaimer remains "
                "on the final PDF page. Formal results are conditional; no independent "
                "machine-checking, deployed ATP performance verification, or global originality "
                "priority is claimed."
            ),
            "publication_date": "31 October 2026",
            "status": "Research preprint with explicit AI-assisted authorship, formal assumptions and verification limits.",
            "pages": pages,
            "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        }
        created.append(item)
        print(f"Validated {p['level']}: {pages} pages, quote p.{quote_page}, disclaimer on final page", flush=True)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    new_ids = {x["id"] for x in created}
    old = [x for x in catalog["items"] if x["id"] not in new_ids]
    if len({x["id"] for x in old}) != len(old):
        raise RuntimeError("Existing catalog contains duplicate IDs; refusing to reorder")
    # Existing slots are the current list order; preserve their relative order.
    # Repair one pre-existing catalog metadata omission required by the
    # repository-wide quote audit. Preserve its PDF, reader and card identity.
    legacy_id = "cs.LO_Logic_in_Computer_Science/epistemic_computational_geometry_mathematical_histories_0_2"
    legacy_quote = "A proof-seeking machine has at least three different mathematical identities"
    for x in old:
        if x["id"] == legacy_id and not x.get("quote"):
            legacy_pdf = fitz.open(DOCS / x["pdf"])
            try:
                if normalized(legacy_quote) not in normalized(legacy_pdf[0].get_text()):
                    raise RuntimeError("Existing legacy quote missing on page 1")
            finally:
                legacy_pdf.close()
            x["quote"] = legacy_quote
            x["quote_page"] = 1
            x["quote_attribution"] = x["title"] + " — p. 1"
            x["quote_also_on_card"] = True
            print("Repaired pre-existing missing quote metadata on original slot 8.", flush=True)
    for i, x in enumerate(created + old, 1):
        x["order"] = i
    catalog["items"] = created + old
    if [x["order"] for x in catalog["items"]] != list(range(1, len(catalog["items"]) + 1)):
        raise RuntimeError("Publication ordering has gaps")
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # The builder intentionally preserves preexisting curated index pages. Remove
    # only top-level catalog indexes so they are regenerated with the new order.
    (DOCS / "index.html").unlink(missing_ok=True)
    (DOCS / "archive" / "index.html").unlink(missing_ok=True)
    for subject_dir in DOCS.iterdir():
        if subject_dir.is_dir() and subject_dir.name.startswith(("cs.", "math.", "q-bio.", "stat.")):
            (subject_dir / "index.html").unlink(missing_ok=True)

    subprocess.run([sys.executable, "scripts/build_publications_106.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/audit_subject_catalog_106.py"], cwd=ROOT, check=True)
    print(f"SUCCESS: {len(created)} new items, {len(old)} preserved items, "
          f"{len(catalog['items'])} contiguous slots, W0–W3 at 1–4", flush=True)

if __name__ == "__main__":
    main()
