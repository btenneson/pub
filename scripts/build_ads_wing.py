#!/usr/bin/env python3
import argparse, hashlib, html, json, os, re, shutil, subprocess, tempfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
import requests

DOC_EXTS={'.pdf','.docx','.pptx','.odt','.rtf','.tex','.md','.txt','.html','.htm'}
ADS_RE=re.compile(r'(?<![A-Za-z])ADS(?![A-Za-z])',re.I)
DS_RE=re.compile(r'\b(?:applied\s+data\s+science|data\s+science)\b',re.I)
AUTHOR_RE=re.compile(r'\b(?:Brian\s+(?:[A-Z]\.?\s+)?Tenneson|B\.?\s*Tenneson|Tenneson,\s*Brian)\b',re.I)
CATEGORIES=[
 ('healthcare_biomedical','Healthcare & Biomedical Analytics',['cancer','tumor','diabetes','heart disease','cardiovascular','lung','kidney','renal','clinical','patient','medical','health','disease']),
 ('sports_performance','Sports & Performance Analytics',['nba','basketball','sports','player','team','season','game','athlete']),
 ('nlp_text','NLP & Text Analytics',['natural language','nlp','spam','email','text classification','sentiment','document classification']),
 ('statistical_methods','Statistical Methods & Experimental Design',['correlation','regression','hypothesis','anova','probability','confidence interval','sampling','experiment','statistical','p-value','chi-square']),
 ('machine_learning','Machine Learning & Predictive Modeling',['machine learning','random forest','decision tree','classifier','classification','logistic regression','neural network','prediction','predictive','supervised learning','cross-validation']),
 ('data_preparation_eda','Data Preparation, Cleaning & EDA',['data cleaning','cleaning','preprocessing','missing data','missing value','data wrangling','feature engineering','exploratory data analysis','eda','outlier'])]
TAGS={
 'Regression':['regression','logistic regression','linear regression'],'Classification':['classification','classifier'],'Random Forest':['random forest'],
 'Visualization':['visualization','visualisation','plot','chart','dashboard'],'Correlation':['correlation'],'Data Cleaning':['data cleaning','cleaning','preprocessing'],
 'Experimental Design':['experimental design','experiment'],'Healthcare':['cancer','tumor','diabetes','heart disease','lung','kidney','clinical','patient','health'],
 'Sports':['nba','basketball','sports','athlete'],'NLP':['natural language','nlp','spam','text classification']}

def headers(token):
    h={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'ads-wing-builder'}
    if token:h['Authorization']=f'Bearer {token}'
    return h

def get(session,url,token,**kwargs):
    r=session.get(url,headers=headers(token),timeout=90,**kwargs); r.raise_for_status(); return r

def repos(session,owner,token):
    out=[]
    for page in range(1,20):
        batch=get(session,f'https://api.github.com/users/{owner}/repos',token,params={'per_page':100,'page':page,'type':'owner','sort':'full_name'}).json()
        out += [r for r in batch if not r.get('private') and not r.get('fork')]
        if len(batch)<100:break
    return out

def tree(session,owner,repo,branch,token):
    return get(session,f'https://api.github.com/repos/{owner}/{repo}/git/trees/{quote(branch,safe="")}',token,params={'recursive':'1'}).json().get('tree',[])

def download(session,owner,repo,branch,path,token):
    url=f'https://raw.githubusercontent.com/{owner}/{repo}/{quote(branch,safe="")}/{quote(path,safe="/")}'
    r=session.get(url,headers={'User-Agent':'ads-wing-builder'},timeout=90); r.raise_for_status(); return r.content

def decode(data):
    for enc in ('utf-8','utf-8-sig','cp1252','latin1'):
        try:return data.decode(enc)
        except UnicodeDecodeError:pass
    return data.decode('utf-8',errors='replace')

def extract(path):
    ext=path.suffix.lower()
    if ext in {'.tex','.md','.txt','.html','.htm'}:return decode(path.read_bytes())
    if ext=='.pdf':
        out=path.with_suffix('.txt'); subprocess.run(['pdftotext','-layout',str(path),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return out.read_text(errors='replace') if out.exists() else ''
    if ext=='.docx':
        from docx import Document
        return '\n'.join(p.text for p in Document(str(path)).paragraphs)
    if ext=='.pptx':
        from pptx import Presentation
        return '\n'.join(sh.text for s in Presentation(str(path)).slides for sh in s.shapes if hasattr(sh,'text'))
    if ext=='.odt':
        from zipfile import ZipFile
        from bs4 import BeautifulSoup
        with ZipFile(path) as z:return BeautifulSoup(z.read('content.xml'),'xml').get_text('\n')
    if ext=='.rtf':
        from striprtf.striprtf import rtf_to_text
        return rtf_to_text(decode(path.read_bytes()))
    return ''

def norm(s):return re.sub(r'\s+',' ',s).strip()
def snippet(text,m,r=85):return '' if not m else norm(text[max(0,m.start()-r):min(len(text),m.end()+r)])[:240]

def authored(text,path,repo):
    m=AUTHOR_RE.search(text)
    if m:return True,snippet(text,m)
    if repo.lower()=='public_projects' and re.search(r'tenneson',path,re.I):
        return True,'public_projects authorship context + filename/path contains “Tenneson”.'
    return False,''

def title(text,filename):
    skip=re.compile(r'^(?:Brian\s+Tenneson|Tenneson,\s*Brian|ADS\s*\d*|Applied Data Science)$',re.I)
    for line in [norm(x) for x in text.splitlines() if norm(x)][:40]:
        if 6<=len(line)<=150 and not skip.match(line):return line
    return Path(filename).stem.replace('_',' ')

def classify(text):
    t=text.lower(); scores=[]
    for slug,label,terms in CATEGORIES:
        d=sum(term in t for term in terms); n=sum(t.count(term) for term in terms); scores.append((d,n,slug,label))
    score_map={slug:{'distinct_terms':d,'occurrences':n} for d,n,slug,_ in scores if d}
    for preferred in ('healthcare_biomedical','sports_performance','nlp_text'):
        x=next(v for v in scores if v[2]==preferred)
        if x[0]:return x[2],x[3],score_map
    scores.sort(reverse=True)
    if scores and scores[0][0]:return scores[0][2],scores[0][3],score_map
    return 'general','General Applied Data Science',{}

def tags(text):
    t=text.lower(); return [k for k,terms in TAGS.items() if any(x in t for x in terms)]
def safe(name):return re.sub(r'[^A-Za-z0-9._-]+','_',name).strip('_') or 'document'

def manifest_md(records):
    lines=['# Applied Data Science (ADS) Wing Manifest','',
      'Generated from public repositories owned by `btenneson`. Eligibility requires author evidence plus at least one extracted-text marker: standalone `ADS`, `data science`, or `applied data science`.','']
    groups=defaultdict(list)
    for r in records:groups[r['category']].append(r)
    for cat in sorted(groups):
        lines += [f'## {cat}','']
        for r in sorted(groups[cat],key=lambda x:x['title'].lower()):
            lines += [f"- **{r['title']}** — `{r['local_path']}`",f"  - Source: {r['sources'][0]['repo']}/{r['sources'][0]['path']}",f"  - Tags: {', '.join(r['tags']) if r['tags'] else '—'}"]
        lines.append('')
    return '\n'.join(lines)

def landing(records,generated):
    groups=defaultdict(list)
    for r in records:groups[r['category']].append(r)
    sections=[]
    for cat in sorted(groups):
        cards=[]
        for r in sorted(groups[cat],key=lambda x:x['title'].lower()):
            cards.append(f'<article class="card"><h3>{html.escape(r["title"])}</h3><p>{html.escape(", ".join(r["tags"]) or "Applied Data Science")}</p><p class="links"><a href="{quote(r["web_path"],safe="/")}">Open document</a><a href="{html.escape(r["sources"][0]["html_url"],quote=True)}">Original GitHub source</a></p></article>')
        sections.append(f'<section><h2>{html.escape(cat)}</h2><div class="grid">{"".join(cards)}</div></section>')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Applied Data Science (ADS) — Brian Tenneson</title><style>body{{font-family:system-ui;line-height:1.45;margin:0}}main{{max-width:1100px;margin:auto;padding:24px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}}.card{{border:1px solid #8886;border-radius:10px;padding:12px}}.card h3{{font-size:1rem;margin:0 0 8px}}.links{{display:flex;gap:12px;flex-wrap:wrap}}input{{font:inherit;padding:9px;width:min(100%,460px);margin:8px 0 18px}}section{{margin:28px 0}}</style></head><body><main><p><a href="../">← Main library</a></p><h1>Applied Data Science (ADS)</h1><p>Works by Brian Tenneson collected from public GitHub repositories and grouped by the subject matter of each work.</p><p><a href="MANIFEST.md">Manifest</a> · <a href="manifest.json">Machine-readable manifest</a></p><input id="q" type="search" placeholder="Search ADS wing…"><div id="g">{''.join(sections)}</div><p><small>Manifest generated {html.escape(generated)}.</small></p></main><script>q.oninput=()=>document.querySelectorAll('.card').forEach(x=>x.hidden=!x.innerText.toLowerCase().includes(q.value.toLowerCase()))</script></body></html>'''

def patch_index(path):
    s=path.read_text(encoding='utf-8')
    if 'href="ADS/"' in s:return
    s=s.replace('Stable browser-reader links for all 25 papers represented in this repository.','Stable browser-reader links for the core paper library, plus specialized subject wings.')
    needle='<input id="q" type="search" placeholder="Search papers…">'
    wing='<div class="grid" style="margin:12px 0 24px"><article class="card"><h3>Applied Data Science (ADS)</h3><p>Graduate-school and related applied data-science work, grouped by subject matter.</p><p class="links"><a href="ADS/">Browse ADS wing</a><a href="ADS/MANIFEST.md">Manifest</a></p></article></div>'
    path.write_text(s.replace(needle,wing+needle,1),encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--owner',default='btenneson'); ap.add_argument('--root',default='.'); ap.add_argument('--token',default=os.getenv('GITHUB_TOKEN','')); ap.add_argument('--generated-at',default='')
    a=ap.parse_args(); root=Path(a.root).resolve(); archive=root/'ADS'; web=root/'docs'/'ADS'
    for d in (archive,web):
        if d.exists():shutil.rmtree(d)
        d.mkdir(parents=True)
    session=requests.Session(); records=[]; by_hash={}; scanned=0
    rs=repos(session,a.owner,a.token)
    for repo in rs:
        name=repo['name']
        if name.lower()=='pub':continue
        branch=repo['default_branch']
        try:items=tree(session,a.owner,name,branch,a.token)
        except Exception as e:print('WARN tree',name,e); continue
        for item in items:
            path=item.get('path',''); ext=Path(path).suffix.lower()
            if item.get('type')!='blob' or ext not in DOC_EXTS:continue
            scanned+=1
            try:data=download(session,a.owner,name,branch,path,a.token)
            except Exception as e:print('WARN download',name,path,e); continue
            with tempfile.TemporaryDirectory() as td:
                f=Path(td)/('source'+ext); f.write_bytes(data)
                try:text=extract(f)
                except Exception as e:print('WARN extract',name,path,e); continue
            am,dm=ADS_RE.search(text),DS_RE.search(text); ok,ae=authored(text,path,name)
            if not (ok and (am or dm)):continue
            digest=hashlib.sha256(data).hexdigest()
            src={'repo':name,'path':path,'branch':branch,'blob_sha':item.get('sha',''),'html_url':f'https://github.com/{a.owner}/{name}/blob/{quote(branch,safe="")}/{quote(path,safe="/")}' }
            if digest in by_hash:by_hash[digest]['sources'].append(src); continue
            slug,label,scores=classify(text); filename=safe(Path(path).name)
            dest=archive/slug/filename; wdest=web/slug/filename
            if dest.exists():filename=safe(f'{name}_{Path(path).name}'); dest=archive/slug/filename; wdest=web/slug/filename
            dest.parent.mkdir(parents=True,exist_ok=True); wdest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(data); wdest.write_bytes(data)
            rec={'title':title(text,Path(path).name),'category':label,'category_slug':slug,'category_scores':scores,'tags':tags(text),'sha256':digest,'bytes':len(data),'local_path':dest.relative_to(root).as_posix(),'web_path':wdest.relative_to(web).as_posix(),'sources':[src],'match_evidence':{'author':ae,'ADS':snippet(text,am),'data_science':snippet(text,dm)}}
            records.append(rec); by_hash[digest]=rec; print('MATCH',name,path,'->',rec['local_path'])
    records.sort(key=lambda r:(r['category'],r['title'].lower())); generated=a.generated_at or 'GitHub Actions run'
    payload={'schema_version':2,'owner':a.owner,'generated_at':generated,'scanned_document_candidates':scanned,'document_count':len(records),'documents':records}
    for d in (archive,web):
        (d/'manifest.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8'); (d/'MANIFEST.md').write_text(manifest_md(records),encoding='utf-8')
    (archive/'README.md').write_text('# Applied Data Science (ADS)\n\nCanonical copied archive for the ADS wing. See `MANIFEST.md` for provenance and categorization.\n',encoding='utf-8')
    (web/'index.html').write_text(landing(records,generated),encoding='utf-8'); patch_index(root/'docs'/'index.html')
    print(f'Generated {len(records)} unique ADS documents after scanning {scanned} document candidates from {len(rs)} public repositories.')
if __name__=='__main__':main()
