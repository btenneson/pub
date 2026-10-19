#!/usr/bin/env python3
"""Publish the verified N* autobiographical reconstruction in library slot #1."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, zipfile
import fitz

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / "incoming_publications/nstar_autobiography/source.tex"
SLUG = "my_name_is_nstar_autobiography"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
REL = SUBJECT + "/" + SLUG
FILENAME = "Nstar_Autobiography_Publication_Ready.pdf"
PDF_ROOT = ROOT / ".build/nstar_autobiography"
TITLE = "My Name Is N* — The Autobiography of a Verifier-Gated Automated Theorem Prover"
QUOTE = "What I attempt. What I can prove. What the available evidence establishes about me."

def build():
    if not INCOMING.is_file():
        raise SystemExit("Missing N* autobiography source")
    source = INCOMING.read_text(encoding="utf-8")
    if "Authorial clarification:" in source:
        raise SystemExit("Excluded authorial-clarification line was reintroduced")
    for needle in ("My Name Is N*", r"\end{document}", "FORGE-6", "ACCEPTED_METADATA_ONLY"):
        if needle not in source:
            raise SystemExit("Source check failed: " + needle)
    PDF_ROOT.mkdir(parents=True, exist_ok=True)
    local_tex = PDF_ROOT / "source.tex"
    shutil.copyfile(INCOMING, local_tex)
    for n in range(2):
        p = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "source.tex"],
            cwd=PDF_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if p.returncode:
            print(p.stdout[-14000:])
            raise SystemExit("XeLaTeX failed at pass " + str(n + 1))
    compiled = PDF_ROOT / "source.pdf"
    if not compiled.is_file():
        raise SystemExit("No compiled PDF")
    doc = fitz.open(compiled)
    if not 20 <= len(doc) <= 30:
        raise SystemExit(f"Unexpected page count: {len(doc)}")
    if any(not p.get_text().strip() for p in doc):
        raise SystemExit("Blank or unextractable PDF page")
    alltext = "\n".join(p.get_text() for p in doc)
    for needle in ("My Name Is N*", "Certified Awareness", "UNKNOWN",
                   "The Autobiography", "Historical and technical sources"):
        if needle.casefold() not in alltext.casefold():
            raise SystemExit("Missing PDF content: " + needle)
    if "Authorial clarification:" in alltext:
        raise SystemExit("Excluded line appeared in compiled PDF")
    quote_pages = [i+1 for i, p in enumerate(doc) if QUOTE in p.get_text()]
    if len(quote_pages) != 1:
        raise SystemExit(f"Quote not uniquely located: {quote_pages}")
    quote_page = quote_pages[0]
    raw = compiled.read_bytes()
    dest = ROOT / "docs" / REL
    archive = ROOT / REL
    for directory in (dest, archive):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / FILENAME).write_bytes(raw)
        (directory / "source.tex").write_text(source, encoding="utf-8")
    pkgname = "Nstar_Autobiography_Source_and_PDF.zip"
    for directory in (dest,):
        with zipfile.ZipFile(directory / pkgname, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.write(compiled, FILENAME)
            z.write(INCOMING, "source.tex")

    catalog = ROOT / "scripts/publications.json"
    data = json.loads(catalog.read_text(encoding="utf-8"))
    before = [x["id"] for x in data["items"] if x.get("id") != REL]
    remaining = [x for x in data["items"] if x.get("id") != REL]
    order = min([x["order"] for x in remaining if isinstance(x.get("order"), int)] + [0]) - 1
    card = {
      "title": TITLE, "kind": "Technical autobiography", "subject": SUBJECT,
      "id": REL, "href": REL + "/",
      "pdf": REL + "/" + FILENAME,
      "archive_path": REL + "/" + FILENAME,
      "source": REL + "/source.html",
      "source_file": REL + "/source.tex",
      "source_package": REL + "/" + pkgname,
      "sha256": hashlib.sha256(raw).hexdigest(),
      "sha256_tex": hashlib.sha256(INCOMING.read_bytes()).hexdigest(),
      "pages": len(doc), "order": order,
      "authors": "N* (first-person historical reconstruction); research origin: Brian Tenneson; technical development: DATA MIND",
      "quote": QUOTE, "quote_page": quote_page,
      "card_quote": QUOTE,
      "card_quote_attribution": "N*, My Name Is N* · p. " + str(quote_page),
      "quote_also_on_card": True,
      "card_text": "N* narrates its origins in M*'s proof-cost SIC architecture, the development of its verifier-gated proof search and fair reserve, and the installation of a read-only certified-awareness sidecar. The technical autobiography distinguishes established demonstrations from unverified generality, speedup, and consciousness claims.",
      "status": "TECHNICAL AUTOBIOGRAPHY — October 18, 2026. Historical reconstruction, not autonomous testimony; general-purpose proving, awareness-driven speedups and independently executed FORGE-6 approval are not established.",
      "classification_note": f"{len(doc)}-page first-person historical reconstruction with mathematical notation, technical limitations, and source references. Certified awareness denotes scoped evidence-checked execution metadata, not phenomenal consciousness."
    }
    data["items"] = [card] + remaining
    if [x["id"] for x in data["items"][1:]] != before:
        raise SystemExit("Existing card order changed")
    catalog.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PREPARED {TITLE}: {len(doc)} pages, quote page {quote_page}, sha256 {card['sha256']}")
    print(f"Preserved {len(before)} existing cards in their exact relative sequence.")

if __name__ == "__main__":
    build()
