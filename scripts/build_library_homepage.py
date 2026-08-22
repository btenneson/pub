#!/usr/bin/env python3
"""Rebuild docs/index.html and docs/search-index.json from published reader pages.

The builder is intentionally dependency-free so GitHub Actions can run it on every
publication change. Core papers are discovered from docs/papers/*/index.html.
Applied Data Science records are imported from docs/ADS/manifest.json.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAPERS = DOCS / "papers"
ADS_MANIFEST = DOCS / "ADS" / "manifest.json"
OUT_HTML = DOCS / "index.html"
OUT_JSON = DOCS / "search-index.json"


def clean_text(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def humanize_slug(s: str) -> str:
    words = re.sub(r"[_-]+", " ", s).split()
    return " ".join(w.upper() if w.lower() in {"ald", "atp", "data", "sat", "sic", "ads", "ml"} else w.capitalize() for w in words)


def category_for(title: str, slug: str) -> str:
    x = f"{title} {slug}".lower()
    if "external" in x or "survey" in x:
        return "External References"
    if "multi-dose" in x or "concentration" in x:
        return "Applied Mathematics & Modeling"
    if "surjection" in x or "number theory" in x:
        return "Mathematics"
    if "sat" in x or "complexity" in x:
        return "Complexity & SAT"
    if any(k in x for k in ("logical decider", "logic decider", "ald", "notald", "conjecture settling")):
        return "Logical Deciders"
    if any(k in x for k in ("self-awareness", "self awareness", "depths of", "simulation", "semi-ideal", "sics")):
        return "Self-Awareness & Simulation"
    if any(k in x for k in ("proof compass", "proof-horizon", "proof horizon", "theorem prover", "theorem search", "theorem maze", "search dynamics", "data 2", "data 3", "data 4", "data-atp", "data_atp", "hilbert")):
        return "Automated Theorem Proving"
    return "Research Papers"


def extract_core() -> list[dict]:
    items: list[dict] = []
    if not PAPERS.exists():
        return items
    for folder in sorted(p for p in PAPERS.iterdir() if p.is_dir()):
        index = folder / "index.html"
        if not index.exists():
            continue
        text = index.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"<header[^>]*>.*?<b>(.*?)</b>", text, re.I | re.S)
        if not m:
            m = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
        title = clean_text(m.group(1)) if m else humanize_slug(folder.name)
        pdf_m = re.search(r"const\s+p\s*=\s*['\"]([^'\"]+\.pdf)['\"]", text, re.I)
        pdf = pdf_m.group(1) if pdf_m else ""
        archive_path = ""
        prefix = "https://raw.githubusercontent.com/btenneson/pub/main/"
        if pdf.startswith(prefix):
            archive_path = pdf[len(prefix):]
        category = category_for(title, folder.name)
        items.append({
            "title": title,
            "kind": "Core paper",
            "category": category,
            "tags": [],
            "href": f"papers/{folder.name}/",
            "pdf": pdf,
            "source": f"https://github.com/btenneson/pub/tree/main/{archive_path.rsplit('/', 1)[0]}" if archive_path and "/" in archive_path else "",
            "archive_path": archive_path,
            "search": " ".join([title, category, folder.name, archive_path]),
        })
    return items


def nicer_ads_title(doc: dict) -> str:
    title = str(doc.get("title") or "").strip()
    bad = title.lower().startswith("oversight to perform data analysis") or title.lower() in {"final report"}
    if title and not bad:
        return title
    path = str(doc.get("web_path") or doc.get("local_path") or "")
    stem = Path(path).stem
    stem = re.sub(r"(?i)tenneson", "", stem)
    stem = re.sub(r"[_-]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    stem = re.sub(r"(?i)\bads\b", "ADS", stem)
    stem = re.sub(r"(?i)\bhomework\s+(\d+)\b", r"Homework \1", stem)
    stem = re.sub(r"(?i)\bversion\s+(\d+)\b", r"Version \1", stem)
    stem = re.sub(r"(?i)\bfinal report\b", "Final Report", stem)
    return stem or title or "Applied Data Science document"


def extract_ads() -> list[dict]:
    if not ADS_MANIFEST.exists():
        return []
    data = json.loads(ADS_MANIFEST.read_text(encoding="utf-8"))
    items: list[dict] = []
    for doc in data.get("documents", []):
        title = nicer_ads_title(doc)
        category = f"ADS — {doc.get('category', 'Applied Data Science')}"
        tags = [str(x) for x in doc.get("tags", [])]
        web_path = str(doc.get("web_path") or "")
        sources = doc.get("sources") or []
        source = str(sources[0].get("html_url") or "") if sources else ""
        source_path = str(sources[0].get("path") or "") if sources else ""
        items.append({
            "title": title,
            "kind": "Applied Data Science",
            "category": category,
            "tags": tags,
            "href": f"ADS/{web_path}",
            "pdf": "",
            "source": source,
            "archive_path": str(doc.get("local_path") or ""),
            "search": " ".join([title, category, " ".join(tags), web_path, source_path, "applied data science ADS"]),
        })
    return items


STYLE = r"""
:root{color-scheme:light dark;--bg:#f7f8fa;--panel:#fff;--text:#18212b;--muted:#5b6773;--line:#d7dde4;--accent:#245d83;--accent2:#eaf3f8;--shadow:0 5px 22px rgba(25,42,55,.07)}
@media(prefers-color-scheme:dark){:root{--bg:#11161b;--panel:#182028;--text:#eef4f8;--muted:#aab6c0;--line:#33414c;--accent:#7fc3ef;--accent2:#1d3341;--shadow:none}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}a{color:var(--accent)}main{max-width:1180px;margin:auto;padding:24px}.hero{padding:18px 0 12px}.hero h1{margin:.1em 0;font-size:clamp(1.8rem,4vw,3rem);letter-spacing:-.03em}.hero p{max-width:860px;color:var(--muted)}.toplinks{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0 20px}.searchbox{position:sticky;top:0;z-index:3;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(10px);padding:12px 0;border-bottom:1px solid var(--line)}.controls{display:grid;grid-template-columns:minmax(230px,2fr) repeat(3,minmax(130px,1fr));gap:10px}.controls input,.controls select,.controls button{width:100%;font:inherit;padding:11px 12px;border:1px solid var(--line);border-radius:10px;background:var(--panel);color:var(--text)}.controls button{cursor:pointer}.summary{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:var(--muted);margin:14px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:14px}.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:15px;box-shadow:var(--shadow);display:flex;flex-direction:column;min-height:190px}.card h2{font-size:1.05rem;line-height:1.3;margin:0 0 9px}.meta{font-size:.86rem;color:var(--muted);margin-bottom:10px}.tags{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 12px}.tag{font-size:.75rem;padding:3px 7px;border-radius:999px;background:var(--accent2);color:var(--text)}.links{display:flex;gap:12px;flex-wrap:wrap;margin-top:auto}.links a{font-weight:600;text-decoration:none}.empty{padding:32px;border:1px dashed var(--line);border-radius:14px;color:var(--muted)}footer{margin:30px 0 10px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}@media(max-width:800px){main{padding:16px}.controls{grid-template-columns:1fr 1fr}.controls input{grid-column:1/-1}.searchbox{top:0}.card{min-height:0}}@media(max-width:480px){.controls{grid-template-columns:1fr}.controls input{grid-column:auto}}
"""

SCRIPT = r"""
const DATA=__DATA__;
const q=document.getElementById('q'),kind=document.getElementById('kind'),cat=document.getElementById('cat'),sort=document.getElementById('sort'),clear=document.getElementById('clear'),grid=document.getElementById('grid'),count=document.getElementById('count');
const norm=s=>(s||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
function populate(){const ks=[...new Set(DATA.map(x=>x.kind))].sort(),cs=[...new Set(DATA.map(x=>x.category))].sort();kind.innerHTML='<option value="">All collections</option>'+ks.map(x=>`<option>${esc(x)}</option>`).join('');cat.innerHTML='<option value="">All subjects</option>'+cs.map(x=>`<option>${esc(x)}</option>`).join('')}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function tokens(){return norm(q.value).trim().split(/\s+/).filter(Boolean)}
function haystack(x){return norm([x.title,x.kind,x.category,(x.tags||[]).join(' '),x.search,x.archive_path].join(' '))}
function matches(x){const toks=tokens(),textok=toks.every(t=>haystack(x).includes(t));if(!textok)return false;if(toks.length)return true;return (!kind.value||x.kind===kind.value)&&(!cat.value||x.category===cat.value)}
function relevance(x){const toks=tokens(),title=norm(x.title),hay=haystack(x);let s=0;for(const t of toks){if(title===t)s+=100;if(title.startsWith(t))s+=60;if(title.includes(t))s+=40;else if(hay.includes(t))s+=10}return s}
function render(){let a=DATA.filter(matches),toks=tokens();if(toks.length)a.sort((x,y)=>relevance(y)-relevance(x)||x.title.localeCompare(y.title));else if(sort.value==='title')a.sort((x,y)=>x.title.localeCompare(y.title));else if(sort.value==='subject')a.sort((x,y)=>x.category.localeCompare(y.category)||x.title.localeCompare(y.title));else a.sort((x,y)=>(x.kind==='Core paper'?0:1)-(y.kind==='Core paper'?0:1)||x.title.localeCompare(y.title));count.textContent=`${a.length} of ${DATA.length} items`;grid.innerHTML=a.length?a.map(card).join(''):'<div class="empty">No publications match that search.</div>';const u=new URL(location);q.value?u.searchParams.set('q',q.value):u.searchParams.delete('q');if(!toks.length){kind.value?u.searchParams.set('kind',kind.value):u.searchParams.delete('kind');cat.value?u.searchParams.set('category',cat.value):u.searchParams.delete('category')}else{u.searchParams.delete('kind');u.searchParams.delete('category')}history.replaceState(null,'',u)}
function card(x){const tags=(x.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join('');const secondary=x.pdf?`<a href="${esc(x.pdf)}">PDF</a>`:'';const source=x.source?`<a href="${esc(x.source)}">GitHub source</a>`:'';return `<article class="card"><h2>${esc(x.title)}</h2><div class="meta">${esc(x.kind)} · ${esc(x.category)}</div>${tags?`<div class="tags">${tags}</div>`:''}<div class="links"><a href="${esc(x.href)}">${x.kind==='Core paper'?'Read':'Open'}</a>${secondary}${source}</div></article>`}
populate();const u=new URL(location),uq=u.searchParams.get('q'),uk=u.searchParams.get('kind'),uc=u.searchParams.get('category');if(uq)q.value=uq;if(uk&&[...kind.options].some(o=>o.value===uk))kind.value=uk;if(uc&&[...cat.options].some(o=>o.value===uc))cat.value=uc;[q,kind,cat,sort].forEach(el=>el.addEventListener(el===q?'input':'change',render));clear.onclick=()=>{q.value='';kind.value='';cat.value='';sort.value='default';q.focus();render()};render();
"""


def build_html(items: list[dict]) -> str:
    data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    script = SCRIPT.replace("__DATA__", data)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Searchable publication library for Brian Tenneson's research papers and applied data-science work."><title>Brian Tenneson — Publication Library</title><style>{STYLE}</style></head>
<body><main><section class="hero"><h1>Brian Tenneson — Publication Library</h1><p>A searchable index of the core research-paper library and the Applied Data Science wing. Search matches titles, subjects, tags, and archive paths. Core paper links use browser-reader pages designed to work on phones as well as desktops.</p><nav class="toplinks"><a href="ADS/">Applied Data Science wing</a><a href="ADS/MANIFEST.md">ADS manifest</a><a href="PERMALINK_POLICY.md">Permalink policy</a><a href="https://github.com/btenneson/pub">GitHub archive</a></nav></section><section class="searchbox" aria-label="Library search"><div class="controls"><input id="q" type="search" autocomplete="off" placeholder="Search titles, topics, tags, paths…" aria-label="Search publications"><select id="kind" aria-label="Collection"></select><select id="cat" aria-label="Subject"></select><select id="sort" aria-label="Sort"><option value="default">Library order</option><option value="title">Title A–Z</option><option value="subject">Subject</option></select><button id="clear" type="button">Clear</button></div></section><div class="summary"><span id="count"></span><span>Text search is global; collection and subject filters apply when the search box is empty.</span></div><section id="grid" class="grid" aria-live="polite"></section><footer>Index generated from <code>docs/papers</code> and <code>docs/ADS/manifest.json</code>. New reader pages are included automatically by the rebuild workflow.</footer></main><script>{script}</script></body></html>'''


def main() -> int:
    items = extract_core() + extract_ads()
    items.sort(key=lambda x: (0 if x["kind"] == "Core paper" else 1, x["title"].casefold()))
    OUT_JSON.write_text(json.dumps({"schema_version": 1, "count": len(items), "items": items}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_HTML.write_text(build_html(items), encoding="utf-8")
    print(f"wrote {OUT_HTML.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)} with {len(items)} searchable items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())