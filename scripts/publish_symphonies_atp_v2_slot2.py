#!/usr/bin/env python3
"""Publish the reviewed Symphonies v2 paper in publication slot 2, preserving MUSIC in slot 1.

Requires the exact audited LaTeX source staged in incoming_publications. Builds
and validates the PDF before modifying the publication catalog or reader pages.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "incoming_publications" / "symphonies_of_atps_v2"
BUILD = ROOT / ".build" / "symphonies_of_atps_v2"
DOCS = ROOT / "docs"
CATALOG = ROOT / "scripts" / "publications.json"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
SLUG = "symphonies_of_automated_theorem_provers_2_0"
IDENT = f"{SUBJECT}/{SLUG}"
MUSIC_ID = f"{SUBJECT}/music_of_an_atp_expository_research_article_2_0"
TITLE = "Symphonies of Automated Theorem Provers"
PDF_NAME = "Symphonies_of_Automated_Theorem_Provers 2.0.pdf"
SOURCE_SHA256 = "3300ef3bebd3ceb31f6d5ccddd23051ca466e0283ce5220f54cec4a96b9e27c7"

def main():
    source = STAGE / "source.tex"
    if not source.is_file():
        raise SystemExit("Missing Atlas-audited source.tex")
    src_bytes = source.read_bytes()
    if hashlib.sha256(src_bytes).hexdigest() != SOURCE_SHA256:
        raise SystemExit("Source differs from the audited version 2.0 LaTeX")
    src = src_bytes.decode("utf-8")
    for expected in ("Symphonies of Automated Theorem Provers",
                     "Research article, version 2.0",
                     "AI Authorship and Mathematical Reliability Disclaimer"):
        if expected not in src:
            raise SystemExit(f"Missing required source text: {expected}")

    # Fail before making any catalog change when publication is no longer MUSIC-first.
    before = json.loads(CATALOG.read_text(encoding="utf-8"))
    original = [x for x in before["items"] if x["id"] != IDENT]
    if len(original) < 2 or original[0]["id"] != MUSIC_ID:
        raise SystemExit("Refusing to alter catalog: MUSIC is not in slot 1")
    if len(original) != len({x["id"] for x in original}):
        raise SystemExit("Existing publication IDs are not unique")
    previous_second = original[1]["id"]
    old_ids = [x["id"] for x in original]

    BUILD.mkdir(parents=True, exist_ok=True)
    for pass_number in range(1, 4):
        proc = subprocess.run(
            ["pdflatex", "-halt-on-error", "-interaction=nonstopmode",
             "-output-directory", str(BUILD), str(source)],
            cwd=ROOT, capture_output=True, text=True)
        if proc.returncode:
            print((proc.stdout + proc.stderr)[-8500:])
            raise SystemExit(f"PDF compilation failed on pass {pass_number}")
    generated = BUILD / "source.pdf"
    if not generated.is_file() or generated.stat().st_size < 100_000:
        raise SystemExit("Missing or implausibly small compiled PDF")

    import fitz
    with fitz.open(generated) as pdf:
        if len(pdf) != 16:
            raise SystemExit(f"Expected audited 16-page article, got {len(pdf)} pages")
        texts = [page.get_text() for page in pdf]
        first, final = texts[0], texts[-1]
        all_text = "\n".join(texts).casefold()
        for required in (
            "symphonies of automated theorem provers",
            "cooperative dream histories",
            "coalition-minimal",
            "verifier-gated",
            "cost-dominating simulation",
            "a complete small worked trace",
        ):
            if required not in all_text:
                raise SystemExit(f"Missing key article content: {required}")
        if "AI authorship and reliability notice" not in first:
            raise SystemExit("Missing first-page disclaimer pointer")
        if "AI Authorship and Mathematical Reliability Disclaimer" not in final:
            raise SystemExit("Missing final-page AI disclaimer")
        if "End of manuscript" not in final:
            raise SystemExit("Final page is not the end of manuscript")
        if not all(txt.strip() for txt in texts):
            raise SystemExit("Empty or unreadable PDF page")
        # Check visible text against page boundaries.
        for page in pdf:
            for word in page.get_text("words"):
                if word[0] < -1 or word[1] < -1 or word[2] > page.rect.width + 1 or word[3] > page.rect.height + 1:
                    raise SystemExit("Page contains out-of-bounds text")
        for page in pdf:
            fonts = page.get_fonts(full=True)
            if not fonts:
                raise SystemExit("A page has no embedded-font text")

    dest = DOCS / IDENT
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(generated, dest / PDF_NAME)
    shutil.copyfile(source, dest / "source.tex")
    digest = hashlib.sha256((dest / PDF_NAME).read_bytes()).hexdigest()

    # The list order, not the numerical 'order' metadata, determines slot placement.
    # Keep all existing publication items in their exact original relative order.
    lo = float(original[0].get("order", 0))
    hi = float(original[1].get("order", lo + 1))
    between = (lo + hi) / 2 if hi > lo else lo + 0.5
    record = {
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
            "Self-contained, Atlas-audited research exposition on five-ATP cooperative "
            "dream histories. Defines a structured SYMPHONY score, proves a five-member "
            "coalition-minimal Horn witness and a conditional verifier-gated soundness "
            "result, and distinguishes genuine distributed evidence from hypothetical "
            "equal-information computational speedup. Version 2.0."
        ),
        "classification_note": (
            "Version 2.0, 3 November 2026. Human-originated, AI-assisted exposition. "
            "Mathematical witnesses and conditional theorems are developed for stipulated "
            "models, not an independently machine-checked or authenticated installed "
            "five-ATP federation. The full reliability disclaimer is the final PDF page."
        ),
        "publication_date": "3 November 2026",
        "status": (
            "Atlas editorial audit and iterative repairs completed. "
            "No independently machine-checked proof or measured search advantage claimed."
        ),
        "pages": 16,
        "sha256": digest,
        "order": between,
    }
    before["items"] = [original[0], record, *original[1:]]
    CATALOG.write_text(json.dumps(before, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    for old_page in (DOCS / "index.html", DOCS / SUBJECT / "index.html"):
        old_page.unlink(missing_ok=True)
    subprocess.run([sys.executable, "scripts/build_publications_106.py"],
                   cwd=ROOT, check=True)

    after = json.loads(CATALOG.read_text(encoding="utf-8"))["items"]
    assert len(after) == len(original) + 1, "Publication count changed unexpectedly"
    assert after[0]["id"] == MUSIC_ID, "MUSIC moved from slot 1"
    assert after[1]["id"] == IDENT, "Symphonies not in slot 2"
    assert after[2]["id"] == previous_second, "Old slot 2 not shifted to slot 3"
    assert [x["id"] for x in after if x["id"] != IDENT] == old_ids, "Existing relative order changed"
    assert after[0] == original[0], "MUSIC catalog record unexpectedly modified"
    assert after[2:] == original[1:], "An existing catalog record unexpectedly modified"
    for index_page in (DOCS / "index.html", DOCS / SUBJECT / "index.html"):
        html = index_page.read_text(encoding="utf-8")
        hrefs = re.findall(r'<article class="card"[^>]*><h2><a href="([^"]+)"', html)
        expected = ["/pub/" + x + "/" for x in (MUSIC_ID, IDENT, previous_second)]
        if hrefs[:3] != expected:
            raise SystemExit(f"Incorrect first three cards in {index_page}: {hrefs[:3]}")
    assert (dest / "index.html").is_file(), "Missing Symphonies reader page"
    assert (dest / "source.html").is_file(), "Missing source reader page"
    assert (dest / PDF_NAME).stat().st_size > 100_000
    print("PASS: MUSIC remains slot 1; Symphonies is slot 2; old slot 2 is now slot 3.")
    print(f"PASS: {len(original)} prior records retained in their original order.")
    print("PASS: 16-page audited manuscript with first- and last-page disclaimers.")
    print("PDF SHA256:", digest)
    print(f"Reader: https://btenneson.github.io/pub/{IDENT}/")
    print(f"PDF: https://btenneson.github.io/pub/{IDENT}/{PDF_NAME.replace(' ', '%20')}")

if __name__ == "__main__":
    main()
