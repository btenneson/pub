#!/usr/bin/env python3
"""Build the publication site with reviewed historical catalog-context aliases.

The canonical publication catalog remains scripts/publications.json. Historical
contexts in scripts/publication_aliases.json get their own reader/card while
reusing the already-verified canonical document. No duplicate PDF is created.
"""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CATALOG = ROOT / "scripts" / "publications.json"
ALIASES = ROOT / "scripts" / "publication_aliases.json"
BUILDER = ROOT / "scripts" / "build_publications.py"

# Keep the catalog's primary Read action independent of fragile embedded-PDF
# iframe behavior. Publication detail pages remain available through titles,
# while the Read button uses the browser's native direct-PDF viewer.
RELIABLE_PUBLICATIONS_JS = r"""const q=document.getElementById('q'),kind=document.getElementById('kind'),cat=document.getElementById('cat'),sort=document.getElementById('sort'),grid=document.getElementById('grid');const cards=[...grid.children];const norm=s=>s.normalize('NFKD').toLowerCase();function makePdfReadsReliable(){for(const c of cards){const downloads=[...c.querySelectorAll('.links a[download]')];const pdf=downloads.find(a=>/\.pdf(?:$|[?#])/i.test(a.getAttribute('href')||''));if(!pdf)continue;const read=[...c.querySelectorAll('.links a')].find(a=>a.textContent.trim()==='Read');if(read){read.href=pdf.href;read.textContent='Read PDF';read.removeAttribute('download');read.setAttribute('aria-label','Read PDF directly');}}}function render(){let tokens=norm(q.value).trim().split(/\s+/).filter(Boolean),n=0;for(const c of cards){c.hidden=!(tokens.every(t=>norm(c.textContent).includes(t))&&(!kind.value||c.dataset.kind===kind.value)&&(!cat.value||c.dataset.subject===cat.value));if(!c.hidden)n++}const ordered=[...cards];if(sort.value==='title')ordered.sort((a,b)=>a.dataset.title.localeCompare(b.dataset.title));if(sort.value==='subject')ordered.sort((a,b)=>a.dataset.subject.localeCompare(b.dataset.subject)||a.dataset.title.localeCompare(b.dataset.title));ordered.forEach(c=>grid.appendChild(c));document.getElementById('count').textContent=n+' of '+cards.length+' publications';document.getElementById('empty').hidden=n!==0;}[q,kind,cat,sort].forEach(e=>e.addEventListener(e===q?'input':'change',render));document.getElementById('clear').onclick=()=>{q.value='';kind.value='';cat.value='';sort.value='default';render();q.focus()};makePdfReadsReliable();render();"""

MOBILE_READER_CSS = r""".reader-note{margin:.8rem 0 0;padding:.7rem .85rem;border:1px solid var(--line);border-radius:8px;background:var(--tint);color:var(--muted)}@media(max-width:800px){.reader-header .fullscreen-reader{display:none}.reader-header .links a.open-pdf{font-weight:800}.reader-frame{height:68vh;min-height:420px}.reader-header:has(+ .reader-frame)::after{content:'If the embedded PDF is blank or unresponsive on this device, use Open PDF or Download PDF above.';display:block;margin-top:.8rem;padding:.7rem .85rem;border:1px solid var(--line);border-radius:8px;background:var(--tint);color:var(--muted);font-size:.92rem}}@media(max-width:480px){.reader-frame{height:58vh;min-height:360px}}"""

PDF_DOWNLOAD = re.compile(r'<a href="([^"]+\.pdf)" download>Download PDF</a>', re.I)


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
        # Reuse the canonical PDF/source. Do not copy a historical binary back.
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


def preserve_reader_fallbacks():
    css_path = DOCS / "publications.css"
    css = css_path.read_text()
    if "reader-header:has(+ .reader-frame)::after" not in css:
        css_path.write_text(css + MOBILE_READER_CSS)

    for reader_page in DOCS.glob("*/*/index.html"):
        text = reader_page.read_text(errors="replace")
        if "reader-frame" not in text or "Download PDF" not in text or "class=\"open-pdf\"" in text:
            continue
        repaired = PDF_DOWNLOAD.sub(
            r'<a class="open-pdf" href="\1" target="_blank" rel="noopener">Open PDF</a>'
            r'<a href="\1" download>Download PDF</a>',
            text,
            count=1,
        )
        if repaired != text:
            reader_page.write_text(repaired)


def main():
    original = CATALOG.read_bytes()
    try:
        expanded = expanded_catalog()
        if len(expanded["items"]) != 107:
            raise SystemExit(f"Expected 107 cards after restoration, got {len(expanded['items'])}")
        CATALOG.write_text(json.dumps(expanded, ensure_ascii=False, indent=2) + "\n")
        subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True)
        (DOCS / "publications.js").write_text(RELIABLE_PUBLICATIONS_JS)
        preserve_reader_fallbacks()
    finally:
        CATALOG.write_bytes(original)


if __name__ == "__main__":
    main()
