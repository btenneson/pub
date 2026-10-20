#!/usr/bin/env python3
"""Publish the DNI v0.2 provisional article and all supporting files at slot 1."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile
import shutil
import fitz

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "incoming_publications/dni_v0_2"
SUBJECT = "cs.LO_Logic_in_Computer_Science"
SLUG = SUBJECT + "/deterministic_nondeterministic_interfaces_provisional_v0_2"
DEST = ROOT / "docs" / SLUG
ARCHIVE = ROOT / SLUG
BUILD = ROOT / ".build/dni_v0_2_publication"
STEM = "PROVISIONAL- DNI_Deterministic_Nondeterministic_Interface_Theory_v0_2_ATLAS_Repaired"
RE_AUDIT = "ATLAS_DNI_v0_2_Reaudit_Report"
OLD = "DNI_Deterministic_Nondeterministic_Interface_Theory_v0_1"
OLD_AUDIT = "ATLAS_Audit_DNI_v0_1_Report"
PACKAGE = "DNI_v0_2_PROVISIONAL_LaTeX_PDF_and_All_Supporting_Files.zip"
TITLE = "PROVISIONAL — Deterministic–Nondeterministic Interfaces: Exact Realization, Finite-Resource Obstructions, and Common-Theory Compatibility"
QUOTE = "A possibility relation does not determine weights; this distinction will remain explicit."
SOURCES = [
    ("main.tex", STEM, ""),
    ("atlas_reaudit.tex", RE_AUDIT, "ATLAS_Reaudit/"),
    ("history_v01.tex", OLD, "History_v0_1/"),
    ("history_atlas_audit.tex", OLD_AUDIT, "History_v0_1/"),
]
BUILD.mkdir(parents=True, exist_ok=True)
DEST.mkdir(parents=True, exist_ok=True)
ARCHIVE.mkdir(parents=True, exist_ok=True)
outputs = []
for input_name, stem, prefix in SOURCES:
    src = IN / input_name
    assert src.is_file(), str(src)
    tex = BUILD / (stem + ".tex")
    shutil.copyfile(src, tex)
    for _ in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                        "-file-line-error", tex.name],
                       cwd=BUILD, check=True, stdout=subprocess.DEVNULL)
    pdf = BUILD / (stem + ".pdf")
    assert pdf.is_file() and pdf.stat().st_size > 10000
    with fitz.open(pdf) as doc:
        expected = 8 if stem in (STEM, OLD) else 3
        assert len(doc) == expected, (stem, len(doc), expected)
        assert all(p.get_text().strip() for p in doc), "Unreadable page: " + stem
        if stem == STEM:
            assert QUOTE in " ".join(doc[0].get_text().split()), "Card quote not on page 1"
            main_pages = len(doc)
    outputs.append((prefix, tex, pdf))
main_pdf = BUILD / (STEM + ".pdf")
main_tex = BUILD / (STEM + ".tex")
for folder in (DEST, ARCHIVE):
    shutil.copyfile(main_pdf, folder / main_pdf.name)
    shutil.copyfile(main_tex, folder / main_tex.name)
    shutil.copyfile(main_tex, folder / "source.tex")

# Supporting material is kept with the public reader and in the ZIP.
for _,tex,pdf in outputs[1:]:
    shutil.copyfile(tex, DEST / tex.name)
    shutil.copyfile(pdf, DEST / pdf.name)

support = [
    "DNI_v0_2_verification_checks.py",
    "DNI_v0_2_independent_four_state_check.py",
]
logs = []
for name in support:
    src = IN / name
    assert src.is_file()
    p = subprocess.run([sys.executable, str(src)],cwd=ROOT,
                       capture_output=True,text=True,check=True)
    logs.append((name.replace(".py","_output.txt"),p.stdout))

readme = (
    "DNI VERSION 0.2 - PROVISIONAL PUBLICATION PACKAGE\n"
    "Main paper: " + STEM + ".pdf and .tex\n"
    "Additional: ATLAS reaudit, Version 0.1 history, two verification scripts and outputs.\n"
    "The main PDF and main LaTeX filenames begin with the exact requested prefix PROVISIONAL- (including the following space).\n"
    "PDFs are freshly typeset from the supplied LaTeX sources for this site; therefore PDF binary hashes may differ from the earlier local files.\n"
    "Restricted scope: classical finite-state deterministic/possibilistic/Markov interfaces.\n"
    "The audited finite-state theorems do not establish a general physical unification, a universal theory-of-theories amalgam, or a novelty claim.\n"
)
zip_members = {}
for prefix, tex, pdf in outputs:
    zip_members[prefix+tex.name] = tex.read_bytes()
    zip_members[prefix+pdf.name] = pdf.read_bytes()
for name in support:
    zip_members["Verification/"+name] = (IN/name).read_bytes()
for name, output in logs:
    zip_members["Verification/"+name] = output.encode()
zip_members["README.txt"] = readme.encode()
manifest = "".join(hashlib.sha256(b).hexdigest()+"  "+name+"\n"
                   for name,b in sorted(zip_members.items()))
zip_members["MANIFEST.sha256"] = manifest.encode()
with zipfile.ZipFile(DEST/PACKAGE,"w",zipfile.ZIP_DEFLATED) as z:
    for name, blob in zip_members.items():
        z.writestr(name,blob)
with zipfile.ZipFile(DEST/PACKAGE) as z:
    assert z.testzip() is None and len(z.namelist()) == 14
    assert z.read(STEM+".tex") == main_tex.read_bytes()
    assert z.read(STEM+".pdf") == main_pdf.read_bytes()

catalog = ROOT/"scripts/publications.json"
data = json.loads(catalog.read_text(encoding="utf-8"))
old = [x for x in data["items"] if x.get("id") != SLUG]
old_ids = [x["id"] for x in old]
position = min([x.get("order",0) for x in old if isinstance(x.get("order"),int)]+[0])-1
card = {
    "id": SLUG,"href": SLUG+"/", "title":TITLE,
    "kind":"Research paper","subject":SUBJECT,
    "pdf":SLUG+"/"+STEM+".pdf",
    "archive_path":SLUG+"/"+STEM+".pdf",
    "source":SLUG+"/source.html",
    "source_file":SLUG+"/source.tex",
    "source_package":SLUG+"/"+PACKAGE,
    "sha256":hashlib.sha256(main_pdf.read_bytes()).hexdigest(),
    "sha256_tex":hashlib.sha256(main_tex.read_bytes()).hexdigest(),
    "pages":main_pages, "order":position, "authors":"Brian Tenneson",
    "quote":QUOTE,"quote_page":1,
    "card_quote":QUOTE,
    "card_quote_attribution":"Brian Tenneson, provisional DNI Version 0.2, p. 1",
    "quote_also_on_card":True,
    "card_text":"A provisional eight-page ATLAS-repaired working note developing exact deterministic–stochastic and deterministic–possibilistic interfaces, a finite-hidden-state existence and minimum-size characterization, examples, and obstructions. The downloadable source package includes the ATLAS reaudit, prior version, and finite verification scripts.",
    "status":"PRELIMINARY RELEASE · PROVISIONAL — ATLAS-REPAIRED VERSION 0.2 · 20 OCTOBER 2026. Finite classical scope; independent originality and general theory-of-theories compatibility are not established.",
    "classification_note":"Provisional working paper. The intertwining equations are attributed to the established Rogers–Pitman framework. The finite-state formal results are audited mathematically and computationally checked in finite cases, not proof-assistant certified."
}
data["items"] = [card]+old
assert [x["id"] for x in data["items"][1:]] == old_ids
catalog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
subprocess.run([sys.executable,"scripts/build_publications_106.py"],cwd=ROOT,check=True)
result = json.loads((ROOT/"docs/search-index.json").read_text())
assert result["items"][0]["id"] == SLUG, "Not slot #1"
index = (ROOT/"docs/index.html").read_text()
first = index.split('<article class="card"',1)[1].split("</article>",1)[0]
assert "PROVISIONAL" in first and QUOTE in first
for name in ("index.html","source.html","source.tex",STEM+".pdf",PACKAGE):
    assert (DEST/name).is_file(),name
print("PASS: DNI 0.2 published as PROVISIONAL slot #1; existing ordering unchanged.")
print("PASS: PDFs + TeX + verification scripts/outputs + historical audits in ZIP.")
