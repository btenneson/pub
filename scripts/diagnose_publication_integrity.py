#!/usr/bin/env python3
"""Non-mutating comprehensive diagnostic of publication PDFs and catalog links."""
import json, re, hashlib, html, unicodedata
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import fitz

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
INDEX=json.loads((DOCS/'search-index.json').read_text())
ITEMS=INDEX['items']

def norm(t):
    return re.sub(r'\s+', ' ',unicodedata.normalize('NFKC',t or '')).strip().replace('- ','')
def report(typ,title,**kw):
    issues.append(dict(type=typ,title=title,**kw))
class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v:self.links.append(v)

issues=[]; paths={DOCS/'index.html',DOCS/'404.html'}; byid={x['id']:x for x in ITEMS}
for x in ITEMS:
    title=x['title']; id=x['id']; pf=DOCS/x.get('pdf','') if x.get('pdf') else None
    reader=DOCS/x['href']/'index.html'
    paths.add(reader);paths.add(DOCS/x['subject']/'index.html')
    if not reader.is_file():report('missing_reader',title,path=str(reader));continue
    for key in ('source','source_file','download','text'):
        if x.get(key) and not (DOCS/x[key]).exists():report('missing_'+key,title,path=x[key])
    if not pf:continue
    if not pf.is_file():report('missing_pdf',title,path=x['pdf']);continue
    sha=hashlib.sha256(pf.read_bytes()).hexdigest()
    if sha!=x.get('sha256'):report('hash_mismatch',title,expected=x.get('sha256'),actual=sha)
    try:doc=fitz.open(pf)
    except Exception as e:report('unopenable_pdf',title,error=str(e));continue
    if not len(doc):report('empty_pdf',title);continue
    for n in range(len(doc)):
        if not doc[n].get_text().strip():report('empty_text_page',title,page=n+1)
    quote=norm(x.get('quote',''))
    qpage=x.get('quote_page')
    if not quote:
        report('missing_quote',title)
    else:
        allpages=[norm(p.get_text()) for p in doc]
        matches=[n+1 for n,t in enumerate(allpages) if quote in t]
        if not qpage or not 1<=qpage<=len(doc):
            report('invalid_quote_page',title,quote=x.get('quote',''),quote_page=qpage,matching_pages=matches,source_pages=len(doc))
        elif quote not in allpages[qpage-1]:
            report('quote_text_mismatch',title,quote=x.get('quote',''),quote_page=qpage,matching_pages=matches,first_page_text=allpages[qpage-1][:380])
    doc.close()
for p in paths:
    if not p.is_file():report('missing_html',str(p.relative_to(ROOT)));continue
    l=Links()
    try:l.feed(p.read_text())
    except Exception as e:report('unparseable_html',str(p.relative_to(ROOT)),error=str(e));continue
    for link in l.links:
        u=urlsplit(link)
        if u.scheme or u.netloc or not u.path:continue
        path=unquote(u.path)
        tgt=(DOCS/path[len('/pub/'):]) if path.startswith('/pub/') else p.parent/path
        if tgt.is_dir():tgt=tgt/'index.html'
        if not tgt.exists():report('broken_local_link',str(p.relative_to(ROOT)),link=link)
print('LIBRARY-AUDIT',json.dumps({'entries':len(ITEMS),'pdf_entries':sum(bool(x.get('pdf')) for x in ITEMS),'failures':len(issues)},ensure_ascii=False))
for issue in issues:print('LIBRARY-ISSUE',json.dumps(issue,ensure_ascii=False))
