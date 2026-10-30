#!/usr/bin/env python3
"""Publish the authorized Two Geometries expository article in slot 1.

The staged LaTeX source is immutable for this operation.  The built PDF,
reader and source are validated before the catalog is changed; existing
entries retain their relative order.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SLUG = "cs.LO_Logic_in_Computer_Science/two_geometries_of_automated_theorem_proving_0_2"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
STAGE = ROOT / "incoming_publications/two_geometries_atlas_repaired_v0_2/source.tex"
DEST = ROOT / "docs" / SLUG
BUILD = ROOT / ".build/two_geometries_atlas_repaired_v0_2"
CATALOG = ROOT / "scripts/publications.json"
PDF_NAME = "Two_Geometries_ATLAS_Repaired_v0_2.pdf"
SOURCE_SHA256 = "abe19393fb4cecde9ff01ea15140f64d16e4d56de415c87ca4c7838d88075145"
QUOTE = (
    "A history tells us how an execution proceeded; a proof object tells us "
    "why a conclusion follows under its stated formal rules."
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def main():
    assert STAGE.is_file(), "Publication source is missing"
    assert digest(STAGE) == SOURCE_SHA256, "Source changed; publication refused"
    tex = STAGE.read_text(encoding="utf-8")
    for check in [
        r"\end{document}", "<Brian Tenneson>",
        "See the AI disclaimer that follows this essay.",
        "Disclaimer on Mathematical Accuracy",
        "P.1", "P.2", "P.3", "P.4"
    ]:
        assert check in tex, "Source check failed: " + check

    BUILD.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(BUILD), str(STAGE)],
            cwd=ROOT, check=True
        )
    built = BUILD / "source.pdf"
    assert built.is_file() and built.read_bytes().startswith(b"%PDF-")
    import fitz
    doc = fitz.open(built)
    assert len(doc) == 9, f"Expected 9 pages; found {len(doc)}"
    assert all(doc[i].get_text().strip() for i in range(9)), "Unreadable PDF page"
    assert norm(QUOTE) in norm(doc[0].get_text()), "Card quotation not on PDF p.1"
    assert doc.metadata.get("author") == "<Brian Tenneson>", "Author metadata changed"
    full_text = "\n".join(page.get_text() for page in doc)
    assert "Disclaimer on Mathematical Accuracy" in full_text
    assert "Exact Addressing" in full_text
    doc.close()

    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(built, DEST / PDF_NAME)
    shutil.copyfile(STAGE, DEST / "source.tex")
    assert digest(DEST / "source.tex") == SOURCE_SHA256

    record = {
        "id": SLUG,
        "href": SLUG + "/",
        "title": "Two Geometries of Automated Theorem Proving: Histories, Proofs, Certificates, and Safe Compression",
        "kind": "Architecture and expository article",
        "subject": SUBJECT,
        "authors": "<Brian Tenneson>",
        "pdf": SLUG + "/" + PDF_NAME,
        "archive_path": "docs/" + SLUG + "/" + PDF_NAME,
        "source": SLUG + "/source.html",
        "source_file": SLUG + "/source.tex",
        "card_text": (
            "An expository development of the prologue to Exact Addressing, Preliminary Release 4.14. "
            "It distinguishes the finite history tree of an automated theorem prover from accepted "
            "proof DAGs, and explains P.1 history unfolding, P.2 proof geometry, P.3 conditional "
            "certificate extraction and origin evidence, and P.4 verifier-safe operational quotients "
            "with cost-preserving bisimulation. Includes five black-and-white figures and describes "
            "why structural compression alone cannot establish an overall ATP search speedup."
        ),
        "quote": QUOTE,
        "quote_page": 1,
        "quote_attribution": "Two Geometries, expository edition v0.2, p. 1",
        "quote_also_on_card": True,
        "status": (
            "ATLAS-reviewed and repaired expository edition v0.2, nine pages. "
            "Source-concordance and editorial review completed; no independent "
            "proof-assistant verification or external peer review is claimed."
        ),
        "classification_note": (
            "Expository article dated 30 October 2026, adapted from the Prologue to "
            "Exact Addressing 4.14. Original source and mathematical qualifications are "
            "preserved. Contains the author's AI disclaimer. Not a formal-verification receipt."
        ),
        "publication_date": "30 October 2026",
        "pages": 9,
        "sha256": digest(DEST / PDF_NAME)
    }

    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    # Repair the sole pre-existing absent quote-page citation. The quoted
    # sentence is on p. 2 of the existing 15-page Completion C PDF.
    for item in data["items"]:
        if item["id"] == "cs.LO_Logic_in_Computer_Science/completion_c_epistemic_conservation_0_2":
            assert item.get("quote") == "A retrospective archive can be correct today but insufficient to validate tomorrow's message."
            if not item.get("quote_page"):
                item["quote_page"] = 2
    old = [x for x in data["items"] if x["id"] != SLUG]
    record["order"] = min(
        (x["order"] for x in old if isinstance(x.get("order"), (int, float))),
        default=0
    ) - 10
    data["items"] = [record] + old
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # The site generator intentionally preserves existing curated pages.
    # Remove only the two gallery pages so they will reflect new slot #1.
    for page in [ROOT / "docs/index.html", ROOT / "docs" / SUBJECT / "index.html"]:
        if page.is_file():
            page.unlink()
    subprocess.run([sys.executable, "scripts/build_publications_106.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/audit_subject_catalog_106.py"], cwd=ROOT, check=True)

    home = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    subject = (ROOT / "docs" / SUBJECT / "index.html").read_text(encoding="utf-8")
    first_card = r'<article class="card"[^>]*><h2><a href="([^"]+)"'
    for markup in [home, subject]:
        links = re.findall(first_card, markup)
        assert links and links[0] == "/pub/" + SLUG + "/", "Not slot 1"
    search = json.loads((ROOT / "docs/search-index.json").read_text())
    assert search["items"][0]["id"] == SLUG
    assert data["items"][1:] == old, "Previous catalog order changed"
    for name in ["index.html", "source.html", "source.tex", PDF_NAME]:
        assert (DEST / name).is_file(), "Missing publication asset: " + name
    assert (DEST / PDF_NAME).stat().st_size > 10000
    print("PASS: Two Geometries v0.2 is publication slot #1.")
    print("Public reader: https://btenneson.github.io/pub/" + SLUG + "/")
    print("Published PDF SHA256: " + record["sha256"])

if __name__ == "__main__":
    main()
