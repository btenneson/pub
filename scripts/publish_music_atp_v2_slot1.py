#!/usr/bin/env python3
"""Publish the reviewed MUSIC of an ATP v2 article in library slot 1.

Recompile the supplied audited LaTeX, verify the resulting 13-page PDF, and
insert a single new catalog entry without deleting or reordering old cards.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "incoming_publications" / "music_of_an_atp_v2"
BUILD = ROOT / ".build" / "music_of_an_atp_v2"
DOCS = ROOT / "docs"
CATALOG = ROOT / "scripts" / "publications.json"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
SLUG = "music_of_an_atp_expository_research_article_2_0"
IDENT = f"{SUBJECT}/{SLUG}"
TITLE = "MUSIC of an Automated Theorem Prover"
PDF_NAME = "MUSIC_of_an_ATP_Expository_Research_Article 2.0.pdf"

def main():
    source = STAGE / "source.tex"
    if not source.is_file():
        raise SystemExit("Missing reviewed source.tex")
    src = source.read_text(encoding="utf-8")
    assert "Research article, version 2.0" in src
    assert "AI Authorship and Mathematical Reliability Disclaimer" in src
    BUILD.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        proc = subprocess.run(
            ["pdflatex", "-halt-on-error", "-interaction=nonstopmode",
             "-output-directory", str(BUILD), str(source)],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True)
        if proc.returncode:
            print(proc.stdout[-7000:])
            raise SystemExit(f"PDF compile failed on pass {attempt+1}")
    generated = BUILD / "source.pdf"
    if not generated.is_file() or generated.stat().st_size < 50000:
        raise SystemExit("Generated PDF missing or implausibly small")

    import fitz
    with fitz.open(generated) as pdf:
        if len(pdf) != 13:
            raise SystemExit(f"Expected 13 pages; got {len(pdf)} (different layout)")
        first = pdf[0].get_text()
        final = pdf[-1].get_text()
        whole = "\n".join(page.get_text() for page in pdf)
        for word in ("MUSIC of an Automated Theorem Prover",
                     "Possible Dream Families",
                     "Realizability-complex",
                     "Verifier-gated conservativity"):
            if word.casefold() not in whole.casefold():
                raise SystemExit(f"Required manuscript text not found: {word}")
        if "AI-authorship and reliability notice" not in first:
            raise SystemExit("Missing front-page disclaimer pointer")
        if "AI Authorship and Mathematical Reliability Disclaimer" not in final:
            raise SystemExit("Missing final-page disclaimer")
        if "End of manuscript" not in final:
            raise SystemExit("Unexpected last page")
        if not all(page.get_text().strip() for page in pdf):
            raise SystemExit("Empty or unreadable PDF page detected")

    target = DOCS / IDENT
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(generated, target / PDF_NAME)
    shutil.copyfile(source, target / "source.tex")
    digest = hashlib.sha256((target / PDF_NAME).read_bytes()).hexdigest()
    meta = json.loads(CATALOG.read_text(encoding="utf-8"))
    existing = meta["items"]
    original = [x for x in existing if x["id"] != IDENT]
    if len(original) != len({x["id"] for x in original}):
        raise SystemExit("Existing catalog contains duplicate identifiers")
    previous_first = original[0]["id"]
    new_entry = {
        "id": IDENT,
        "href": IDENT + "/",
        "subject": SUBJECT,
        "title": TITLE,
        "kind": "Research paper",
        "authors": "<Brian Tenneson>",
        "pdf": IDENT + "/" + PDF_NAME,
        "archive_path": "docs/" + IDENT + "/" + PDF_NAME,
        "source": IDENT + "/source.html",
        "source_file": IDENT + "/source.tex",
        "card_text": (
            "Research exposition defining MUSIC as the powerset of an ATP's possible "
            "report-union dreams under a frozen BANK, player roster and initial state. "
            "Develops recovery and factorization results, a joint-realizability complex, "
            "finite and infinite compatibility counterexamples, and verifier-gated "
            "conservativity. Version 2.0 includes an iterative mathematical and layout audit."
        ),
        "classification_note": (
            "Version 2.0, 3 November 2026. Human-directed, AI-assisted mathematical "
            "exposition. The results are conditional on explicitly stated assumptions, "
            "and the paper does not claim machine-checked proofs, verified AMLD+0 "
            "deployment or demonstrated proof-search speedups. The full AI "
            "authorship and reliability disclaimer appears on the last page."
        ),
        "publication_date": "3 November 2026",
        "status": (
            "ATLAS editorial audit and iterative repairs completed. "
            "No independent formal proof-assistant verification is claimed."
        ),
        "pages": 13,
        "sha256": digest,
        "order": min(int(x.get("order", 100)) for x in original) - 1,
    }
    meta["items"] = [new_entry] + original
    CATALOG.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    for page in (DOCS / "index.html", DOCS / SUBJECT / "index.html"):
        if page.exists():
            page.unlink()
    subprocess.run([sys.executable, "scripts/build_publications_106.py"],
                   cwd=ROOT, check=True)

    # Ensure slot 1 and preservation of the entire prior ordered catalog.
    post = json.loads(CATALOG.read_text(encoding="utf-8"))["items"]
    assert post[0]["id"] == IDENT
    assert [x["id"] for x in post[1:]] == [x["id"] for x in original]
    assert post[1]["id"] == previous_first
    assert len(post) == len(original) + 1
    for page in (DOCS / "index.html", DOCS / SUBJECT / "index.html"):
        html = page.read_text(encoding="utf-8")
        names = re.findall(
            r'<article class="card"[^>]*><h2><a href="([^"]+)"', html)
        assert names[0] == "/pub/" + IDENT + "/", names[:3]
        assert names[1] == "/pub/" + previous_first + "/", names[:3]
    assert (target / "index.html").is_file()
    assert (target / "source.html").is_file()
    assert (target / PDF_NAME).stat().st_size > 50000
    print("PASS: MUSIC v2 published in library slot 1; previous entries preserved.")
    print(f"PDF SHA256: {digest}")
    print(f"Live path: https://btenneson.github.io/pub/{IDENT}/")

if __name__ == "__main__":
    main()
