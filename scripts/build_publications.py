#!/usr/bin/env python3
"""Build all publication cards and readers from one reviewed subject catalog."""
from pathlib import Path
import html,json,re,hashlib,shutil
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1];DOCS=ROOT/'docs'
SUBJECTS={'cs.LO':'Logic in Computer Science','cs.AI':'Artificial Intelligence','cs.LG':'Machine Learning','cs.CR':'Cryptography and Security','cs.CY':'Computers and Society','cs.CL':'Computation and Language','cs.CC':'Computational Complexity','math.LO':'Logic','q-bio.QM':'Quantitative Methods','stat.AP':'Applications of Statistics'}
DIRECT_PDF_READER='cs.LO_Logic_in_Computer_Science/universal_theorem_geometry_ii_weighted_geodesics_mapquest_heuristics'
CSS='''*{box-sizing:border-box} :root{color-scheme:light dark;--bg:#f7f8fa;--panel:#fff;--ink:#18212b;--muted:#536170;--line:#d7dde4;--accent:#245d83;--tint:#eaf3f8} @media(prefers-color-scheme:dark){:root{--bg:#11161b;--panel:#182028;--ink:#eef4f8;--muted:#b6c1cb;--line:#33414c;--accent:#8bcdf7;--tint:#1d3341}}body{margin:0;background:var(--bg);color:var(--ink);font:1rem/1.55 system-ui,-apple-system,Segoe UI,sans-serif}a{color:var(--accent)}main{max-width:1180px;margin:auto;padding:24px}h1{font-size:clamp(1.6rem,4vw,2.5rem);line-height:1.2}h2{font-size:1.1rem;line-height:1.4;margin:0 0 .6rem}.muted,.meta,cite{color:var(--muted)}.meta,cite{font-size:.9rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:1rem}.card{display:flex;flex-direction:column;padding:1.2rem;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow-wrap:anywhere}.card[hidden]{display:none}.links{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:auto}.links a,.links button{padding:.5rem .7rem;border:1px solid var(--line);border-radius:8px;text-decoration:none;font-weight:650}.links button{cursor:pointer}.links a:hover,.links a:focus-visible,.links button:hover,.links button:focus-visible{background:var(--tint)}blockquote{margin:1rem 0;padding:.75rem 1rem;border-left:3px solid var(--accent);background:var(--tint)}blockquote p{margin:0 0 .4rem}cite{font-style:normal}.controls{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:.6rem;margin:1.5rem 0 1rem}input,select,button{font:inherit;padding:.65rem;min-width:0;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:8px}.reader-header{padding:1rem 1.5rem;border-bottom:1px solid var(--line);background:var(--panel)}.reader-header h1{font-size:1.3rem;margin:.5rem 0}.reader-header blockquote{margin:.7rem 0;max-width:70rem}.reader-frame{display:block;width:100%;height:80vh;min-height:560px;border:0;background:white}.status{padding:1rem;border:1px solid var(--line);background:var(--tint)}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:1rem}.toplinks{display:flex;gap:1rem;flex-wrap:wrap}footer{margin:2rem 0;color:var(--muted)}@media(max-width:800px){main{padding:16px}.controls{grid-template-columns:1fr 1fr}.controls input{grid-column:1/-1}.reader-header{padding:1rem}}@media(max-width:480px){.controls{grid-template-columns:1fr}}'''
def esc(s):return html.escape(str(s or ''),quote=True)
def url(s):return '/pub/'+quote(s,safe='/._-')
def shell(title,body,canonical=''):
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title>'+('<link rel="canonical" href="https://btenneson.github.io'+url(canonical)+'">' if canonical else '')+'<link rel="stylesheet" href="/pub/publications.css"></head><body>'+body+'</body></html>\n'
def quote_block(x):
 if not x.get('quote'):return ''
 attribution=x.get('quote_attribution') or (f"{x['authors']} · p. {x['quote_page']}" if x.get('quote_page') else x['authors'])
 return '<blockquote><p>“'+esc(x['quote'])+'”</p><cite>'+esc(attribution)+'</cite></blockquote>'
def links(x,reader=False):
 result='<a href="'+url(x['href'])+'">Read</a>' if not reader else '<a href="/pub/">All publications</a><a href="'+url(x['subject']+'/')+'">Subject</a>'
 if x.get('pdf'):
  p=url(x['pdf'])
  if reader:
   if x['id']==DIRECT_PDF_READER:result+='<a href="'+p+'" target="_blank" rel="noopener">Open PDF</a>'
   else:result+='<button type="button" class="fullscreen-reader" onclick="const f=document.querySelector(\'.reader-frame\');if(f?.requestFullscreen)f.requestFullscreen();else if(f?.webkitRequestFullscreen)f.webkitRequestFullscreen();">Open full-screen reader</button>'
  result+='<a href="'+p+'" download>Download PDF</a>'
 if x.get('download'):result+='<a href="'+url(x['download'])+'" download>Download DOCX</a>'
 if x.get('source'):result+='<a href="'+url(x['source'])+'">Source</a>'
 return '<nav class="links" aria-label="Publication links">'+result+'</nav>'
def card(x):
 return '<article class="card" data-subject="'+esc(x['category'])+'" data-kind="'+esc(x['kind'])+'" data-title="'+esc(x['title'])+'"><h2><a href="'+url(x['href'])+'">'+esc(x['title'])+'</a></h2><div class="meta">'+esc(x['kind']+' · '+x['category'])+'</div>'+quote_block(x)+('<p class="status">'+esc(x['status'])+'</p>' if x.get('status') else '')+links(x)+'</article>'
def index(items,title,subject=None):
 controls='''<div class="controls"><input id="q" type="search" aria-label="Search publications" placeholder="Search titles, topics, quotes…"><select id="kind" aria-label="Collection"><option value="">All collections</option>'''+''.join('<option>'+esc(k)+'</option>' for k in sorted({x['kind'] for x in items}))+'''</select><select id="cat" aria-label="Subject"><option value="">All subjects</option>'''+''.join('<option>'+esc(k)+'</option>' for k in sorted({x['category'] for x in items}))+'''</select><select id="sort" aria-label="Sort"><option value="default">Library order</option><option value="title">Title A–Z</option><option value="subject">Subject</option></select></div><button id="clear" type="button">Clear filters</button>'''
 body='<main><h1>'+esc(title)+'</h1><p class="muted">Research papers, applied data science, and stories.</p><nav class="toplinks">'+('<a href="/pub/">All publications</a>' if subject else '')+'<a href="/pub/PERMALINK_POLICY.md">Publication policy</a></nav>'+controls+'<p id="count" role="status">'+str(len(items))+' publications</p><div class="grid" id="grid">'+''.join(card(x) for x in items)+'</div><p id="empty" hidden>No publications match that search.</p><footer>Subject folders use arXiv classification names; these labels do not imply submission to or endorsement by arXiv.</footer></main><script src="/pub/publications.js"></script>'
 return shell(title,body,(subject+'/') if subject else '')
def main():
 data=json.loads((ROOT/'scripts/publications.json').read_text());items=data['items']
 for x in items:
  code=x['subject'].split('_')[0];x['category']=code+' — '+SUBJECTS[code];x['tags']=x.get('tags',[]);x['search']=' '.join([x['title'],x['category'],x.get('quote',''),x.get('authors','')])
  folder=DOCS/x['id'];folder.mkdir(parents=True,exist_ok=True)
  # Keep a reviewed publication attached to its archive when that archive exists.
  src=ROOT/x.get('archive_path','')
  if x.get('pdf') and src.is_file() and src.resolve()!=(DOCS/x['pdf']).resolve():
   shutil.copyfile(src,DOCS/x['pdf'])
  if x.get('pdf'):x['sha256']=hashlib.sha256((DOCS/x['pdf']).read_bytes()).hexdigest()
  if x.get('source_file'):
   s=(DOCS/x['source_file']).read_text(errors='replace');(DOCS/x['source']).write_text(shell(x['title']+' — source','<main><a href="'+url(x['href'])+'">Back to publication</a><h1>'+esc(x['title'])+'</h1><a href="'+url(x['source_file'])+'" download>Download source</a><pre>'+esc(s)+'</pre></main>'))
  body='<header class="reader-header"><h1>'+esc(x['title'])+'</h1><div class="meta">'+esc(x['authors']+' · '+x['category'])+'</div>'+quote_block(x)+links(x,True)
  if x.get('classification_note'):body+='<p class="meta">'+esc(x['classification_note'])+'</p>'
  trilogy=[y for y in items if y['title'].startswith(('MAPQUEST I —','MAPQUEST II —','MAPQUEST III —'))]
  if x in trilogy:body+='<p>MAPQUEST trilogy: '+ ' · '.join('<a href="'+url(y['href'])+'">'+esc(y['title'].split(' —')[0])+'</a>' for y in trilogy)+'</p>'
  body+='</header>'
  target=x.get('pdf') or x.get('text')
  if target:body+='<iframe class="reader-frame" src="'+url(target)+'" title="'+esc(x['title'])+' — document reader"></iframe>'
  else:body+='<main><p class="status">'+esc(x.get('status','Document unavailable.'))+'</p></main>'
  (folder/'index.html').write_text(shell(x['title'],body,x['href']))
 DOCS.joinpath('publications.css').write_text(CSS)
 DOCS.joinpath('publications.js').write_text('''const q=document.getElementById('q'),kind=document.getElementById('kind'),cat=document.getElementById('cat'),sort=document.getElementById('sort'),grid=document.getElementById('grid');const cards=[...grid.children];const norm=s=>s.normalize('NFKD').toLowerCase();function render(){let tokens=norm(q.value).trim().split(/\\s+/).filter(Boolean),n=0;for(const c of cards){c.hidden=!(tokens.every(t=>norm(c.textContent).includes(t))&&(!kind.value||c.dataset.kind===kind.value)&&(!cat.value||c.dataset.subject===cat.value));if(!c.hidden)n++}const ordered=[...cards];if(sort.value==='title')ordered.sort((a,b)=>a.dataset.title.localeCompare(b.dataset.title));if(sort.value==='subject')ordered.sort((a,b)=>a.dataset.subject.localeCompare(b.dataset.subject)||a.dataset.title.localeCompare(b.dataset.title));ordered.forEach(c=>grid.appendChild(c));document.getElementById('count').textContent=n+' of '+cards.length+' publications';document.getElementById('empty').hidden=n!==0;}[q,kind,cat,sort].forEach(e=>e.addEventListener(e===q?'input':'change',render));document.getElementById('clear').onclick=()=>{q.value='';kind.value='';cat.value='';sort.value='default';render();q.focus()};render();''')
 DOCS.joinpath('index.html').write_text(index(items,'Brian Tenneson — Publication Library'))
 for subject in sorted({x['subject'] for x in items}):
  group=[x for x in items if x['subject']==subject];(DOCS/subject/'index.html').write_text(index(group,group[0]['category'],subject))
 DOCS.joinpath('search-index.json').write_text(json.dumps({'schema_version':1,'count':len(items),'items':items},ensure_ascii=False,indent=2)+'\n')
 DOCS.joinpath('404.html').write_text(shell('Publication moved','<main><h1>Find this publication</h1><p id="message">Checking the updated publication address…</p><a href="/pub/">Browse all publications</a></main><script>fetch("/pub/redirects.json").then(r=>r.json()).then(m=>{const p=decodeURIComponent(location.pathname.replace(/^\\/pub\\//,""));if(Object.prototype.hasOwnProperty.call(m,p)){location.replace("/pub/"+m[p]+location.search+location.hash)}else{document.getElementById("message").textContent="This address is no longer in the catalog. Search the publication library below."}}).catch(()=>{document.getElementById("message").textContent="Please open the publication library."});</script>'))
 # Keep legacy/historical reader pages consistent with the current fullscreen control.
 fullscreen_button='<button type="button" class="fullscreen-reader" onclick="const f=document.querySelector(\'.reader-frame\');if(f?.requestFullscreen)f.requestFullscreen();else if(f?.webkitRequestFullscreen)f.webkitRequestFullscreen();">Open full-screen reader</button>'
 raw_fullscreen=re.compile(r'<a href="[^"]+\.pdf" target="_blank" rel="noopener">Open full-screen reader</a>',re.I)
 for reader_page in DOCS.glob('*/*/index.html'):
  legacy=reader_page.read_text(errors='replace')
  repaired=raw_fullscreen.sub(fullscreen_button,legacy)
  if repaired!=legacy:reader_page.write_text(repaired)
 print(f'Built {len(items)} publication cards and readers in {len({x["subject"] for x in items})} subjects.')
if __name__=='__main__':main()
