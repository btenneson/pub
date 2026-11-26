#!/usr/bin/env python3
"""Publish both audited Search Dynamics manuscripts, using static readers."""
import hashlib, html, json, os, re, shutil, subprocess
from pathlib import Path
from urllib.parse import quote
stage=Path('.build/search-dynamics-atlas-repeat')
docs=Path('docs')
is_pub=os.environ['GITHUB_REPOSITORY'].lower().endswith('/pub')
repo=os.environ['GITHUB_REPOSITORY']
stem=['From_Search_Dynamics_to_Semi-Ideal_Computers_Part_I_Correctedv2v2','From_Search_Dynamics_to_Semi-Ideal_Computers_Part_IIv2v2']
hashes=['3677a48769069be088698aad25b5711a072eb0838e1b5470c8abb6f3b601bd37','932e4c1412fcbf0b72bd5bb09aee85ec86a012632333a38bfe5bff7f5b4ed5a9']
titles=['From Search Dynamics to Semi-Ideal Computers — Part I','From Search Dynamics to Semi-Ideal Computers — Part II']
subtitles=['Theorem Mazes, Certified Settlement, and Feedback Control','The Geometry of Incomplete Proof Knowledge: Certified Envelopes, Active Discovery, and Reliable Feedback']
descs=['Corrected and expanded foundations of rational theorem mazes, typed settlement, verified-history SICs, safe quotienting, and feedback control. Historical experiments remain explicitly limited.','Certified inner and outer proof-graph envelopes, optimality certificates, active discovery, embedding stability, and reliable feedback. A 64-case synthetic experiment compares fixed-order and geometry-guided edge queries; no real ATP speedup is claimed.']
credit='Research Director: Brian Tenneson · Mathematical development: Picard (ChatGPT research role) · Internal audit: Atlas (ChatGPT research role)'
slugs=['search_dynamics_sic_part_i_atlas_repeat','search_dynamics_sic_part_ii_atlas_repeat']
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
    assert count==[18,13][i], f'Unexpected page count {count}'
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
    other=(f'../{slugs[1-i]}/' if is_pub else slugs[1-i]+'.html')
    nav=' '.join(f'<a href="#page-{n}">{n}</a>' for n in range(1,count+1))
    parts=[f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(titles[i])}</title><link rel="stylesheet" href="{css}"><style>main{{max-width:970px;margin:auto;padding:clamp(12px,3vw,30px)}}nav{{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}}nav a{{padding:.35rem .55rem}}.paper-page{{margin:2rem 0;border-top:1px solid #bbb;scroll-margin-top:1rem}}img{{display:block;width:100%;height:auto;border:1px solid #aaa;background:white}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:.95rem/1.5 ui-monospace,monospace}}a{{overflow-wrap:anywhere}}details{{margin:1rem 0}}.fallback{{font-size:.9rem}}</style></head><body><main><p><a href="{back}">Back to library</a></p><h1>{esc(titles[i])}</h1><h2>{esc(subtitles[i])}</h2><p>{esc(credit)}</p><p>Atlas repeat audit · 26 November 2026 · {count} pages</p><p>{esc(descs[i])}</p><p>Internal mathematical review, not independent formal verification or peer review.</p><nav aria-label="Manuscript links"><a href="{pdfhref}" target="_blank" rel="noopener">Open original PDF</a><a href="{pdfhref}" download>Download PDF</a><a href="{texhref}" download>LaTeX source</a><a href="{other}">Read Part {"II" if i==0 else "I"}</a><a href="{github}" target="_blank" rel="noopener">PDF on GitHub</a></nav><h2 id="pages">Read the complete manuscript</h2><p>Every typeset page is available below, with its text transcript and direct PDF link. This reader needs no JavaScript or embedded PDF viewer.</p><nav aria-label="Jump to page">{nav}</nav>']
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
# Store and run the original experiment, preserving reproducibility.
exp='Picard_Part_II_Envelope_Experiment.py'
run('python3',exp,cwd=stage)
assert (stage/'Picard_Part_II_Envelope_Experiment.csv').is_file()
experiment_folder=(docs/'cs.LO_Logic_in_Computer_Science'/slugs[1] if is_pub else docs/'library/01_Core_Theory/Picard')
for f in [exp,'Picard_Part_II_Envelope_Experiment.csv']:
    shutil.copyfile(stage/f,experiment_folder/f)
# Place the two-part series together at the first featured position; keep old items.
index=docs/'index.html'
original=read(index)
mark='<!-- search-dynamics-slot-one -->'
endmark='<!-- /search-dynamics-slot-one -->'
original=re.sub(re.escape(mark)+r'.*?'+re.escape(endmark),'',original,flags=re.S)
def links(r):
    page=('/pub/'+r['page'].removesuffix('index.html') if is_pub else r['page'])
    pdf=('/pub/' if is_pub else '')+r['pdf']
    tex=('/pub/' if is_pub else '')+r['tex']
    return f'<a href="{page}">Read Part {"I" if r is records[0] else "II"} — full reader</a> · <a href="{pdf}" download>PDF</a> · <a href="{tex}">LaTeX source</a>'
inner=''.join(f'<p><strong>{esc(r["subtitle"])}</strong> · {r["pages"]} pages<br>{esc(r["desc"])}<br>{links(r)}</p>' for r in records)
if is_pub:
    card=mark+'<article class="card" data-subject="cs.LO — Logic in Computer Science" data-kind="Research paper" data-title="From Search Dynamics to Semi-Ideal Computers"><h2>1. From Search Dynamics to Semi-Ideal Computers — Parts I &amp; II</h2><div class="meta">'+esc(credit)+'</div>'+inner+'<p class="status">Atlas repeat-audited research manuscripts; conditional results, not independent formal verification.</p></article>'+endmark
    anchor='<div class="grid" id="grid">'
    assert anchor in original
    old=re.sub(r'(<h2><a [^>]*>)([1-4])\. ',lambda m:m[1]+str(int(m[2])+1)+'. ',original,count=4)
    old=old.replace('Slot 1 is the audited Sovereign–Oracle Compatibility paper, followed by What Makes an Oracle? in slot 2 and the earlier Picard works in slots 3 and 4.','Slot 1 is the two-part Search Dynamics series. The previous featured papers follow in slots 2–5.')
    old=old.replace('Featured in slots 1–4:', 'Featured in slots 1–5:')
    write(index,old.replace(anchor,anchor+card,1))
    catalog_items=[]
    for i,r in enumerate(records):
        ident=str(Path(r['page']).parent)
        catalog_items.append(dict(id=ident,href=ident+'/',subject='cs.LO_Logic_in_Computer_Science',title=r['title'],kind='Research paper',authors=credit,pdf=r['pdf'],archive_path='docs/'+r['pdf'],source=r['tex'],card_text=r['desc'],classification_note='Atlas repeat audit; conditional mathematical manuscript, not formal machine verification.',publication_date='26 November 2026',status='Internally audited research',pages=r['pages'],sha256=r['sha256'],order=-100+i))
    for p in [Path('scripts/publications.json'),docs/'search-index.json']:
        data=json.loads(read(p))
        olditems=[x for x in data['items'] if x['id'] not in {r['id'] for r in catalog_items}]
        add=catalog_items if p.name=='publications.json' else [dict(r,category='cs.LO — Logic in Computer Science',tags=[],search=r['title']+' '+r['card_text']+' '+credit) for r in catalog_items]
        data['items']=add+olditems
        if 'count' in data:data['count']=len(data['items'])
        write(p,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    sitemap=docs/'sitemap.xml'
    st=read(sitemap)
    for r in catalog_items:
        url='https://btenneson.github.io/pub/'+r['href']
        if url not in st:st=st.replace('</urlset>',f'  <url><loc>{url}</loc></url>\n</urlset>')
    write(sitemap,st)
else:
    card=mark+'<div class="step"><span class="tag">Slot 1 · Two-part series · Picard</span><b>From Search Dynamics to Semi-Ideal Computers</b><p>'+esc(credit)+'</p>'+inner+'</div>'+endmark
    anchor='<div class="steps">'
    assert anchor in original
    old=re.sub(r'Slot ([1-4]) ·',lambda m:f'Slot {int(m[1])+1} ·',original,count=4)
    old=old.replace('Featured papers · slots 1–4','Featured papers · slots 1–5')
    write(index,old.replace(anchor,anchor+card,1))
    cp=docs/'catalog.js'; s=read(cp)
    a=json.loads(s[s.index('['):s.rindex(']')+1])
    a=[x for x in a if x.get('paper_page') not in {r['page'] for r in records} and x.get('path') not in {r['tex'].removeprefix('library/') for r in records}]
    for x in a:
        if isinstance(x.get('slot'),int):x['slot']+=1
    n=max(x['id'] for x in a)+1
    new=[]
    for i,r in enumerate(records):
        path=r['pdf'].removeprefix('library/'); tex=r['tex'].removeprefix('library/')
        new.append(dict(id=n,title=r['title'],category='Featured',observation=r['desc'],pages=r['pages'],filetype='PDF',path=path,sha256=r['sha256'],status='Provisional',companion_of='',subject='01_Core_Theory',link=r['pdf'],featured=True,available=True,pinned=True,slot=1,byline=credit,paper_page=r['page'],static_reader=True))
        new.append(dict(id=n+1,title='Source: '+r['title'],category='Source Companion',observation='Exact audited LaTeX source.',pages=None,filetype='TEX',path=tex,sha256=r['source_sha'],status='Provisional',companion_of=path,subject='01_Core_Theory',link=r['tex'],featured=False,available=True))
        n+=2
    write(cp,'window.LIBRARY_CATALOG = '+json.dumps(new+a,ensure_ascii=False,separators=(',',':'))+';\n')
    app=docs/'assets/app.js'
    s=read(app)
    anchor="function readerLink(r,page){return 'reader.html?id='"
    replacement="function readerLink(r,page){if(r.static_reader&&r.paper_page)return r.paper_page+(page?'#page-'+encodeURIComponent(page):'');return 'reader.html?id='"
    if replacement not in s:
        assert anchor in s
        write(app,s.replace(anchor,replacement,1))
# Verify the reader links and all 31 page images before committing.
for r in records:
    p=docs/r['page']
    for m in re.finditer(r'(?:src|href)="([^"]+)"',read(p)):
        url=html.unescape(m[1]).split('#')[0]
        if not url or url.startswith(('https://','/pub/','mailto:')):continue
        assert (p.parent/url).exists(), f'Broken relative link {p}: {url}'
assert mark in read(index)
write(stage/'publication-manifest.json',json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('All reader links and PDF files verified in checkout.')
