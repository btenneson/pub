#!/usr/bin/env python3
"""Publish the authorized ATLAS-repaired Completion C in slot 1.

Source is immutable for this operation. Compile it, validate the output, and
insert the publication ahead of existing cards without permuting their order.
"""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
SLUG = "cs.LO_Logic_in_Computer_Science/completion_c_epistemic_conservation_0_2"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
STAGE = ROOT / "incoming_publications/completion_c_epistemic_conservation_0_2/source.tex"
DEST = ROOT / "docs" / SLUG
BUILD = ROOT / ".build/completion_c_epistemic_conservation_0_2"
CATALOG = ROOT / "scripts/publications.json"
PDF_NAME = "Completion_C_Epistemic_Conservation_0_2_ATLAS_Repaired.pdf"
SOURCE_SHA256 = "08eb77db5acad673ada230d3f48e7974f996d115ecc4b5cecdc3350cba36abe8"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert STAGE.is_file() and digest(STAGE) == SOURCE_SHA256, "Source mismatch: refuse publication"
    tex = STAGE.read_text(encoding="utf-8")
    assert r"\end{document}" in tex and "ATLAS-repaired version 0.2" in tex
    BUILD.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(BUILD), str(STAGE)],
            cwd=ROOT, stdout=subprocess.DEVNULL, check=True
        )
    pdf = BUILD / "source.pdf"
    assert pdf.is_file() and pdf.read_bytes().startswith(b"%PDF-")
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    assert re.search(r"(?m)^Pages:\s*15\s*$", info), "Completion C should be 15 pages"
    extracted = subprocess.check_output(["pdftotext", str(pdf), "-"], text=True)
    for phrase in ["The Epistemic Conservation", "Exact", "indistinguishability", "ATLAS-repaired"]:
        assert phrase.lower() in extracted.lower(), f"Missing content: {phrase}"
    assert "<Brian Tenneson>" in info, "PDF metadata must retain exact author credit"
    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf, DEST / PDF_NAME)
    shutil.copyfile(STAGE, DEST / "source.tex")
    assert digest(DEST / "source.tex") == SOURCE_SHA256
    record = {
        "id": SLUG, "href": SLUG + "/",
        "title": "Completion C — The Epistemic Conservation of Mathematical Histories",
        "kind": "Research paper", "subject": SUBJECT,
        "authors": "<Brian Tenneson>",
        "pdf": SLUG + "/" + PDF_NAME,
        "archive_path": "docs/" + SLUG + "/" + PDF_NAME,
        "source": SLUG + "/source.html",
        "source_file": SLUG + "/source.tex",
        "card_text": (
            "Completion C intertwines two Level-1 discrete writing completions: a typed evidence "
            "calculus and an epistemic-boundary analysis. It proves exact retrospective "
            "audit-preservation criteria, distinguishes mathematical from computable "
            "reconstruction, derives finite-memory bounds, and develops future-transition "
            "conditions for safe history compression. Includes a worked oracle-ledger example "
            "and limits on effective quotient computation."
        ),
        "quote": "A retrospective archive can be correct today but insufficient to validate tomorrow's message.",
        "quote_attribution": "Completion C, ATLAS-repaired v0.2, introductory discussion",
        "quote_also_on_card": True,
        "status": (
            "ATLAS-repaired and re-audited v0.2, 15 pages. Conditional paper-level mathematics; "
            "no independent formal proof certification, external peer review, AMLD+0 engine "
            "execution, or physical truth-oracle implementation."
        ),
        "classification_note": (
            "Published as Completion C, 30 October 2026. A synthesis of FDWC Level-1 "
            "Completions A and B, not an A+B compilation. Immutable ancestors and other "
            "published papers are unchanged. Includes the author's AI disclaimer."
        ),
        "publication_date": "30 October 2026", "pages": 15,
        "sha256": digest(DEST / PDF_NAME)
    }
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    items = [x for x in data["items"] if x["id"] != SLUG]
    existing = next((x for x in data["items"] if x["id"] == SLUG), None)
    min_order = min((x["order"] for x in items if isinstance(x.get("order"), (int,float))), default=0)
    record["order"] = min_order - 10
    data["items"] = [record] + items
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Existing landing pages are curated and are intentionally not rewritten by the builder.
    # Force a regeneration from the authoritative ordered catalog.
    for page in [ROOT / "docs/index.html", ROOT / "docs" / SUBJECT / "index.html"]:
        if page.is_file():
            page.unlink()
    subprocess.run([sys.executable, "scripts/build_publications_106.py"], cwd=ROOT, check=True)
    home = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    subject = (ROOT / "docs" / SUBJECT / "index.html").read_text(encoding="utf-8")
    first_card = r'<article class="card"[^>]*><h2><a href="([^"]+)"'
    for markup in [home, subject]:
        cards = re.findall(first_card, markup)
        assert cards and cards[0] == "/pub/" + SLUG + "/", "Completion C is not first card"
    assert (DEST / "index.html").is_file() and (DEST / "source.html").is_file()
    assert (DEST / PDF_NAME).is_file() and (DEST / "source.tex").is_file()
    assert data["items"][1:] == items, "Existing relative catalog order changed"
    print("PUBLISHED Completion C:", SLUG, "PDF SHA256", record["sha256"], "slot=1")

if __name__ == "__main__":
    main()
