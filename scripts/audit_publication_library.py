#!/usr/bin/env python3
"""Audit publication archive and Pages reader/index invariants."""
from __future__ import annotations
import html,json,re,sys
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'; PAPERS=DOCS/'papers'; INDEX=DOCS/'search-index.json'
RAW_PREFIX='https://raw.githubusercontent.com/btenneson/pub/main/'
BLOB_PREFIX='https://github.com/btenneson/pub/blob/main/'
errors=[]; warnings=[]

def err(x): errors.append(x)
def warn(x): warnings.append(x)
def clean(s): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s))).strip()

def extract_pdf(text):
    for pat in (r"const\s+p\s*=\s*['\"]([^'\"]+\.pdf)['\"]",r'(https://raw\.githubusercontent\.com/btenneson/pub/main/[^\"\'<>\s]+\.pdf)'):
        m=re.search(pat,text,re.I)
        if m:return html.unescape(m.group(1))
    return ''

def repo_path_from_url(url,prefix):
    if not url.startswith(prefix):return None
    rel=unquote(url[len(prefix):].split('#',1)[0].split('?',1)[0]); return ROOT/rel

def local_href_exists(href):
    href=href.split('#',1)[0].split('?',1)[0]
    if not href or href.startswith(('http://','https://','mailto:')):return True
    p=DOCS/unquote(href)
    if p.is_dir():p=p/'index.html'
    return p.exists()

def is_redirect(text):
    return bool(re.search(r'http-equiv=[\'\"]refresh[\'\"]|location\.replace\(',text,re.I))

def is_nonpdf_reader(text):
    # Explicit publication readers that intentionally render repository text/Markdown.
    return bool(re.search(r'\.md[\'\"]|fulltext-\d+\.txt|<pre\b',text,re.I))

def active_pdf_readers():
    out={}
    if not PAPERS.exists(): err('docs/papers is missing'); return out
    for folder in sorted(p for p in PAPERS.iterdir() if p.is_dir()):
        page=folder/'index.html'
        if not page.exists(): warn(f'reader directory lacks index.html: {folder.relative_to(ROOT)}'); continue
        text=page.read_text(encoding='utf-8',errors='replace')
        if re.search(r'\bsuperseded\s+by\b',clean(text),re.I) or is_redirect(text): continue
        pdf=extract_pdf(text)
        if not pdf:
            if is_nonpdf_reader(text): continue
            err(f'active reader exposes neither PDF nor recognized full-text source: {page.relative_to(ROOT)}'); continue
        if not pdf.startswith(RAW_PREFIX): warn(f'active reader PDF is external rather than archive-local: {page.relative_to(ROOT)} -> {pdf}')
        else:
            target=repo_path_from_url(pdf,RAW_PREFIX)
            if target is None or not target.exists(): err(f'reader PDF target missing: {page.relative_to(ROOT)} -> {pdf}')
        for src in re.findall(r'https://github\.com/btenneson/pub/blob/main/[^\"\'<>\s]+\.tex',text,re.I):
            target=repo_path_from_url(html.unescape(src),BLOB_PREFIX)
            if target is not None and not target.exists(): err(f'reader source target missing: {page.relative_to(ROOT)} -> {src}')
        out[folder.name]={'page':page,'pdf':pdf}
    return out

def audit_search_index(readers):
    if not INDEX.exists(): err('docs/search-index.json is missing'); return
    try:data=json.loads(INDEX.read_text(encoding='utf-8'))
    except Exception as exc: err(f'docs/search-index.json is invalid JSON: {exc}'); return
    if data.get('schema_version')!=1:err('search-index schema_version must be 1')
    items=data.get('items') or []
    if data.get('count')!=len(items):err('search-index count does not equal len(items)')
    seen=set(); core_pdf_slugs=set()
    for item in items:
        href=str(item.get('href') or '')
        if href in seen:err(f'duplicate search-index href: {href}')
        seen.add(href)
        if not local_href_exists(href):err(f'search-index href does not resolve locally: {href}')
        if item.get('kind')=='Core paper':
            archive=str(item.get('archive_path') or ''); pdf=str(item.get('pdf') or '')
            # A Core paper may intentionally use an HTML/full-text reader with no PDF.
            if pdf or archive.lower().endswith('.pdf'):
                if not archive or not pdf:err(f'PDF-backed core item missing PDF metadata: {item.get("title")!r}')
                elif not (ROOT/unquote(archive)).exists():err(f'core search-index archive_path missing: {archive}')
                m=re.fullmatch(r'papers/([^/]+)/?',href)
                if m:core_pdf_slugs.add(m.group(1))
    missing=sorted(set(readers)-core_pdf_slugs); extra=sorted(core_pdf_slugs-set(readers))
    if missing:err('active PDF readers absent from search index: '+', '.join(missing))
    if extra:err('search index contains non-active/superseded PDF reader slugs: '+', '.join(extra))

def audit_ads():
    manifest=DOCS/'ADS'/'manifest.json'
    if not manifest.exists():warn('ADS manifest is absent');return
    try:data=json.loads(manifest.read_text(encoding='utf-8'))
    except Exception as exc:err(f'ADS manifest invalid JSON: {exc}');return
    for doc in data.get('documents',[]):
        web=str(doc.get('web_path') or '')
        if web and not (DOCS/'ADS'/unquote(web)).exists():err(f'ADS manifest web_path missing: {web}')

def main():
    for required in (DOCS/'.nojekyll',DOCS/'index.html',INDEX):
        if not required.exists():err(f'required publication-site file missing: {required.relative_to(ROOT)}')
    readers=active_pdf_readers(); audit_search_index(readers); audit_ads()
    print(f'active canonical PDF readers: {len(readers)}'); print(f'warnings: {len(warnings)}')
    for x in warnings:print('WARNING:',x)
    print(f'errors: {len(errors)}')
    for x in errors:print('ERROR:',x)
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
