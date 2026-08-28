#!/usr/bin/env python3
"""Mirror repository-root pub.experimental into docs/pub.experimental for GitHub Pages.

The source archive remains pub.experimental/. GitHub Pages publishes docs/, so
this script copies the exact file bytes into the Pages tree and builds a landing
page that deliberately matches the main publication-library interface.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pub.experimental"
DEST = ROOT / "docs" / "pub.experimental"
BRAINSTORMING_NAME = "BRAINSTORMING-the_creativity_knobs_limits_natures_for_an_ATP.pdf"

STYLE = r"""
:root{color-scheme:light dark;--bg:#f7f8fa;--panel:#fff;--text:#18212b;--muted:#5b6773;--line:#d7dde4;--accent:#245d83;--accent2:#eaf3f8;--shadow:0 5px 22px rgba(25,42,55,.07)}
@media(prefers-color-scheme:dark){:root{--bg:#11161b;--panel:#182028;--text:#eef4f8;--muted:#aab6c0;--line:#33414c;--accent:#7fc3ef;--accent2:#1d3341;--shadow:none}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}a{color:var(--accent)}main{max-width:1180px;margin:auto;padding:24px}.hero{padding:18px 0 12px}.hero h1{margin:.1em 0;font-size:clamp(1.8rem,4vw,3rem);letter-spacing:-.03em}.hero p{max-width:860px;color:var(--muted)}.toplinks{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0 20px}.searchbox{position:sticky;top:0;z-index:3;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(10px);padding:12px 0;border-bottom:1px solid var(--line)}.controls{display:grid;grid-template-columns:minmax(230px,2fr) repeat(2,minmax(130px,1fr));gap:10px}.controls input,.controls select,.controls button{width:100%;font:inherit;padding:11px 12px;border:1px solid var(--line);border-radius:10px;background:var(--panel);color:var(--text)}.controls button{cursor:pointer}.summary{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:var(--muted);margin:14px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:14px}.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:15px;box-shadow:var(--shadow);display:flex;flex-direction:column;min-height:190px}.card h2{font-size:1.05rem;line-height:1.3;margin:0 0 9px}.meta{font-size:.86rem;color:var(--muted);margin-bottom:10px}.tags{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 12px}.tag{font-size:.75rem;padding:3px 7px;border-radius:999px;background:var(--accent2);color:var(--text)}.links{display:flex;gap:12px;flex-wrap:wrap;margin-top:auto}.links a{font-weight:600;text-decoration:none}.empty{padding:32px;border:1px dashed var(--line);border-radius:14px;color:var(--muted)}footer{margin:30px 0 10px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}@media(max-width:800px){main{padding:16px}.controls{grid-template-columns:1fr 1fr}.controls input{grid-column:1/-1}}@media(max-width:480px){.controls{grid-template-columns:1fr}.controls input{grid-column:auto}}
"""


def included(path: Path) -> bool:
    rel = path.relative_to(SOURCE)
    return not any(part.startswith(".") or part.startswith("_") for part in rel.parts)


def title_for(rel: Path) -> str:
    if rel.name == BRAINSTORMING_NAME:
        return "BRAINSTORMING — the creativity knob(s)/limits/natures for an ATP"
    stem = unquote(rel.stem)
    stem = re.sub(r"[_]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or rel.name


def type_for(rel: Path) -> str:
    ext = rel.suffix.lower().lstrip(".")
    return {
        "pdf": "PDF",
        "md": "Markdown",
        "tex": "LaTeX source",
        "txt": "Text",
        "py": "Python",
        "html": "HTML",
    }.get(ext, ext.upper() if ext else "File")


def main() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)

    files: list[Path] = []
    if SOURCE.exists():
        for src in sorted(SOURCE.rglob("*"), key=lambda p: p.as_posix().casefold()):
            if not src.is_file() or not included(src):
                continue
            rel = src.relative_to(SOURCE)
            dst = DEST / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            files.append(rel)

    # README is etiquette/navigation rather than a publication card.
    card_files = [p for p in files if p.name not in {"README.md", "MANIFEST.json"}]
    card_files.sort(key=lambda p: (0 if p.name == BRAINSTORMING_NAME else 1, p.as_posix().casefold()))

    items = []
    for rel in card_files:
        href = quote(rel.as_posix(), safe="/")
        ext = rel.suffix.lower().lstrip(".") or "file"
        title = title_for(rel)
        file_type = type_for(rel)
        items.append({
            "title": title,
            "kind": "Experimental",
            "category": "Experimental research & working notes",
            "type": file_type,
            "tags": ["experimental", ext],
            "href": href,
            "path": rel.as_posix(),
            "search": " ".join([title, rel.as_posix(), file_type, "experimental working note"]),
        })

    data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    script = r"""
const DATA=__DATA__;
const q=document.getElementById('q'),typ=document.getElementById('typ'),sort=document.getElementById('sort'),clear=document.getElementById('clear'),grid=document.getElementById('grid'),count=document.getElementById('count');
const norm=s=>(s||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function populate(){const ts=[...new Set(DATA.map(x=>x.type))].sort();typ.innerHTML='<option value="">All file types</option>'+ts.map(x=>`<option>${esc(x)}</option>`).join('')}
function tokens(){return norm(q.value).trim().split(/\s+/).filter(Boolean)}
function hay(x){return norm([x.title,x.type,(x.tags||[]).join(' '),x.search,x.path].join(' '))}
function matches(x){const ts=tokens();if(!ts.every(t=>hay(x).includes(t)))return false;return !typ.value||x.type===typ.value}
function relevance(x){const ts=tokens(),title=norm(x.title),h=hay(x);let n=0;for(const t of ts){if(title===t)n+=100;if(title.startsWith(t))n+=60;if(title.includes(t))n+=40;else if(h.includes(t))n+=10}return n}
function card(x){const tags=(x.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join('');return `<article class="card"><h2>${esc(x.title)}</h2><div class="meta">Experimental · ${esc(x.type)}</div><div class="tags">${tags}</div><div class="links"><a href="${esc(x.href)}">Open</a></div></article>`}
function render(){let a=DATA.filter(matches),ts=tokens();if(ts.length)a.sort((x,y)=>relevance(y)-relevance(x)||x.title.localeCompare(y.title));else if(sort.value==='title')a.sort((x,y)=>x.title.localeCompare(y.title));else if(sort.value==='type')a.sort((x,y)=>x.type.localeCompare(y.type)||x.title.localeCompare(y.title));count.textContent=`${a.length} of ${DATA.length} items`;grid.innerHTML=a.length?a.map(card).join(''):'<div class="empty">No experimental items match that search.</div>';}
populate();[q,typ,sort].forEach(el=>el.addEventListener(el===q?'input':'change',render));clear.onclick=()=>{q.value='';typ.value='';sort.value='default';q.focus();render()};render();
""".replace("__DATA__", data)

    etiquette = '<a href="README.md">Experimental etiquette</a>' if (DEST / "README.md").exists() else ""
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Searchable experimental research and working-note library."><title>Brian Tenneson — pub.experimental</title><style>{STYLE}</style></head><body><main><section class="hero"><h1>Brian Tenneson — pub.experimental</h1><p>A searchable working wing for experimental research, drafts, exploratory notes, and provisional results. The standards here are intentionally less formal than the main publication library.</p><nav class="toplinks"><a href="../">Publication Library</a>{etiquette}<a href="https://github.com/btenneson/pub/tree/main/pub.experimental">Repository folder</a></nav></section><section class="searchbox"><div class="controls"><input id="q" type="search" placeholder="Search titles, topics, file names…" aria-label="Search experimental work"><select id="typ" aria-label="File type"></select><select id="sort" aria-label="Sort"><option value="default">Library order</option><option value="title">Title A–Z</option><option value="type">File type</option></select><button id="clear" type="button">Clear</button></div></section><div class="summary"><span id="count"></span><span>Experimental material may be rough, provisional, collaborative, or unattributed.</span></div><section id="grid" class="grid" aria-live="polite"></section><footer>Experimental archive mirrored from <code>pub.experimental</code>. The main publication library indexes these items as well.</footer></main><script>{script}</script></body></html>'''
    (DEST / "index.html").write_text(page, encoding="utf-8")
    print(f"mirrored {len(files)} experimental files and built {len(items)} library cards")


if __name__ == "__main__":
    main()
