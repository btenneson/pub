#!/usr/bin/env python3
"""Publish the Atlas-audited Professor of Professors, using a static reader."""
import hashlib, html, json, os, re, shutil, subprocess
from pathlib import Path
from urllib.parse import quote
stage=Path('.build/professor-of-professors-001v2')
docs=Path('docs')
is_pub=os.environ['GITHUB_REPOSITORY'].lower().endswith('/pub')
repo=os.environ['GITHUB_REPOSITORY']
stem=['The_Professor_of_Professors_001v2']
hashes=['e7f86a1d36cd86ba427277ff256b233c8fe0dcb5c89b1b2b5237588e3a871da8']
titles=["The Professor of Professors"]
subtitles=["Probabilistic Partial Credit, Recursive Awareness, and the Oracle Limit"]
descs=["Recursive probabilistic partial credit, monotone expected squared-error ignorance, exact limiting grade recovery, and a halting-encoded noncomputable limit. Includes an exact finite Bayesian example comparing fresh evidence with redundant evidence. Conditional mathematical results; no deployed oracle or independent formal verification claimed."]
credit='Research Director: Brian Tenneson · Mathematical development: Picard–CIIP (ChatGPT conversational research protocol) · Internal audit: Atlas (ChatGPT research role)'
slugs=['the_professor_of_professors_001v2']
esc=html.escape
def write(p,s): p.write_text(s,encoding='utf-8')
def read(p): return p.read_text(encoding='utf-8')
def hashfile(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(*args,**kw): return subprocess.run(args,check=True,**kw)
def rel(p): return p.relative_to(docs).as_posix()
def relative(p,base): return os.path.relpath(p,base).replace(os.sep,'/')
records=[]
for i,s in enumerate(stem):
    source=stage/(s+'.tex')
    assert hashfile(source)==hashes[i], 'Audited source hash mismatch'
    run('latexmk','-pdf','-halt-on-error','-interaction=nonstopmode',s+'.tex',cwd=stage)
    pdf=stage/(s+'.pdf')
    assert pdf.read_bytes().startswith(b'%PDF-')
    info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
    count=int(re.search(r'^Pages:\s*(\d+)',info,re.M).group(1))
    assert count==12, f'Unexpected page count {count}'
    if is_pub:
        folder=docs/'cs.LO_Logic_in_Computer_Science'/slugs[i]
        page=folder/'index.html'
        images=folder/'pages'
    else:
        folder=docs/'library/01_Core_Theory/Picard'
        page=docs/(slugs[i]+'.html')
        images=docs/'assets'/slugs[i]
    folder.mkdir(parents=True,exist_ok=True)
    images.mkdir(parents=True,exist_ok=True)
    target=folder/pdf.name
    shutil.copyfile(pdf,target)
    shutil.copyfile(source,folder/source.name)
    run('pdftoppm','-r','130','-png',str(target),str(images/'page'))
    pngs=sorted(images.glob('page-*.png'))
    assert len(pngs)==count and all(p.stat().st_size>1000 and p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') for p in pngs)
    pdfhref=relative(target,page.parent)
    texhref=relative(folder/source.name,page.parent)
    back='/pub/' if is_pub else 'index.html'
    css='/pub/publications.css' if is_pub else 'assets/style.css'
    github=f'https://github.com/{repo}/blob/main/docs/{rel(target)}'
    nav=' '.join(f'<a href="#page-{n}">{n}</a>' for n in range(1,count+1))
    parts=[f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(titles[i])}</title><link rel="stylesheet" href="{css}"><style>main{{max-width:970px;margin:auto;padding:clamp(12px,3vw,30px)}}nav{{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}}nav a{{padding:.35rem .55rem}}.paper-page{{margin:2rem 0;border-top:1px solid #bbb;scroll-margin-top:1rem}}img{{display:block;width:100%;height:auto;border:1px solid #aaa;background:white}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:.95rem/1.5 ui-monospace,monospace}}a{{overflow-wrap:anywhere}}details{{margin:1rem 0}}.fallback{{font-size:.9rem}}</style></head><body><main><p><a href="{back}">Back to library</a></p><h1>{esc(titles[i])}</h1><h2>{esc(subtitles[i])}</h2><p>{esc(credit)}</p><p>Atlas audit · 26 November 2026 · {count} pages</p><p>{esc(descs[i])}</p><p>Internal mathematical review, not independent formal verification or peer review.</p><nav aria-label="Manuscript links"><a href="{pdfhref}" target="_blank" rel="noopener">Open compiled PDF</a><a href="{pdfhref}" download>Download PDF</a><a href="{texhref}" download>LaTeX source</a><a href="{relative(folder / 'Professor_Hierarchy_Exact_Example.py',page.parent)}">Python example</a><a href="{relative(folder / 'Professor_Hierarchy_Exact_Example.csv',page.parent)}">Numerical results</a><a href="{github}" target="_blank" rel="noopener">PDF on GitHub</a></nav><h2 id="pages">Read the complete manuscript</h2><p>Every typeset page is available below, with its text transcript and direct PDF link. This reader needs no JavaScript or embedded PDF viewer.</p><nav aria-label="Jump to page">{nav}</nav>']
    for n,img in enumerate(pngs,1):
        href=relative(img,page.parent)
        transcript=subprocess.check_output(['pdftotext','-f',str(n),'-l',str(n),'-layout',str(target),'-'],text=True).replace('\f','').strip()
        assert transcript, f'Empty transcript {s} page {n}'
        lazy = 'loading="lazy"' if n>1 else ''
        parts.append(f'<section class="paper-page" id="page-{n}"><h3>Page {n} of {count}</h3><p class="fallback"><a href="{pdfhref}#page={n}" target="_blank" rel="noopener">Open this page in PDF</a> · <a href="{href}" target="_blank" rel="noopener">Full-size page image</a> · <a href="#pages">Page index</a></p><a href="{href}"><img {lazy} decoding="async" src="{href}" alt="Typeset manuscript page {n}"></a><details><summary>Readable text transcript — page {n}</summary><pre>{esc(transcript)}</pre></details></section>')
    parts.append('</main></body></html>')
    write(page,'\n'.join(parts))
    assert read(page).count('class="paper-page"')==count
    records.append(dict(title=titles[i],subtitle=subtitles[i],desc=descs[i],pages=count,pdf=rel(target),tex=rel(folder/source.name),page=rel(page),sha256=hashfile(target),source_sha=hashfile(source)))
    print('Verified PDF and static reader',s,count,'pages',flush=True)

r=records[0]
exp='Professor_Hierarchy_Exact_Example.py'
assert hashfile(stage/exp)=='c4c0067b555d7ae1ee2c81f20f89c5ba5bf55ade1e6bce664d0bdbf1415582ec'
run('python3',exp,cwd=stage)
csvname='Professor_Hierarchy_Exact_Example.csv'
assert hashfile(stage/csvname)=='160cb366cb9b5e2eb714ac0db2c6ecddf5a283f63228abca63210c7aedf40e1f'
folder=(docs/r['pdf']).parent
for name in (exp,csvname):
    shutil.copyfile(stage/name,folder/name)
index=docs/'index.html'
original=read(index)
mark='<!-- professor-of-professors-001v2 -->'
endmark='<!-- /professor-of-professors-001v2 -->'
original=re.sub(re.escape(mark)+r'.*?'+re.escape(endmark),'',original,flags=re.S)
prefix='/pub/' if is_pub else ''
pagehref=prefix+(r['page'].removesuffix('index.html') if is_pub else r['page'])
pdfhref=prefix+r['pdf']
texhref=prefix+r['tex']
links=f'<a href="{pagehref}">Read complete article</a> · <a href="{pdfhref}" download>PDF</a> · <a href="{texhref}">LaTeX source</a> · <a href="{prefix+rel(folder/exp)}">Python example</a> · <a href="{prefix+rel(folder/csvname)}">Numerical results</a>'
inner=f'<p>{esc(credit)}</p><p>{esc(r["subtitle"])}</p><p>{esc(r["desc"])}</p><p>{links}</p>'
if is_pub:
    card=mark+f'<article class="card" data-subject="cs.LO — Logic in Computer Science" data-kind="Research paper" data-title="{esc(r["title"])}"><h2><a href="{pagehref}">{esc(r["title"])}</a></h2>'+inner+'</article>'+endmark
    anchor='<div class="grid" id="grid">'
    ident=str(Path(r['page']).parent)
    entry=dict(id=ident,href=ident+'/',subject='cs.LO_Logic_in_Computer_Science',title=r['title'],kind='Research paper',authors=credit,pdf=r['pdf'],archive_path='docs/'+r['pdf'],source=r['tex'],card_text=r['desc'],classification_note='Atlas-audited conditional research; not independent formal verification.',publication_date='26 November 2026',status='Internally audited research',pages=r['pages'],sha256=r['sha256'],order=-102)
    for p in [Path('scripts/publications.json'),docs/'search-index.json']:
        data=json.loads(read(p))
        new=entry if p.name=='publications.json' else dict(entry,category='cs.LO — Logic in Computer Science',tags=['oracle','partial credit','martingale','self-improvement'],search=r['title']+' '+r['desc']+' '+credit)
        data['items']=[new]+[x for x in data['items'] if x['id']!=ident]
        if 'count' in data:data['count']=len(data['items'])
        write(p,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    sitemap=docs/'sitemap.xml'
    st=read(sitemap)
    url='https://btenneson.github.io/pub/'+entry['href']
    if url not in st:write(sitemap,st.replace('</urlset>',f'  <url><loc>{url}</loc></url>\n</urlset>'))
else:
    card=mark+f'<div class="step"><span class="tag">New · Picard–CIIP · 26 November 2026</span><b>{esc(r["title"])}</b>'+inner+'</div>'+endmark
    anchor='<div class="steps">'
    cp=docs/'catalog.js'; st=read(cp)
    a=json.loads(st[st.index('['):st.rindex(']')+1])
    paths=[r['pdf'],r['tex'],rel(folder/exp),rel(folder/csvname)]
    a=[x for x in a if x.get('link') not in paths]
    n=max(x['id'] for x in a)+1
    new=[dict(id=n,title=r['title'],category='Featured',observation=r['desc'],pages=r['pages'],filetype='PDF',path=r['pdf'].removeprefix('library/'),sha256=r['sha256'],status='Provisional',companion_of='',subject='01_Core_Theory',link=r['pdf'],featured=True,available=True,byline=credit,paper_page=r['page'],static_reader=True)]
    for j,p in enumerate(paths[1:],1):
        new.append(dict(id=n+j,title=Path(p).name,category='Source Companion',observation='Reproducibility companion.',pages=None,filetype=Path(p).suffix[1:].upper(),path=p.removeprefix('library/'),sha256=hashfile(docs/p),status='Provisional',companion_of=r['pdf'].removeprefix('library/'),subject='01_Core_Theory',link=p,featured=False,available=True))
    write(cp,'window.LIBRARY_CATALOG = '+json.dumps(new+a,ensure_ascii=False,separators=(',',':'))+';\n')
    assert 'r.static_reader&&r.paper_page' in read(docs/'assets/app.js')
assert anchor in original
write(index,original.replace(anchor,anchor+card,1))
p=docs/r['page']
for match in re.finditer(r'(?:src|href)="([^"]+)"',read(p)):
    url=html.unescape(match[1]).split('#')[0]
    if not url or url.startswith(('https://','mailto:')):continue
    target=(docs/url.removeprefix('/pub/')) if url.startswith('/pub/') else p.parent/url
    assert target.exists(), f'Broken reader link {url}'
assert mark in read(index)
write(stage/'publication-manifest.json',json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('All 12 page images, transcripts, PDF, source, example and reader links verified.')
