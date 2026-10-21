#!/usr/bin/env python3
"""Publish FAIR-ZIP paper as the new first library card; preserve previous order."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile
import fitz

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = "cs.LO_Logic_in_Computer_Science"
SLUG = SUBJECT + "/transcendent_theorem_search_brute_force_vs_delicate_0_1"
STEM = "Transcendent_Theorem_Search_Brute_Force_vs_Delicate_0_1"
TITLE = "The Search for Transcendent Theorems in Multiarticle Theory: a Brute Force versus a More Delicate Approach"
QUOTE = "Inspect everything at least once; explore selectively thereafter; certify without compromise; and never mistake an unvisited proof for a nonexistent theorem."
SOURCE = ROOT / "incoming_publications/transcendent_theorem_search_brute_force_vs_delicate_0_1/source.tex"
source = SOURCE.read_bytes()
assert hashlib.sha256(source).hexdigest() == "cf8b21fcabc07371602217bfe4e6780867dcdbf2031084502058e5601af1393d", "Published source bytes differ from reviewed article"
build = ROOT / ".build/transcendent_theorem_search_brute_force_vs_delicate_0_1"
build.mkdir(parents=True,exist_ok=True)
(build/(STEM+".tex")).write_bytes(source)
for _ in range(3):
    subprocess.run(["pdflatex","-interaction=nonstopmode","-halt-on-error",STEM+".tex"],cwd=build,check=True,stdout=subprocess.DEVNULL)
raw = (build/(STEM+".pdf")).read_bytes()
with fitz.open(stream=raw, filetype="pdf") as doc:
    assert len(doc)==9, f"Expected 9-page PDF, got {len(doc)}"
    text = " ".join(" ".join(page.get_text().split()) for page in doc)
    assert all(len(page.get_text().strip()) > 400 for page in doc), "Unrendered PDF page"
    for phrase in ("FAIR-ZIP","2,415","54,740","Lossy search and perfect fidelity","Inspect everything at least once"):
        assert phrase in text, f"Missing reviewed article passage: {phrase}"
for folder in (ROOT/"docs"/SLUG, ROOT/SLUG):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/(STEM+".pdf")).write_bytes(raw)
    (folder/"source.tex").write_bytes(source)
pkg_name=STEM+"_Full_Source_and_PDF.zip"
with zipfile.ZipFile(ROOT/"docs"/SLUG/pkg_name,"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr(STEM+".pdf",raw)
    z.writestr(STEM+".tex",source)
    z.writestr("PUBLICATION_NOTE.txt","FAIR-ZIP 0.1; selective investigation is incomplete but accepted proof obligations remain unchanged. 70-article costs are estimates, not benchmarks.\n")
catalog=ROOT/"scripts/publications.json"
data=json.loads(catalog.read_text(encoding="utf-8"))
previous=[item for item in data["items"] if item["id"]!=SLUG]
prior_ids=[item["id"] for item in previous]
assert len(prior_ids)==len(set(prior_ids))
order=min([item.get("order",0) for item in previous if isinstance(item.get("order"),int)]+[0])-1
card={
 "id":SLUG,"href":SLUG+"/","title":TITLE,"kind":"Research paper","subject":SUBJECT,
 "pdf":SLUG+"/"+STEM+".pdf","archive_path":SLUG+"/"+STEM+".pdf",
 "source":SLUG+"/source.html","source_file":SLUG+"/source.tex",
 "source_package":SLUG+"/"+pkg_name,
 "sha256":hashlib.sha256(raw).hexdigest(),"sha256_tex":hashlib.sha256(source).hexdigest(),
 "pages":9,"order":order,"authors":"Brian Tenneson",
 "quote":QUOTE,"quote_page":9,"card_quote":QUOTE,
 "card_quote_attribution":"Brian Tenneson, FAIR-ZIP version 0.1, conclusion, p. 9",
 "quote_also_on_card":True,
 "card_text":"Brute-force versus FAIR-ZIP approaches to transcendent-theorem search in Multiarticle Theory. All 70 settler-related articles receive a substantive first examination; 100–200 selected pair investigations replace 2,415 exhaustive pairs. The 91.72–95.86% reductions are pair-workload scenarios, not measured total computational savings. Selection is lossy in coverage, but accepted proofs retain exact fidelity and provenance.",
 "status":"RESEARCH ARTICLE · VERSION 0.1 · 21 OCTOBER 2026. Cost scenarios illustrative; FAIR-ZIP not empirically benchmarked and no exhaustive 70-source transcendent theorem census claimed.",
 "classification_note":"Nine-page mathematical and methodological research paper. It distinguishes finite source coverage, selective theorem discovery, strict closure-separation certificates, and the undecidability of unrestricted completeness."
}
data["items"]=[card]+previous
assert [item["id"] for item in data["items"][1:]]==prior_ids
catalog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
subprocess.run(["python","scripts/build_publications_106.py"],cwd=ROOT,check=True)
search=json.loads((ROOT/"docs/search-index.json").read_text(encoding="utf-8"))
assert search["items"][0]["id"]==SLUG,"New article did not reach slot 1"
assert [item["id"] for item in search["items"][1:1+len(prior_ids)]]==prior_ids, "Previous catalog order changed"
home=(ROOT/"docs/index.html").read_text(encoding="utf-8")
first=home.split('<article class="card"',1)[1].split("</article>",1)[0]
assert TITLE in first and "FAIR-ZIP" in first
for name in ("index.html","source.html","source.tex",STEM+".pdf",pkg_name):
    assert (ROOT/"docs"/SLUG/name).is_file(),f"Publication asset missing: {name}"
assert (ROOT/"docs"/SLUG/"source.tex").read_bytes()==source
assert (ROOT/SLUG/(STEM+".pdf")).read_bytes()==raw
print(f"PASS: nine-page FAIR-ZIP article in slot 1; {len(prior_ids)} previous canonical entries preserved in exact order")
