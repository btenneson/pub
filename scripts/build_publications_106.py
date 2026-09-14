#!/usr/bin/env python3
"""Build the publication site with reviewed historical catalog-context aliases.

The canonical publication catalog remains scripts/publications.json. Historical
contexts in scripts/publication_aliases.json get their own reader/card while
reusing the already-verified canonical document. No duplicate PDF is created.
"""
from pathlib import Path
import html
import json
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CATALOG = ROOT / "scripts" / "publications.json"
ALIASES = ROOT / "scripts" / "publication_aliases.json"
BUILDER = ROOT / "scripts" / "build_publications.py"

MOBILE_READER_CSS = r""".reader-note{margin:.8rem 0 0;padding:.7rem .85rem;border:1px solid var(--line);border-radius:8px;background:var(--tint);color:var(--muted)}@media(max-width:800px){.reader-frame{height:72vh;min-height:440px}}@media(max-width:480px){.reader-frame{height:66vh;min-height:390px}}"""

PDF_READER_HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PDF reader</title><style>*{box-sizing:border-box}body{margin:0;background:#3f454b;color:#111;font:16px/1.4 system-ui,-apple-system,Segoe UI,sans-serif}.toolbar{position:sticky;top:0;z-index:2;display:flex;align-items:center;justify-content:center;gap:.45rem;flex-wrap:wrap;padding:.5rem;background:#f6f7f8;border-bottom:1px solid #c9ced3}.toolbar button,.toolbar a{font:inherit;padding:.45rem .65rem;border:1px solid #aeb5bc;border-radius:7px;background:white;color:#17212b;text-decoration:none;cursor:pointer}.toolbar button:disabled{opacity:.45}.page-info{min-width:7.5rem;text-align:center}.stage{min-height:calc(100vh - 58px);display:flex;justify-content:center;align-items:flex-start;padding:18px}.stage canvas{display:block;max-width:100%;height:auto;background:white;box-shadow:0 2px 14px #0007}.status{max-width:48rem;margin:3rem auto;padding:1rem;background:white;border-radius:8px}.status[hidden]{display:none}@media(max-width:560px){.toolbar{gap:.3rem;padding:.4rem}.toolbar button,.toolbar a{padding:.42rem .55rem}.stage{padding:8px}}@media(prefers-color-scheme:dark){.toolbar{background:#20262c;border-color:#46505a}.toolbar button,.toolbar a{background:#303941;color:#f3f6f8;border-color:#65717c}.page-info{color:#f3f6f8}} </style></head><body><div class="toolbar"><button id="prev" type="button" aria-label="Previous page">‹ Prev</button><span class="page-info" id="pageInfo">Loading…</span><button id="next" type="button" aria-label="Next page">Next ›</button><button id="zoomOut" type="button" aria-label="Zoom out">−</button><button id="zoomIn" type="button" aria-label="Zoom in">+</button><a id="openPdf" target="_blank" rel="noopener">Open PDF</a></div><div class="stage"><canvas id="page"></canvas><div class="status" id="status" hidden></div></div><script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script><script src="/pub/pdf-reader.js"></script></body></html>'''

PDF_READER_JS = r'''(()=>{const params=new URLSearchParams(location.search);const file=params.get('file');const status=document.getElementById('status');const canvas=document.getElementById('page');const pageInfo=document.getElementById('pageInfo');const prev=document.getElementById('prev');const next=document.getElementById('next');const zoomIn=document.getElementById('zoomIn');const zoomOut=document.getElementById('zoomOut');const openPdf=document.getElementById('openPdf');let pdf=null,pageNum=1,scale=1.25,rendering=false,pending=null;function fail(msg){status.hidden=false;status.textContent=msg;canvas.hidden=true;pageInfo.textContent='Reader unavailable';prev.disabled=next.disabled=zoomIn.disabled=zoomOut.disabled=true}if(!file||!file.startsWith('/pub/')||!file.toLowerCase().includes('.pdf')){fail('Invalid PDF address.');return}openPdf.href=file;if(!window.pdfjsLib){fail('The document reader could not load. Use Open PDF above.');return}pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';async function render(num){if(rendering){pending=num;return}rendering=true;try{const page=await pdf.getPage(num);const viewport=page.getViewport({scale});const ratio=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.floor(viewport.width*ratio);canvas.height=Math.floor(viewport.height*ratio);canvas.style.width=Math.floor(viewport.width)+'px';canvas.style.height=Math.floor(viewport.height)+'px';const ctx=canvas.getContext('2d');ctx.setTransform(ratio,0,0,ratio,0,0);await page.render({canvasContext:ctx,viewport}).promise;pageInfo.textContent=`Page ${pageNum} of ${pdf.numPages}`;prev.disabled=pageNum<=1;next.disabled=pageNum>=pdf.numPages}catch(e){fail('This PDF could not be rendered here. Use Open PDF above.')}finally{rendering=false;if(pending!==null){const p=pending;pending=null;render(p)}}}prev.onclick=()=>{if(pageNum>1){pageNum--;render(pageNum)}};next.onclick=()=>{if(pdf&&pageNum<pdf.numPages){pageNum++;render(pageNum)}};zoomIn.onclick=()=>{scale=Math.min(3,scale+.2);render(pageNum)};zoomOut.onclick=()=>{scale=Math.max(.5,scale-.2);render(pageNum)};pdfjsLib.getDocument(file).promise.then(doc=>{pdf=doc;render(pageNum)}).catch(()=>fail('This PDF could not be loaded in the reader. Use Open PDF above.'));})();'''

PDF_IFRAME = re.compile(r'(<iframe\s+class="reader-frame"\s+src=")([^"?]+\.pdf)("[^>]*></iframe>)', re.I)


def expanded_catalog():
    data = json.loads(CATALOG.read_text())
    base = data["items"]
    by_id = {x["id"]: x for x in base}
    aliases = json.loads(ALIASES.read_text())["items"]
    expanded = [dict(x) for x in base]
    for n, alias in enumerate(aliases):
        canonical_id = alias["canonical_id"]
        if canonical_id not in by_id:
            raise SystemExit(f"Alias canonical_id not found: {canonical_id}")
        canonical = by_id[canonical_id]
        x = dict(canonical)
        x["id"] = f"{canonical['subject']}/{alias['id_suffix']}"
        x["href"] = x["id"] + "/"
        x["title"] = alias["title"]
        x["kind"] = alias["kind"]
        x["catalog_alias_of"] = canonical_id
        x["archive_path"] = ""
        x["source_file"] = ""
        x["order"] = 2000 + n
        x["classification_note"] = (
            "Historical catalog context restored from the 106-item pre-migration "
            f"publication library. This card shares its verified document with “{canonical['title']}”."
        )
        expanded.append(x)
    out = dict(data)
    out["items"] = expanded
    return out


def install_pdf_reader():
    (DOCS / "pdf-reader.html").write_text(PDF_READER_HTML)
    (DOCS / "pdf-reader.js").write_text(PDF_READER_JS)
    changed = 0
    for reader_page in DOCS.glob("*/*/index.html"):
        source = reader_page.read_text(errors="replace")
        def repl(match):
            pdf_url = html.unescape(match.group(2))
            viewer = "/pub/pdf-reader.html?file=" + quote(pdf_url, safe="")
            return match.group(1) + viewer + match.group(3)
        repaired = PDF_IFRAME.sub(repl, source)
        if repaired != source:
            reader_page.write_text(repaired)
            changed += 1
    return changed


def main():
    original = CATALOG.read_bytes()
    try:
        expanded = expanded_catalog()
        if len(expanded["items"]) != 108:
            raise SystemExit(f"Expected 107 cards after restoration, got {len(expanded['items'])}")
        CATALOG.write_text(json.dumps(expanded, ensure_ascii=False, indent=2) + "\n")
        subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True)
        css_path = DOCS / "publications.css"
        css_path.write_text(css_path.read_text() + MOBILE_READER_CSS)
        changed = install_pdf_reader()
        print(f"Installed shared PDF.js reader in {changed} PDF publication pages.")
    finally:
        CATALOG.write_bytes(original)


if __name__ == "__main__":
    main()
