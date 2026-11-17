#!/usr/bin/env python3
"""Publish the submitted ATLAS v2 discoverer manuscript as catalog slot 1.

This is a create-only operation: no prior paper, version, or reader is replaced.
Build the PDF from the exact uploaded LaTeX source and audit the published site.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SLUG = "cs.LO_Logic_in_Computer_Science/what_survives_the_successor_discoverer_atlas_v2"
SRC = ROOT / "incoming_publications/what_survives_the_successor_discoverer_atlas_v2/source.tex"
DEST = ROOT / "docs" / SLUG
BUILD = ROOT / ".build/what_survives_the_successor_discoverer_atlas_v2"
CAT = ROOT / "scripts/publications.json"
PDF_NAME = "What_Survives_the_Successor_Discoverer_Revision_REGEN(4)v2(2).pdf"
SOURCE_SHA256 = "4f1c23eb5cd4998a5a242d3067ef6dae5eb1badee4770936369d802a1b6dd90a"
QUOTE = "A proof about a machine is not the same as a modification to its executable."

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(argv):
    subprocess.run(argv, cwd=ROOT, check=True)

def main():
    assert SRC.is_file() and sha256(SRC) == SOURCE_SHA256, "Source checksum mismatch"
    assert not DEST.exists(), "Refusing to overwrite an existing published edition"
    data = json.loads(CAT.read_text(encoding="utf-8"))
    assert not any(x.get("id") == SLUG for x in data["items"]), "Publication ID already exists"
    BUILD.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        with (BUILD / "compile.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                 "-output-directory", str(BUILD), str(SRC)],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT
            )
        if result.returncode:
            print((BUILD / "compile.log").read_text(errors="replace")[-4500:], file=sys.stderr)
            raise RuntimeError("LaTeX compilation failed")
    pdf = BUILD / "source.pdf"
    assert pdf.is_file() and pdf.read_bytes().startswith(b"%PDF-")
    import fitz
    document = fitz.open(pdf)
    assert len(document) == 26, f"Expected 26 pages, found {len(document)}"
    assert "What Survives the Successor?" in document[0].get_text()
    assert QUOTE in document[1].get_text(), "Card quote not found on page 2"
    assert all(page.get_text().strip() for page in document), "Empty or unreadable PDF page"
    text = "\n".join(page.get_text() for page in document)
    assert "Research Director: Brian Tenneson" in text
    assert "AI disclaimer and verification notice" in text
    DEST.mkdir(parents=True)
    shutil.copy2(SRC, DEST / "source.tex")
    shutil.copy2(pdf, DEST / PDF_NAME)
    assert sha256(DEST / "source.tex") == SOURCE_SHA256
    assert sha256(DEST / PDF_NAME) == sha256(pdf)

    numeric = [float(x["order"]) for x in data["items"]
               if isinstance(x.get("order"), (int, float))]
    record = {
        "id": SLUG,
        "href": SLUG + "/",
        "subject": "cs.LO_Logic_in_Computer_Science",
        "title": "What Survives the Successor? The Self-Improving Mathematical Discoverer",
        "kind": "Research paper",
        "authors": "ChatGPT (OpenAI) — Research Director: Brian Tenneson",
        "pdf": SLUG + "/" + PDF_NAME,
        "archive_path": "docs/" + SLUG + "/" + PDF_NAME,
        "source": SLUG + "/source.html",
        "source_file": SLUG + "/source.tex",
        "card_text": (
            "Constructive theory of a mathematical discoverer that generates, checks, "
            "and installs a proof-search rule from its own trace. Establishes a "
            "restricted self-composition ladder, exact charged break-even thresholds, "
            "evidence-qualified successor handoff, adversarial strategy transport, "
            "conditional coordinated basin escape, and fixed-point boundaries."
        ),
        "quote": QUOTE,
        "quote_page": 2,
        "quote_attribution": "What Survives the Successor? · p. 2",
        "quote_also_on_card": True,
        "classification_note": (
            "ATLAS-audited v2 research draft, 16 November 2026. "
            "Research and writing: ChatGPT (OpenAI); Research Director: Brian Tenneson. "
            "The construction is conditional and paper-level, not an operational "
            "demonstration of FORGE-6-E or an independently verified ATP improvement."
        ),
        "publication_date": "16 November 2026",
        "status": (
            "Restricted mathematical existence and abstract full-charge results; "
            "no independent proof-kernel verification, deployment results, or "
            "general self-improving theorem prover is claimed."
        ),
        "pages": 26,
        "sha256": sha256(DEST / PDF_NAME),
        "order": min(numeric, default=0) - 10
    }
    untouched = list(data["items"])
    data["items"] = [record] + untouched
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for site_index in (ROOT / "docs/index.html",
                       ROOT / "docs/cs.LO_Logic_in_Computer_Science/index.html"):
        if site_index.exists():
            site_index.unlink()
    run([sys.executable, "scripts/build_publications_106.py"])
    for site_index in (ROOT / "docs/index.html",
                       ROOT / "docs/cs.LO_Logic_in_Computer_Science/index.html"):
        html = site_index.read_text(encoding="utf-8")
        m = re.search(r'<article class="card"[^>]*><h2><a href="([^"]+)"', html)
        assert m and m.group(1) == "/pub/" + SLUG + "/", "Slot 1 placement failed"
    assert (DEST / "index.html").is_file() and (DEST / "source.html").is_file()
    assert data["items"][1:] == untouched, "Existing catalog order changed"
    print("PUBLISHED:", SLUG, "slot=1", "pdf_sha256=" + record["sha256"])

if __name__ == "__main__":
    main()
