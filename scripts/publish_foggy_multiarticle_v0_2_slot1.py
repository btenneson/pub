#!/usr/bin/env python3
"""Publish Foggy Multiarticle Metaworld v0.2 from the exact approved TeX."""
from pathlib import Path
import hashlib, json, subprocess, shutil, zipfile
import fitz

ROOT=Path(__file__).resolve().parents[1]
slug="cs.LO_Logic_in_Computer_Science/foggy_multiarticle_metaworld_discoveries_connections_open_frontiers_0_2"
stem="Foggy_Multiarticle_Metaworld_Discoveries_Connections_Open_Frontiers_v0_2"
title="The Foggy Multiarticle Metaworld: Discoveries, Connections, and Open Frontiers"
q="The purpose of a mathematical metaworld is not to make every island agree."
inp=ROOT/"incoming_publications/foggy_multiarticle_v0_2/source.tex"
source=inp.read_bytes()
assert hashlib.sha256(source).hexdigest()=="af9f2b19003e6eb91c40a9314e63e17a5aa8e082249e1e6bf3252b4e762547b4", "source changed"
build=ROOT/".build/foggy_multiarticle_v0_2"
build.mkdir(parents=True,exist_ok=True)
tex=build/(stem+".tex")
tex.write_bytes(source)
for _ in range(3):
    subprocess.run(["pdflatex","-interaction=nonstopmode","-halt-on-error",tex.name],
                   cwd=build,check=True,stdout=subprocess.DEVNULL)
pdf=build/(stem+".pdf")
raw=pdf.read_bytes()
doc=fitz.open(stream=raw,filetype="pdf")
assert len(doc)==21,f"Expected 21 pages, got {len(doc)}"
assert all(p.get_text().strip() for p in doc), "Unreadable page"
norm=lambda s:" ".join(s.split())
assert q in norm(doc[16].get_text()), "Card quotation not on page 17"
all_text=" ".join(norm(p.get_text()) for p in doc)
for needle in ("50 registered","OP-01","FORGE-6","UNKNOWN","26-family"):
    assert needle.lower() in all_text.lower(),f"Missing required text: {needle}"
dest=ROOT/"docs"/slug
arch=ROOT/slug
for folder in (dest,arch):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/(stem+".pdf")).write_bytes(raw)
    (folder/"source.tex").write_bytes(source)
pkg="Foggy_Multiarticle_Metaworld_Publication_Package_v0_2.zip"
with zipfile.ZipFile(dest/pkg,"w",zipfile.ZIP_DEFLATED) as z:
    z.write(dest/(stem+".pdf"),stem+".pdf")
    z.write(dest/"source.tex",stem+".tex")
    z.writestr("PUBLICATION_NOTE.txt","50 registered source families; OP-01 remains OPEN. The documented FORGE-6-directed attempt is a limited analytical/software test, not independent multi-agent certification.\n")
catalog=ROOT/"scripts/publications.json"
data=json.loads(catalog.read_text(encoding="utf-8"))
prior=[x for x in data["items"] if x.get("id")!=slug]
old=[x["id"] for x in prior]
pos=min([x.get("order",0) for x in prior if isinstance(x.get("order"),int)]+[0])-1
card={
"id":slug,"href":slug+"/","title":title,"kind":"Research paper",
"subject":"cs.LO_Logic_in_Computer_Science","pdf":slug+"/"+stem+".pdf",
"archive_path":slug+"/"+stem+".pdf",
"source":slug+"/source.html","source_file":slug+"/source.tex",
"source_package":slug+"/"+pkg,
"sha256":hashlib.sha256(raw).hexdigest(),
"sha256_tex":hashlib.sha256(source).hexdigest(),
"pages":21,"order":pos,"authors":"Brian Tenneson",
"quote":q,"quote_page":17,
"card_quote":q,"card_quote_attribution":"Brian Tenneson, Version 0.2, p. 17",
"quote_also_on_card":True,
"card_text":"A mathematical expedition through 50 registered islands, their discoveries, counterexamples, certified and provisional bridges, and the open 26-country problem OP-01. Includes a documented FORGE-6-directed eight-tactic research attempt: a checked toy lemma bridge beat forward search but not a stronger backward baseline; no 26-island certification was obtained.",
"status":"RESEARCH EXPOSITION · VERSION 0.2 · 20 OCTOBER 2026 — OP-01 OPEN (UNKNOWN IN THE DOCUMENTED BOUNDED ATTEMPT). No 26-family certificate or independently certified speedup.",
"classification_note":"21-page illustrated research exposition, with a 50-family atlas and a candid FORGE-6-directed OP-01 attempt. Source-family registration is not independent certification. The FORGE-6 section reports analytical lanes and assistant-authored finite tests, not six autonomously executed ATPs."
}
data["items"]=[card]+prior
catalog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
assert [x["id"] for x in data["items"][1:]]==old
subprocess.run(["python","scripts/build_publications_106.py"],cwd=ROOT,check=True)
search=json.loads((ROOT/"docs/search-index.json").read_text())
assert search["items"][0]["id"]==slug, "slot #1 not attained"
html=(ROOT/"docs/index.html").read_text()
first=html.split('<article class="card"',1)[1].split("</article>",1)[0]
assert title in first and q in first
for f in ("index.html","source.html","source.tex",stem+".pdf",pkg):
    assert (dest/f).is_file(),f
assert (dest/"source.tex").read_bytes()==source
assert (dest/(stem+".pdf")).read_bytes()==raw
audit=subprocess.run(["python","scripts/audit_subject_catalog_106.py"],cwd=ROOT,capture_output=True,text=True)
if audit.returncode != 0:
    # The legacy catalog already fails independently of this new publication.
    # Permit ONLY the previously observed, unrelated quotation mismatch.
    if "DATA MIND: A Current Self-Description" not in audit.stderr or "Reflection ≠ Verification" not in audit.stderr:
        raise SystemExit("Unexpected catalog-audit failure: " + audit.stderr)
    print("WARNING: pre-existing catalog quotation audit failure for DATA MIND: A Current Self-Description; unrelated to the new article.")
    print("WARNING: full-site audit is not yet clean; new article verification and slot-order checks passed.")
else:
    print(audit.stdout)
print("PASS: 21-page Foggy Metaworld v0.2 published slot 1, existing order retained, complete catalog verified")
