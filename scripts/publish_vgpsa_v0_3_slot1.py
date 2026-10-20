#!/usr/bin/env python3
"""Publish Brian Tenneson's ATLAS-repaired VGPSA article in featured slot 1."""
from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile
import fitz

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "incoming_publications/vgpsa_v0_3"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
slug = SUBJECT + "/verifier_gated_prompt_self_awareness_atlas_v0_3"
stem = "VGPSA_Article_ATLAS_Repaired_v0_3"
pkg_name = "VGPSA_ATLAS_Repaired_v0_3_Source_PDF_and_Witness.zip"
title = "Verifier-Gated Prompt Self-Awareness: A Lemma-Fishing Experiment in Certified Prompt Reflection"
quote = "A string containing the literal word ACCEPT is not itself an accepted certificate."
hashes = {
  "article.pdf": "70bd8e1088bedc459e75eb2a86a018674b05d138d368f2aab9a6d26f7c525b17",
  "source.tex": "c1112a9130c3ee5ed97e1a16ee0964ea63d571ec331ad5395da96c43ab07159f",
  "full_package.zip": "37d5df8f5a6814ecb2fada6bb3b9a3e5eaaf4968040bc96c703653426dc19906",
}
for fname, expected in hashes.items():
    path = IN / fname
    assert path.is_file(), f"Missing approved artifact {path}"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"Unexpected artifact contents: {path}"
pdf_bytes = (IN / "article.pdf").read_bytes()
tex_bytes = (IN / "source.tex").read_bytes()
zip_bytes = (IN / "full_package.zip").read_bytes()
with zipfile.ZipFile(IN / "full_package.zip") as z:
    with fitz.open(stream=z.read(stem+".pdf"), filetype="pdf") as packaged_pdf:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as standalone_pdf:
            assert len(packaged_pdf) == len(standalone_pdf) == 23, "Packaged PDF page count differs"
            assert all(
                " ".join(packaged_pdf[i].get_text().split()) == " ".join(standalone_pdf[i].get_text().split())
                for i in range(23)
            ), "Packaged PDF content differs from approved standalone PDF"
    assert z.read(stem+".tex") == tex_bytes, "ZIP TeX differs from approved TeX"
doc = fitz.open(stream=pdf_bytes, filetype="pdf")
assert len(doc) == 23, f"Expected 23 pages, got {len(doc)}"
assert all(p.get_text().strip() for p in doc), "Unreadable PDF page"
norm = lambda text: " ".join(text.split())
assert quote in norm(doc[8].get_text()), "Card quotation not on page 9"
full_text = " ".join(norm(p.get_text()) for p in doc)
for needle in ("FRSA-1", "FRSA-8", "Relative", "ZFC", "historical", "provisional"):
    assert needle.lower() in full_text.lower(), f"Missing expected concept: {needle}"

for dest in (ROOT / "docs" / slug, ROOT / slug):
    dest.mkdir(parents=True, exist_ok=True)
    (dest / (stem + ".pdf")).write_bytes(pdf_bytes)
    (dest / "source.tex").write_bytes(tex_bytes)
    (dest / pkg_name).write_bytes(zip_bytes)

catalog = ROOT / "scripts/publications.json"
data = json.loads(catalog.read_text(encoding="utf-8"))
prior = [item for item in data["items"] if item.get("id") != slug]
old_ids = [item["id"] for item in prior]
new_order = min([item.get("order",0) for item in prior if isinstance(item.get("order"),int)] + [0]) - 1
card = {
    "id": slug,
    "href": slug + "/",
    "title": title,
    "kind": "Research paper",
    "subject": SUBJECT,
    "pdf": slug + "/" + stem + ".pdf",
    "archive_path": slug + "/" + stem + ".pdf",
    "source": slug + "/source.html",
    "source_file": slug + "/source.tex",
    "source_package": slug + "/" + pkg_name,
    "sha256": hashes["article.pdf"],
    "sha256_tex": hashes["source.tex"],
    "pages": 23,
    "order": new_order,
    "authors": "Brian Tenneson",
    "quote": quote,
    "quote_page": 9,
    "card_quote": quote,
    "card_quote_attribution": "Brian Tenneson, ATLAS-repaired Version 0.3, p. 9",
    "quote_also_on_card": True,
    "card_text": "A 23-page research article defining eight operational axioms of formal reflective self-awareness (FRSA-1 through FRSA-8), presenting a finite verifier-gated witness and a ZFC relative-consistency argument, and distinguishing the reproducible new certificate example from the original September 2026 experiment.",
    "status": "ATLAS-REPAIRED RESEARCH DRAFT V0.3 · 20 OCTOBER 2026. Finite witness independently replay-checked; existence argument not proof-assistant certified; original historical execution remains provisional. No consciousness claim.",
    "classification_note": "Includes exact approved PDF and LaTeX plus a complete verifier-witness package. The recorded eight-check pass and negative-test results concern the new finite construction, not independent verification of the original 29 September 2026 run."
}
data["items"] = [card] + prior
catalog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
assert [x["id"] for x in data["items"][1:]] == old_ids, "Original cards rearranged"
subprocess.run(["python","scripts/build_publications_106.py"],cwd=ROOT,check=True)
search = json.loads((ROOT/"docs/search-index.json").read_text(encoding="utf-8"))
assert search["items"][0]["id"] == slug, "Slot 1 not attained"
index = (ROOT/"docs/index.html").read_text(encoding="utf-8")
first_card = index.split('<article class="card"',1)[1].split("</article>",1)[0]
assert title in first_card and quote in first_card
dest = ROOT/"docs"/slug
for f in ("index.html","source.html","source.tex",stem+".pdf",pkg_name):
    assert (dest/f).is_file(), "Missing output "+f
assert (dest/"source.tex").read_bytes() == tex_bytes
assert (dest/(stem+".pdf")).read_bytes() == pdf_bytes
assert (dest/pkg_name).read_bytes() == zip_bytes
print("PASS: VGPSA v0.3 published in slot 1, approved standalone PDF, source, and original ZIP checksummed, every prior card retains relative order.")
audit=subprocess.run(["python","scripts/audit_subject_catalog_106.py"],cwd=ROOT,capture_output=True,text=True)
if audit.returncode:
    print("WARNING: Whole-site audit failed; inspect output. New article and slot checks passed.")
    print(audit.stderr[-2500:])
else:
    print(audit.stdout)
