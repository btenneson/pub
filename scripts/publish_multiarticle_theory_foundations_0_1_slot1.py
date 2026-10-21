#!/usr/bin/env python3
"""Publish the two-page Multiarticle Theory foundation at slot #1."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile
import fitz

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = "cs.LO_Logic_in_Computer_Science"
SLUG = SUBJECT + "/multiarticle_theory_foundations_0_1"
STEM = "Multiarticle_Theory_Foundations_0_1"
TITLE = "Multiarticle Theory: A Short Foundational Text"
QUOTE = "The word transcendent signals the crossing of an article-level consequence boundary."
SOURCE = ROOT / "incoming_publications/multiarticle_theory_foundations_0_1/source.tex"
source = SOURCE.read_bytes()
assert b"Transcendent theorem" in source and b"\\end{document}" in source
build = ROOT / ".build/multiarticle_theory_foundations_0_1"
build.mkdir(parents=True, exist_ok=True)
tex = build / (STEM + ".tex")
tex.write_bytes(source)
for pass_num in range(2):
    subprocess.run(["pdflatex","-interaction=nonstopmode","-halt-on-error",tex.name],
                   cwd=build,check=True)
pdf = build / (STEM + ".pdf")
raw = pdf.read_bytes()
with fitz.open(stream=raw,filetype="pdf") as d:
    assert len(d)==2, f"Expected precisely 2 pages; found {len(d)}"
    all_pages=[" ".join(p.get_text().split()) for p in d]
    assert QUOTE in all_pages[1], "Card quotation not present on second page"
    assert all(len(s)>400 for s in all_pages), "Empty or unreadable PDF page"
    assert "Transcendent theorem" in " ".join(all_pages), "Missing central definition"
for folder in (ROOT/"docs"/SLUG,ROOT/SLUG):
    folder.mkdir(parents=True, exist_ok=True)
    (folder/(STEM+".pdf")).write_bytes(raw)
    (folder/"source.tex").write_bytes(source)
with zipfile.ZipFile(ROOT/"docs"/SLUG/(STEM+"_LaTeX_and_PDF.zip"),"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr(STEM+".pdf",raw)
    z.writestr(STEM+".tex",source)
catalog = ROOT/"scripts/publications.json"
data = json.loads(catalog.read_text(encoding="utf-8"))
old = [x for x in data["items"] if x.get("id")!=SLUG]
ids = [x["id"] for x in old]
assert len(ids)==len(set(ids)), "Pre-existing duplicate catalog IDs"
order = min([x.get("order",0) for x in old if isinstance(x.get("order"),int)] + [0])-1
card = {
  "id": SLUG, "href":SLUG+"/", "title":TITLE,
  "kind":"Foundational reference", "subject":SUBJECT,
  "pdf":SLUG+"/"+STEM+".pdf", "archive_path":SLUG+"/"+STEM+".pdf",
  "source":SLUG+"/source.html", "source_file":SLUG+"/source.tex",
  "source_package":SLUG+"/"+STEM+"_LaTeX_and_PDF.zip",
  "sha256":hashlib.sha256(raw).hexdigest(),
  "sha256_tex":hashlib.sha256(source).hexdigest(),
  "pages":2, "order":order, "authors":"Brian Tenneson",
  "quote":QUOTE,"quote_page":2,"card_quote":QUOTE,
  "card_quote_attribution":"Multiarticle Theory Foundations 0.1, p. 2",
  "quote_also_on_card":True,
  "card_text":"A concise two-page foundation for multiarticle theorem graphs, deductive surplus, structural zipping, and transcendent theorems: consequences in the combined theory's closure but in no individual source closure. Includes a formal definition, a worked modus ponens example, and the necessary derivability and non-derivability proof obligations.",
  "status":"FOUNDATIONAL RESEARCH NOTE · 21 OCTOBER 2026. Terminology defined relative to declared formal contexts; no historical novelty or proof-assistant certification asserted.",
  "classification_note":"Short general introduction, separate from the six-paper Multiarticle Theory 0.1 case study and its ATLAS-style audit 0.2."
}
data["items"]=[card]+old
assert [x["id"] for x in data["items"][1:]]==ids, "Prior catalog relative order changed"
catalog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
subprocess.run(["python","scripts/build_publications_106.py"],cwd=ROOT,check=True)
search = json.loads((ROOT/"docs/search-index.json").read_text(encoding="utf-8"))
assert search["items"][0]["id"]==SLUG,"New item is not slot #1"
assert [x["id"] for x in search["items"][1:]][:len(ids)]==ids[:len(search["items"])-1], "Existing search order unexpectedly changed"
home = (ROOT/"docs/index.html").read_text(encoding="utf-8")
first=home.split('<article class="card"',1)[1].split("</article>",1)[0]
assert TITLE in first and "transcendent" in first.lower(), "First card wrong"
assert (ROOT/"docs"/SLUG/"index.html").is_file(),"Reader missing"
assert (ROOT/"docs"/SLUG/"source.html").is_file(),"LaTeX source reader missing"
assert (ROOT/"docs"/SLUG/"source.tex").read_bytes()==source
assert (ROOT/SLUG/(STEM+".pdf")).read_bytes()==raw
print("PASS: exact two-page text from original LaTeX compiled and published in slot #1.")
print(f"PASS: all {len(old)} preexisting cards retained in the same relative order.")
