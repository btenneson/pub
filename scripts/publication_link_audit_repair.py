#!/usr/bin/env python3
from __future__ import annotations
import argparse,difflib,html,json,re,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'docs'; PAPERS=DOCS/'papers'
RAW='https://raw.githubusercontent.com/btenneson/pub/main/'
BLOB='https://github.com/btenneson/pub/blob/main/'; TREE='https://github.com/btenneson/pub/tree/main/'
PAGES='https://btenneson.github.io/pub/papers/'
STOP={'a','an','and','as','at','by','for','from','in','of','on','or','the','to','v','version','brian','tenneson','with'}
def clean(s): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s))).strip()
def norm(s):
 s=html.unescape(s); s=re.sub(r'\\[A-Za-z@]+',' ',s); s=re.sub(r'[^A-Za-z0-9]+',' ',s).lower(); return re.sub(r'\s+',' ',s).strip()
def toks(s): return {w for w in norm(s).split() if len(w)>2 and w not in STOP and not w.isdigit()}
def pdf_of(t):
 for p in (r"const\s+(?:p|archive)\s*=\s*['\"]([^'\"]+\.pdf)['\"]",r'(https://raw\.githubusercontent\.com/btenneson/pub/main/[^\"\'<>\s]+\.pdf)'):
  m=re.search(p,t,re.I)
  if m:return html.unescape(m.group(1))
 return ''
def title_of(t,slug):
 for p in (r'<header[^>]*>.*?<b>(.*?)</b>',r'<h1[^>]*>\s*<b>(.*?)</b>',r'<title>(.*?)</title>'):
  m=re.search(p,t,re.I|re.S)
  if m:return re.sub(r'\s*[—-]\s*Version\s+[\d.]+\s*$','',clean(m.group(1)),flags=re.I)
 return slug.replace('_',' ').title()
def source_of(t):
 m=re.search(r'https://github\.com/btenneson/pub/blob/main/([^\"\'<>\s]+\.tex)',t,re.I)
 return urllib.parse.unquote(html.unescape(m.group(1))) if m else ''
def readers():
 out=[]
 for d in sorted(x for x in PAPERS.iterdir() if x.is_dir() and (x/'index.html').exists()):
  t=(d/'index.html').read_text(errors='replace')
  if re.search(r'\bsuperseded\s+by\b',clean(t),re.I):continue
  pdf=pdf_of(t)
  if not pdf:continue
  sm=re.search(r'<p[^>]*class=[\'\"]sub[\'\"][^>]*>(.*?)</p>',t,re.I|re.S)
  out.append({'slug':d.name,'title':title_of(t,d.name),'pdf':pdf,'archive':urllib.parse.unquote(pdf[len(RAW):]) if pdf.startswith(RAW) else '',
   'url':PAGES+d.name+'/','source':source_of(t),'subtitle':clean(sm.group(1)) if sm else 'Brian Tenneson'})
 return out
def src_page(r,tex):
 return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(r['title'])} — source</title><link rel="canonical" href="{r['url']}source.html"><style>body{{font:15px/1.5 system-ui;max-width:1100px;margin:auto;padding:24px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid #8885;border-radius:10px;padding:16px}}a{{font-weight:650}}</style></head><body><p><a href="./">← Back to article</a></p><h1>LaTeX source</h1><pre>{html.escape(tex)}</pre></body></html>'''
def reader_page(r,has_source):
 s=r['url']+'source.html' if has_source else ''
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(r['title'])}</title><meta name="description" content="Canonical reader for {html.escape(r['title'])} by Brian Tenneson."><link rel="canonical" href="{r['url']}"><style>:root{{color-scheme:light dark;--b:#8885}}*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui}}header{{padding:1rem;border-bottom:1px solid var(--b)}}h1{{font-size:1.2rem;margin:0 0 .3rem}}.sub{{opacity:.76}}.links{{display:flex;gap:.55rem;flex-wrap:wrap}}.links a{{padding:.45rem .65rem;border:1px solid var(--b);border-radius:8px;text-decoration:none;font-weight:650}}iframe{{width:100%;height:calc(100vh - 165px);min-height:560px;border:0}}</style></head><body><header><h1><b>{html.escape(r['title'])}</b></h1><p class="sub">{html.escape(r['subtitle'])}</p><nav class="links" id="links"></nav></header><iframe id="reader"></iframe><script>const p='{r['pdf']}',source='{s}',v='https://mozilla.github.io/pdf.js/web/viewer.html?file='+encodeURIComponent(p);reader.src=v;links.innerHTML='<a href="'+v+'" target="_blank" rel="noopener">Open full-screen reader</a><a href="'+p+'">PDF</a>'+(source?'<a href="'+source+'">LaTeX source</a>':'');</script></body></html>'''
def best(item,rs):
 it=toks(item); best=(None,0)
 for r in rs:
  rt=toks(r['title']); score=len(it&rt)/max(1,len(rt))+(0.35 if norm(r['title']) in norm(item) else 0)
  if score>best[1]:best=(r,score)
 return best
def fix_tex(p,rs):
 t=p.read_text(errors='replace'); old=t; notes=[]
 for r in rs:
  if not r['archive']:continue
  for u in (RAW+r['archive'],BLOB+urllib.parse.quote(r['archive'],safe='/')):
   if u in t:t=t.replace(u,r['url']);notes.append('archive URL→'+r['slug'])
 pat=re.compile(r'(\\begin\{thebibliography\}.*?\\end\{thebibliography\})',re.S)
 for m in reversed(list(pat.finditer(t))):
  parts=re.split(r'(?=\\bibitem(?:\[[^\]]*\])?\{[^}]+\})',m.group(1)); out=[]
  for x in parts:
   if x.startswith('\\bibitem') and 'tenneson' in norm(x) and PAGES not in x:
    r,score=best(x,rs)
    if r and score>=.9:
     x=x.rstrip()+rf'\ \href{{{r["url"]}}}{{Live article}}.'+'\n';notes.append('citation→'+r['slug'])
   out.append(x)
  t=t[:m.start()]+''.join(out)+t[m.end():]
 if t!=old:
  if '\\href{' in t and 'hyperref' not in t:t=t.replace('\\begin{document}','\\usepackage{hyperref}\n\\begin{document}',1)
  p.write_text(t);return notes
 return []
def fix_builder(apply):
 p=ROOT/'scripts/build_library_homepage_v2.py'; t=p.read_text(); old=t
 t=t.replace('source = extract_source_link(text, archive_path)',"source = f\"papers/{folder.name}/source.html\" if (folder / 'source.html').exists() else ''")
 t=t.replace("const src=x.source?`<a href=\\\"${esc(x.source)}\\\">Source</a>`:'';","const src=x.source&&x.source.startsWith('papers/')?`<a href=\\\"${esc(x.source)}\\\">Source</a>`:'';")
 t=t.replace('<a href="https://github.com/btenneson/pub">GitHub archive</a>','')
 if apply and t!=old:p.write_text(t)
 return t!=old
def scan():
 ugly=[];broken=[];ext=set(); anch=re.compile(r'<a\b[^>]*href=[\'\"]([^\'\"]+)',re.I)
 for p in DOCS.rglob('*.html'):
  t=p.read_text(errors='replace')
  for u in anch.findall(t):
   u=html.unescape(u)
   # JavaScript template placeholders are not literal links and must not be resolved as files.
   if '${' in u: continue
   if u.startswith((BLOB,TREE)):ugly.append(f'{p.relative_to(ROOT)} -> {u}')
   if u.startswith(('http://','https://')):ext.add(u)
   elif u and not u.startswith(('#','mailto:')):
    q=(p.parent/urllib.parse.unquote(urllib.parse.urlsplit(u).path)).resolve(); q=q/'index.html' if q.is_dir() else q
    if not q.exists():broken.append(f'{p.relative_to(ROOT)} -> {u}')
 # Do not grep raw source text inside <pre> blocks for URLs: only actual anchors are destinations.
 return sorted(set(ugly)),sorted(set(broken)),ext
def netcheck(urls):
 bad=[]
 for u in sorted(urls)[:250]:
  try:
   q=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0','Range':'bytes=0-0'}); urllib.request.urlopen(q,timeout=10).close()
  except Exception as e:bad.append(f'{type(e).__name__}: {u} ({e})')
 return bad
def unresolved(rs):
 out=[]
 for p in ROOT.rglob('*.tex'):
  if any(x in p.parts for x in ('build','.build')):continue
  t=p.read_text(errors='replace')
  for m in re.finditer(r'\\bibitem(?:\[[^\]]*\])?\{[^}]+\}(.*?)(?=\\bibitem|\\end\{thebibliography\})',t,re.S):
   x=m.group(1)
   if 'tenneson' in norm(x) and PAGES not in x:
    r,s=best(x,rs)
    if r and s>=.9:out.append(f'{p.relative_to(ROOT)} -> {r["title"]}')
 return sorted(set(out))
def main():
 a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');a.add_argument('--network',action='store_true');a.add_argument('--report',default='docs/LINK_AUDIT.md');a.add_argument('--manifest',default='build/link-manifest.json');o=a.parse_args()
 rs=readers();fix_builder(o.apply);changed=[]
 if o.apply:
  for p in ROOT.rglob('*.tex'):
   if any(x in p.parts for x in ('build','.build')):continue
   n=fix_tex(p,rs)
   if n:
    r=next((r for r in rs if r['source']==p.relative_to(ROOT).as_posix()),None);changed.append({'source':p.relative_to(ROOT).as_posix(),'pdf':r['archive'] if r else '','reader':r['slug'] if r else '','notes':n})
 reader_changes=source_changes=0
 for r in rs:
  page=PAPERS/r['slug']/'index.html'; sp=PAPERS/r['slug']/'source.html'; has=bool(r['source'] and (ROOT/r['source']).exists())
  if has:
   want=src_page(r,(ROOT/r['source']).read_text(errors='replace'))
   if not sp.exists() or sp.read_text(errors='replace')!=want:
    source_changes+=1
    if o.apply:sp.write_text(want)
  want=reader_page(r,has)
  if page.read_text(errors='replace')!=want:
   reader_changes+=1
   if o.apply:page.write_text(want)
 ugly,broken,ext=scan();bad=netcheck(ext) if o.network else [];unres=unresolved(rs)
 Path(o.manifest).parent.mkdir(parents=True,exist_ok=True);Path(o.manifest).write_text(json.dumps({'changed_sources':changed},indent=2)+'\n')
 L=['# Publication Link Audit','',f'- Active canonical readers: **{len(rs)}**',f'- Reader pages changed/needed: **{reader_changes}**',f'- Clean source pages changed/needed: **{source_changes}**',f'- Article sources changed: **{len(changed)}**',f'- Visible GitHub blob/tree destinations remaining: **{len(ugly)}**',f'- Broken local links: **{len(broken)}**',f'- Unresolved confidently matched self-citations: **{len(unres)}**',f'- External URL failures: **{len(bad)}**','','## Remaining GitHub destinations']
 L+=['- None.'] if not ugly else [f'- `{x}`' for x in ugly];L+=['','## Broken local links']+(['- None.'] if not broken else [f'- `{x}`' for x in broken]);L+=['','## Unresolved self-citations']+(['- None.'] if not unres else [f'- `{x}`' for x in unres]);L+=['','## External failures']+(['- None.'] if not bad else [f'- `{x}`' for x in bad]);L+=['','## Repairs']+(['- No source citations changed in this pass.'] if not changed else [f'- `{x["source"]}` — '+', '.join(x['notes']) for x in changed])
 Path(o.report).write_text('\n'.join(L)+'\n');print(json.dumps({'readers':len(rs),'reader_changes':reader_changes,'source_pages':source_changes,'sources_changed':len(changed),'ugly':len(ugly),'broken':len(broken),'unresolved':len(unres),'external_failures':len(bad)},indent=2))
if __name__=='__main__':main()