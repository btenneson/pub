#!/usr/bin/env python3
"""Fail publication builds on broken readers, PDFs, quotes, or subject routes."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
from html.parser import HTMLParser
import hashlib,json,re,unicodedata
import fitz
R=Path(__file__).resolve().parents[1];D=R/'docs'
def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s)).strip().replace('- ','')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src') and v:self.links.append(v)
def main():
 data=json.loads((D/'search-index.json').read_text());items=data['items'];assert data['count']==len(items)
 assert not (D/'papers').exists(),'Obsolete papers directory returned'
 seen=set();checked=0;unavailable=[]
 paths=[D/'index.html',D/'404.html']
 for x in items:
  assert x['id'].startswith(x['subject']+'/')
  p=D/x['href']/'index.html';assert p.is_file(),p;paths.append(p);paths.append(D/x['subject']/'index.html')
  for k in ('source','source_file','download','text'):
   if x.get(k):assert (D/x[k]).is_file(),x[k]
  if x.get('pdf'):
   pdf=D/x['pdf'];assert pdf.is_file(),pdf
   digest=hashlib.sha256(pdf.read_bytes()).hexdigest();assert digest==x['sha256'];assert digest not in seen,'duplicate card';seen.add(digest)
   d=fitz.open(pdf);assert len(d)>0,pdf
   assert all(d[i].get_text().strip() for i in range(len(d))),('empty/unreadable page',pdf)
   q=norm(x['quote']);assert q,('missing quote',x['title']);assert q in norm(d[x['quote_page']-1].get_text()),('quote not in cited page',x['title'],q)
   checked+=1
  elif x.get('status'):unavailable.append(x['title'])
  else:
   assert x.get('text') and x.get('quote')
   parser=Links();parser.feed((D/x['text']).read_text())
   plain=re.sub('<[^>]+>',' ',(D/x['text']).read_text())
   import html
   assert norm(x['quote']) in norm(html.unescape(plain)), ('text quote mismatch',x['title'])
 for p in set(paths):
  parser=Links();parser.feed(p.read_text())
  for link in parser.links:
   u=urlsplit(link)
   if u.scheme or u.netloc or not u.path:continue
   path=unquote(u.path)
   target=(D/path[len('/pub/'):]) if path.startswith('/pub/') else p.parent/path
   if target.is_dir():target/='index.html'
   assert target.exists(),(p,link)
 aliases=json.loads((D/'redirects.json').read_text())
 for old,new in aliases.items():
  target=D/new
  if target.is_dir():target/='index.html'
  assert target.exists(),('redirect target missing',old,new)
 print(f'PASS: {len(items)} cards, {checked} readable PDFs with page-verified quotes; all reader and redirect targets exist.')
 print('Explicitly unavailable:',', '.join(unavailable) or 'none')
if __name__=='__main__':main()
