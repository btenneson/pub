#!/usr/bin/env python3
"""Publish the exact 14-page illustrated PDF in slot 1, shifting all prior cards.

The PDF is pre-staged as a binary Git object. No recompilation or image
substitution is permitted: publication must preserve the approved PDF SHA256.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CATALOG = ROOT / "scripts" / "publications.json"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
SLUG = "undecidable_attained_labels_with_finite_checkable_witnesses"
IDENT = f"{SUBJECT}/{SLUG}"
MUSIC_ID = f"{SUBJECT}/music_of_an_atp_expository_research_article_2_0"
SYMPHONY_ID = f"{SUBJECT}/symphonies_of_automated_theorem_provers_2_0"
TITLE = "Undecidable Attained Labels with Finite Checkable Witnesses"
PDF_NAME = "Undecidable_Attained_Labels_with_Finite_Checkable_Witnesses.pdf"
EXPECTED_SHA256 = "472e64e4da23b6e2b7de35448d8bf19361bbd0b9552ba26bb3703fb231e58ea7"

def main():
    pdf_path = DOCS / IDENT / PDF_NAME
    if not pdf_path.exists() or pdf_path.stat().st_size < 1_000_000:
        raise SystemExit("Missing exact illustrated PDF")
    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"PDF differs from approved illustrated edition: {digest}")

    import fitz
    with fitz.open(pdf_path) as pdf:
        if len(pdf) != 14:
            raise SystemExit(f"Expected 14 pages, found {len(pdf)}")
        if pdf.metadata.get("title") != TITLE:
            raise SystemExit("PDF metadata title does not match approved article")
        if not pdf[0].get_images(full=True):
            raise SystemExit("The black-and-white illustrated cover image is missing")
        inside = pdf[1].get_text().casefold()
        for expected in ("undecidable attained labels", "finite checkable witnesses",
                         "five-party quantum separation"):
            if expected not in inside:
                raise SystemExit(f"Interior article title or subtitle missing: {expected}")
        final = pdf[-1].get_text()
        if "Full AI-Assistance and Mathematical Reliability Disclaimer" not in final:
            raise SystemExit("Full final-page AI disclaimer is absent")
        if "End of manuscript" not in final:
            raise SystemExit("Unexpected final page content")
        for i, page in enumerate(pdf):
            if i and not page.get_text().strip():
                raise SystemExit(f"Empty text page {i+1}")
            for word in page.get_text("words"):
                if word[0] < -1 or word[1] < -1 or word[2] > page.rect.width + 1 or word[3] > page.rect.height + 1:
                    raise SystemExit(f"Text exceeds page boundary at page {i+1}")

    before = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = before["items"]
    if any(x["id"] == IDENT for x in entries):
        raise SystemExit("The target item already exists: refusing to insert a duplicate")
    original_ids = [x["id"] for x in entries]
    if len(set(original_ids)) != len(original_ids):
        raise SystemExit("Existing catalog contains duplicate identifiers")
    if len(entries) < 2 or original_ids[:2] != [MUSIC_ID, SYMPHONY_ID]:
        raise SystemExit("Unexpected current library slots; preserving existing records")

    new_entry = {
        "id": IDENT,
        "href": IDENT + "/",
        "subject": SUBJECT,
        "title": TITLE,
        "kind": "Research paper",
        "authors": "<Brian Tenneson>",
        "pdf": IDENT + "/" + PDF_NAME,
        "archive_path": "docs/" + IDENT + "/" + PDF_NAME,
        "card_text": (
            "Atlas-audited, illustrated research exposition connecting MUSIC, "
            "five-ATP SYMPHONY, deterministic–nondeterministic interfaces and "
            "adaptive composition. Develops the distinction between decidably "
            "checkable successful performance witnesses and undecidable global "
            "attainability, alongside exact five-qubit quantum calculations, "
            "finite deterministic-realization obstructions and verifier-gated "
            "adaptive conservativity."
        ),
        "classification_note": (
            "Illustrated Version 2.0, 3 November 2026. Author-directed, AI-assisted "
            "mathematical exposition. This is a collection of conditional and "
            "standard-background results plus proposals for future research. "
            "No independent machine-checked proof, deployed AMLD+0 federation, "
            "novel physics prediction or universal search improvement is claimed. "
            "Full reliability disclaimer appears on the PDF's last page."
        ),
        "publication_date": "3 November 2026",
        "status": (
            "Iteratively Atlas-audited editorial research edition. "
            "Original approved 14-page illustrated PDF preserved byte-for-byte."
        ),
        "pages": 14,
        "sha256": digest,
        "order": min(float(x.get("order", i)) for i, x in enumerate(entries)) - 1,
    }

    before["items"] = [new_entry] + entries
    CATALOG.write_text(json.dumps(before, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    for old_page in (DOCS / "index.html", DOCS / SUBJECT / "index.html"):
        old_page.unlink(missing_ok=True)
    subprocess.run([sys.executable, "scripts/build_publications_106.py"],
                   cwd=ROOT, check=True)

    after = json.loads(CATALOG.read_text(encoding="utf-8"))["items"]
    assert len(after) == len(entries) + 1
    assert after[0]["id"] == IDENT
    assert after[1:] == entries, "Existing catalog entries changed or reordered"
    assert [x["id"] for x in after[:3]] == [IDENT, MUSIC_ID, SYMPHONY_ID]
    assert hashlib.sha256(pdf_path.read_bytes()).hexdigest() == EXPECTED_SHA256
    for index_page in (DOCS / "index.html", DOCS / SUBJECT / "index.html"):
        text = index_page.read_text(encoding="utf-8")
        hrefs = re.findall(r'<article class="card"[^>]*><h2><a href="([^"]+)"', text)
        expected = ["/pub/" + v + "/" for v in (IDENT, MUSIC_ID, SYMPHONY_ID)]
        if hrefs[:3] != expected:
            raise SystemExit(f"Card order mismatch for {index_page}: {hrefs[:3]}")
    if not (DOCS / IDENT / "index.html").is_file():
        raise SystemExit("Missing public PDF reader page")
    print("PASS: Exact illustrated 14-page PDF and complete final disclaimer.")
    print("PASS: New paper slot 1; MUSIC slot 2; Symphonies slot 3.")
    print(f"PASS: All {len(entries)} prior catalog entries retain their order and fields.")
    print("PDF SHA256:", digest)
    print(f"Reader: https://btenneson.github.io/pub/{IDENT}/")

if __name__ == "__main__":
    main()
