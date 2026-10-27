#!/usr/bin/env python3
"""Publish One-Way Pac-Man FDWC Completion B only, at slot 1.

Use the exact already-selected source. Compile it without editorial changes.
Keep all existing publication cards in their existing relative order.
"""
from pathlib import Path
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "incoming_publications/one_way_pac_man_fdwc_completion_b_0_1"
SOURCE = STAGE / "source.tex"
SLUG = "cs.LO_Logic_in_Computer_Science/one_way_pac_man_fdwc_completion_b_0_1"
DEST = ROOT / "docs" / SLUG
BUILD = ROOT / ".build" / "one_way_pac_man_fdwc_completion_b_0_1"
PDF_NAME = "One_Way_Pac_Man_FDWC_Completion_B_0_1.pdf"
EXPECTED_SOURCE_SHA256 = "f37a8c56baaa3746b68b7851c163056d2abf4b57f62d07f79985a53d1d38427f"
TITLE = "One-Way Pac-Man: Certified Proof Search, BANK Provenance, and Finite-Cost Frontiers"
QUOTE = "The deposit itself must be charged to the path leading to the enlarged BANK."
CATALOG = ROOT / "scripts/publications.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compile_exact_source():
    assert SOURCE.is_file(), "Missing authorized FDWC Completion B LaTeX"
    assert sha(SOURCE) == EXPECTED_SOURCE_SHA256, "Source differs from authorized Completion B"
    source_text = SOURCE.read_text(encoding="utf-8")
    assert r"\def\CompletionLabel{ALTERNATIVE B}" in source_text
    assert r"\end{document}" in source_text
    assert QUOTE in source_text
    assert r"\newcommand{\AuthorTag}{\textless{}Brian Tenneson\textgreater{}}" in source_text
    BUILD.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(BUILD), str(SOURCE)],
            cwd=STAGE, stdout=subprocess.DEVNULL, check=True
        )
    compiled = BUILD / "source.pdf"
    assert compiled.is_file() and compiled.read_bytes().startswith(b"%PDF-")
    info = subprocess.check_output(["pdfinfo", str(compiled)], text=True)
    assert re.search(r"(?m)^Pages:\s*7\s*$", info), "Unexpected page count (expected seven)"
    assert "<Brian Tenneson>" in info, "Author PDF metadata missing"
    extracted = subprocess.check_output(["pdftotext", str(compiled), "-"], text=True)
    for phrase in ("One-Way Pac-Man", "Certified Proof Search", "Finite-Cost Frontiers"):
        assert phrase in extracted, f"Compiled manuscript missing {phrase}"
    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, DEST / "source.tex")
    shutil.copy2(compiled, DEST / PDF_NAME)
    return sha(DEST / PDF_NAME)

def record(pdf_sha):
    return {
        "id": SLUG, "href": SLUG + "/",
        "title": TITLE,
        "kind": "Research paper",
        "subject": "cs.LO_Logic_in_Computer_Science",
        "authors": "<Brian Tenneson>",
        "pdf": SLUG + "/" + PDF_NAME,
        "archive_path": "docs/" + SLUG + "/" + PDF_NAME,
        "source": SLUG + "/source.html",
        "source_file": SLUG + "/source.tex",
        "card_text": (
            "The single proof-seeking Pac-Man is a verifier-gated ATP traversing a fixed "
            "graph of complete states. FDWC Completion B develops proof-carrying BANK "
            "provenance, finite certificate expansion, conservative-deposit counterexamples, "
            "and an exhaustive finite-cost frontier that can sometimes certify the exact "
            "distance to proof settlement. Conditional mathematics, not a measured speedup."
        ),
        "quote": QUOTE,
        "quote_attribution": "One-Way Pac-Man, FDWC Completion B · p. 3",
        "quote_page": 3,
        "quote_also_on_card": True,
        "status": (
            "PRELIMINARY RELEASE — FDWC Completion B · 26 October 2026. "
            "Derived solely from immutable source W0 (v0.2). "
            "Not independently proof-verified or externally peer-reviewed; "
            "no demonstrated online optimal policy or runtime improvement."
        ),
        "classification_note": (
            "Seven-page FDWC alternative B · 26 October 2026. "
            "LaTeX source reproduced byte-for-byte from the selected Library manuscript; "
            "PDF freshly recompiled without mathematical edits. Alternative A is not published here."
        ),
        "pages": 7,
        "sha256": pdf_sha,
        "publication_date": "26 October 2026"
    }

def place_catalog_item(rec):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    matches = [i for i, x in enumerate(data["items"]) if x["id"] == SLUG]
    assert len(matches) <= 1, "Duplicated publication identifier"
    if matches:
        assert data["items"][matches[0]]["sha256"] == rec["sha256"], "Re-run PDF mismatch"
        # A later publication may already have taken slot 1. Do not reorder it.
        return data["items"][matches[0]]
    current_min = min(
        (x["order"] for x in data["items"] if isinstance(x.get("order"), (int, float))),
        default=0
    )
    rec["order"] = current_min - 10
    data["items"].insert(0, rec)
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert data["items"][0]["id"] == SLUG
    return rec

def insert_card_first(path, rec):
    from scripts.build_publications import card, SUBJECTS
    markup = path.read_text(encoding="utf-8")
    needle = "/pub/" + SLUG + "/"
    if needle in markup:
        return
    marker = '<div class="grid" id="grid">'
    assert markup.count(marker) == 1, f"Card grid not found in {path}"
    enriched = dict(rec)
    code = rec["subject"].split("_")[0]
    enriched["category"] = code + " — " + SUBJECTS[code]
    markup = markup.replace(marker, marker + card(enriched), 1)
    count = len(re.findall(r'<article class="card"', markup))
    markup, changed = re.subn(
        r'(<p id="count" role="status">)\d+ publications(</p>)',
        lambda m: m.group(1) + str(count) + " publications" + m.group(2),
        markup, count=1
    )
    assert changed == 1, f"Count could not be updated in {path}"
    assert markup.index(needle) < markup.index('/pub/cs.LO_Logic_in_Computer_Science/two_armies_of_one_scout_probe_rendezvous_0_3/')
    path.write_text(markup, encoding="utf-8")

def add_sitemap():
    site = ROOT / "docs/sitemap.xml"
    body = site.read_text(encoding="utf-8")
    loc = "https://btenneson.github.io/pub/" + SLUG + "/"
    if loc not in body:
        body = body.replace("</urlset>", "  <url><loc>" + html.escape(loc) + "</loc></url>\n</urlset>")
        site.write_text(body, encoding="utf-8")

def main():
    digest = compile_exact_source()
    rec = place_catalog_item(record(digest))
    sys.path.insert(0, str(ROOT))
    insert_card_first(ROOT / "docs/index.html", rec)
    insert_card_first(ROOT / "docs/cs.LO_Logic_in_Computer_Science/index.html", rec)
    add_sitemap()
    subprocess.run([sys.executable, "scripts/build_publications.py"], cwd=ROOT, check=True)
    assert (DEST / "index.html").is_file()
    assert (DEST / "source.html").is_file()
    assert (DEST / PDF_NAME).is_file()
    assert sha(DEST / "source.tex") == EXPECTED_SOURCE_SHA256
    front = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    cards = re.findall(r'<article class="card".*?<h2><a href="([^"]+)"', front)
    assert cards and cards[0] == "/pub/" + SLUG + "/", "New manuscript not card slot 1"
    assert front.count("/pub/" + SLUG + "/") >= 1
    print("PUBLISHED FDWC B", SLUG, "pdf_sha256", digest, "slot=1")

if __name__ == "__main__":
    main()
