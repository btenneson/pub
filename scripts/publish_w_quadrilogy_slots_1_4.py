#!/usr/bin/env python3
"""Publish the authorized W0-W3 quadrilogy in four consecutive library slots."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys
import fitz

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/"incoming_publications/w_quadrilogy_20261031"
BUILD=ROOT/".build/w_quadrilogy_20261031"
DOCS=ROOT/"docs"
CATALOG=ROOT/"scripts/publications.json"
SUBJECT="cs.LO_Logic_in_Computer_Science"
ARTICLES=[
 dict(key="W0", slug="geodesic_continuation_and_multiresolution_omnicartography",
      title="Geodesic Continuation and Multiresolution Omnicartography — Version 4",
      filename="Geodesic_Continuation_and_Multiresolution_Omnicartography_Version_4.pdf",
      pages=23, quote="Thus the Omnicartographer need not know the complete geodesic or even the exact horizon values.", quote_page=3,
      kind="Core paper", synopsis="W0. Version 4 of the ancestral research paper on AMLD Pioneers, directional gaps, advance certification, oracle guidance and changing BANK geometry. Includes retrospective attribution, qualified settlements and the full AI disclaimer."),
 dict(key="W1", slug="cost_recertifying_geodesic_fdwc_w1",
      title="The Cost of Re-Certifying a Geodesic",
      filename="The_Cost_of_Re_Certifying_a_Geodesic_W1_v2.pdf",
      pages=20, quote="The proof does not require knowing the exact new settlement horizon.", quote_page=1,
      kind="Research paper", synopsis="W1. FDWC Level-1 multiarticle, Version 2. Investigates the validity of retained geodesics under verifier-gated BANK updates, portable proof evidence and the cost of recalculation. Citations and AI disclaimer included."),
 dict(key="W2", slug="certified_sufficiency_frontiers_repair_w2",
      title="Certified Sufficiency and the Frontiers of Repair",
      filename="Certified_Sufficiency_and_Frontiers_of_Repair_W2_v3_1.pdf",
      pages=15, quote="Three tasks must not be conflated", quote_page=3,
      kind="Research paper", synopsis="W2. Integrated FDWC Level-2, Version 3.1, ATLAS-audited. Establishes zero-outside frontier certificates, sufficient regions and a conditional separation between local certification and explicit global rebuilding."),
 dict(key="W3", slug="portal_quotients_decisional_memory_w3",
      title="Portal Quotients and Decisional Memory",
      filename="Portal_Quotients_and_Decisional_Memory_W3_v4_1.pdf",
      pages=14, quote="A BANK update may change the settlement distance of arbitrarily many states", quote_page=1,
      kind="Research paper", synopsis="W3. FDWC Level-3, Version 4.1, cited and ATLAS-audited. Develops finite portal representations for global BANK effects, decision-relative memory and distinctions among verification certificate languages.")
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s): return " ".join(s.split())

def main():
    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    before=list(data["items"])
    prior_ids=[x["id"] for x in before]
    assert len(prior_ids)==len(set(prior_ids)), "Original catalog has duplicate IDs"
    ids=[SUBJECT+"/"+a["slug"] for a in ARTICLES]
    assert ids[0] in prior_ids, "Existing W0 not found; do not create duplicate"
    assert all(n not in prior_ids for n in ids[1:]), "One or more new publications already exist; stop"
    old=[x for x in before if x["id"] not in ids]
    assert len(old)==len(before)-1
    old_visible=[x["id"] for x in old if x.get("visibility") not in ("hidden","archive")]
    assert len(old_visible)>=4
    BUILD.mkdir(parents=True,exist_ok=True)
    records=[]
    for a in ARTICLES:
        src=STAGE/a["key"]/"source.tex"
        assert src.is_file() and src.stat().st_size>25000, src
        work=BUILD/a["key"]
        work.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,work/"source.tex")
        for _ in range(4):
            p=subprocess.run(["pdflatex","-interaction=nonstopmode","-halt-on-error","source.tex"],
                cwd=work,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            if p.returncode:
                raise RuntimeError(a["key"]+" compilation failed:\n"+p.stdout[-4000:])
        pdf=work/"source.pdf"
        assert pdf.is_file() and pdf.read_bytes().startswith(b"%PDF-")
        with fitz.open(pdf) as d:
            assert len(d)==a["pages"],(a["key"],len(d),a["pages"])
            assert all(pg.get_text().strip() for pg in d),a["key"]+" blank page"
            first=norm(d[0].get_text()); last=norm(d[-1].get_text())
            assert "<Brian Tenneson>" in first, a["key"]+" author"
            assert "Disclaimer on Mathematical Accuracy" in last, a["key"]+" last-page disclaimer"
            assert norm(a["quote"]) in norm(d[a["quote_page"]-1].get_text()),a["key"]+" quote not found"
            if a["key"]=="W0": assert "Version 4" in first
        pubid=SUBJECT+"/"+a["slug"]
        path=ROOT/pubid
        docs=DOCS/pubid
        path.mkdir(parents=True,exist_ok=True)
        docs.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(pdf,path/a["filename"])
        shutil.copyfile(pdf,docs/a["filename"])
        shutil.copyfile(src,docs/"source.tex")
        if a["key"]=="W0":
            original=next(x for x in before if x["id"]==pubid)
            record=dict(original)
            # Retain historical W0 PDF as a valid legacy direct-link asset.
            # Rebuild the existing W0 reader to point to the reviewed new edition.
            (docs/"index.html").unlink(missing_ok=True)
        else: record={}
        record.update({
            "id":pubid,"href":pubid+"/","title":a["title"],
            "kind":a["kind"],"subject":SUBJECT,"authors":"<Brian Tenneson>",
            "pdf":pubid+"/"+a["filename"],"archive_path":pubid+"/"+a["filename"],
            "source":pubid+"/source.html","source_file":pubid+"/source.tex",
            "card_text":a["synopsis"],"quote":a["quote"],"quote_page":a["quote_page"],
            "quote_attribution":a["title"]+" · p. "+str(a["quote_page"]),
            "quote_also_on_card":True,
            "publication_date":"31 October 2026",
            "classification_note":a["key"]+" of the four-article W0→W3 research sequence, 31 October 2026. Research preprint; manuscript-level mathematical audit does not constitute peer review, historical originality certification or machine-verified proof.",
            "status":"Reviewed mathematical research preprint with explicit AI assistance, prior-art qualifications and stated verification limits.",
            "pages":a["pages"],"sha256":sha(pdf),
        })
        record.pop("visibility",None)
        records.append(record)
    data["items"]=records+old
    for i,rec in enumerate(data["items"],1): rec["order"]=i
    assert len(data["items"])==len(before)+3
    assert [x["id"] for x in data["items"][4:]]==[x["id"] for x in old]
    CATALOG.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # The catalog builder deliberately preserves reviewed HTML; release only the
    # home and subject indices for a controlled reorder and W0's new reader.
    for p in [DOCS/"index.html",DOCS/SUBJECT/"index.html"]:
        p.unlink(missing_ok=True)
    subprocess.run([sys.executable,"scripts/build_publications_106.py"],cwd=ROOT,check=True)
    generated=json.loads((DOCS/"search-index.json").read_text())
    seen=[x["id"] for x in generated["items"] if x.get("visibility") not in ("hidden","archive")]
    assert seen[:4]==ids,(seen[:4],ids)
    assert seen[4:4+len(old_visible)]==old_visible,"Existing public cards reordered or omitted"
    assert len(seen)==len(old_visible)+4
    for p in (DOCS/"index.html",DOCS/SUBJECT/"index.html"):
        links=re.findall(r'<article class="card"[^>]*><h2><a href="([^"]+)"',p.read_text())
        assert links[:4]==["/pub/"+s+"/" for s in ids],(p,links[:4])
        assert links[4]=="/pub/"+old_visible[0]+"/"
    for a in ARTICLES:
        d=DOCS/SUBJECT/a["slug"]
        assert (d/a["filename"]).is_file() and (d/"source.tex").is_file()
        reader=(d/"index.html").read_text()
        assert a["filename"] in reader and a["title"] in reader
        assert (d/"source.html").is_file()
    print("PASS W0–W3: 4 consecutive top slots, "+str(len(old_visible))+
          " preexisting public cards shifted without gaps or reorder.")
    print("Catalog canonical items:",len(data["items"]),
          "indexed items:",len(generated["items"]),
          "visible cards:",len(seen))
    print("Published document checksums:",{a["key"]:sha(DOCS/SUBJECT/a["slug"]/a["filename"]) for a in ARTICLES})
if __name__=="__main__": main()
