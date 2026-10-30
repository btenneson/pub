#!/usr/bin/env python3
"""Publish the authorized ATLAS-repaired integrated mathematical article at slot #1.

Use the selected LaTeX manuscript unchanged and compile its publication PDF.
Other catalog entries keep their previous relative order.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SLUG = "cs.LO_Logic_in_Computer_Science/epistemic_computational_geometry_mathematical_histories_0_2"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
SOURCE = ROOT / "incoming_publications/epistemic_computational_geometry_0_2/source.tex"
DEST = ROOT / "docs" / SLUG
BUILD = ROOT / ".build/epistemic_computational_geometry_0_2"
CATALOG = ROOT / "scripts/publications.json"
PDF_NAME = "The_Epistemic_and_Computational_Geometry_of_Mathematical_Histories_0_2_ATLAS_Repaired.pdf"
SOURCE_SHA256 = "a899acec575da9ec5cf8ec3b2c6c9d2fa6633292dc6e39619909d74ff7b731f0"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compile_source():
    assert SOURCE.is_file(), "Authorized source is missing"
    assert sha256(SOURCE) == SOURCE_SHA256, "Authorized source has changed"
    text = SOURCE.read_text(encoding="utf-8")
    assert r"\end{document}" in text and "ATLAS-repaired integrated successor" in text
    BUILD.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(BUILD), str(SOURCE)],
            cwd=ROOT, check=True, stdout=subprocess.DEVNULL
        )
    pdf = BUILD / "source.pdf"
    assert pdf.is_file() and pdf.read_bytes().startswith(b"%PDF-")
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    assert re.search(r"(?m)^Pages:\s*23\s*$", info), "Expected 23-page revised edition"
    assert "<Brian Tenneson>" in info, "Exact author credit absent from PDF metadata"
    extracted = subprocess.check_output(["pdftotext", str(pdf), "-"], text=True)
    for phrase in (
        "The Epistemic and Computational Geometry",
        "Certified Quotient Search",
        "A unified hierarchy of obligations",
        "Disclaimer on Mathematical Accuracy",
    ):
        assert phrase.lower() in extracted.lower(), f"Missing expected text: {phrase}"
    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf, DEST / PDF_NAME)
    shutil.copyfile(SOURCE, DEST / "source.tex")
    assert sha256(DEST / "source.tex") == SOURCE_SHA256
    return sha256(DEST / PDF_NAME)

def main():
    pdf_sha = compile_source()
    record = {
        "id": SLUG, "href": SLUG + "/",
        "title": "The Epistemic and Computational Geometry of Mathematical Histories",
        "kind": "Research paper", "subject": SUBJECT,
        "authors": "<Brian Tenneson>",
        "pdf": SLUG + "/" + PDF_NAME,
        "archive_path": "docs/" + SLUG + "/" + PDF_NAME,
        "source": SLUG + "/source.html",
        "source_file": SLUG + "/source.tex",
        "card_text": (
            "From Evidence Conservation to Certified Quotient Search. This integrated successor "
            "to Completion C joins epistemic conservation with the Trading Theorem 003 and "
            "Exact Addressing 4.14. It distinguishes execution histories, operational states, "
            "and verified proofs, derives endpoint audit sufficiency, and proves a conditional "
            "joint audit–settlement quotient theorem preserving future observations and "
            "weighted target-reaching traces. Includes a checked finite exact quotient, "
            "a spurious-path counterexample, and explicit effectiveness and cost limits. "
            "ATLAS-repaired v0.2; 23 pages and 11 black-and-white diagrams."
        ),
        "status": (
            "ATLAS-repaired and internally re-audited version 0.2. Conditional paper-level "
            "mathematics: independent formal proof certification and external peer review "
            "have not been performed."
        ),
        "classification_note": (
            "First published 30 October 2026. Integrated successor to the separately "
            "published Completion C; that earlier work is preserved unchanged. "
            "Source is reproduced verbatim from the ATLAS-repaired manuscript. "
            "The source's 'unpublished' statement records its pre-publication preparation status."
        ),
        "publication_date": "30 October 2026",
        "pages": 23,
        "sha256": pdf_sha
    }
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    matches = [x for x in data["items"] if x["id"] == SLUG]
    assert len(matches) <= 1, "Duplicate publication identifiers"
    existing = [x for x in data["items"] if x["id"] != SLUG]
    min_order = min((x["order"] for x in existing if isinstance(x.get("order"), (int,float))), default=0)
    record["order"] = min_order - 10
    data["items"] = [record] + existing
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for page in (ROOT / "docs/index.html", ROOT / "docs" / SUBJECT / "index.html"):
        if page.exists():
            page.unlink()
    subprocess.run([sys.executable, "scripts/build_publications_106.py"], cwd=ROOT, check=True)

    for landing in (ROOT / "docs/index.html", ROOT / "docs" / SUBJECT / "index.html"):
        body = landing.read_text(encoding="utf-8")
        cards = re.findall(r'<article class="card"[^>]*><h2><a href="([^"]+)"', body)
        assert cards and cards[0] == "/pub/" + SLUG + "/", f"New item not first in {landing}"
    assert (DEST / "index.html").is_file(), "Reader page missing"
    assert (DEST / "source.html").is_file(), "LaTeX source page missing"
    assert (DEST / PDF_NAME).is_file(), "PDF missing"
    assert (DEST / "source.tex").is_file(), "Source missing"
    assert data["items"][1:] == existing, "Old library order was changed"
    print("PUBLISHED slot 1:", SLUG, "PDF sha256:", pdf_sha)

if __name__ == "__main__":
    main()
