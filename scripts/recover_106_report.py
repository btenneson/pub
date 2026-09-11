#!/usr/bin/env python3
"""Identify 20 historical publication contexts to restore to the current 86-card catalog."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];BASE='6a2ce29ddc308747d75ca82f58c3b35604a8b744'
def norm(s):return re.sub(r'\s+',' ',(s or '').casefold().replace('—','-').replace('–','-')).strip()
def git_bytes(p):
 p=unquote((p or '').strip())
 if not p or p.endswith('/') or p.startswith(('http://','https://')):return None
 r=subprocess.run(['git','show',f'{BASE}:{p}'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 return r.stdout if r.returncode==0 else None
def old_blob(x):
 cand=[]
 for k in ('archive_path','pdf','href','source'):
  raw=x.get(k) or ''
  if raw.startswith(('http://','https://')):
   raw=urlsplit(raw).path
   for m in ('/btenneson/pub/blob/main/','/btenneson/pub/main/'):
    if m in raw:raw=raw.split(m,1)[1]
  raw=unquote(raw).lstrip('/')
  if raw and not raw.endswith('/'):cand += [raw,'docs/'+raw]
 for p in dict.fromkeys(cand):
  b=git_bytes(p)
  if b is not None:return b,p
 return None,None
def main():
 old=json.loads(subprocess.run(['git','show',f'{BASE}:docs/search-index.json'],cwd=ROOT,stdout=subprocess.PIPE,check=True).stdout)['items']
 cur=json.loads((ROOT/'scripts/publications.json').read_text())['items']
 oldsha=[];oldpath=[]
 for x in old:
  b,p=old_blob(x);oldsha.append(hashlib.sha256(b).hexdigest() if b else None);oldpath.append(p)
 edges=[]
 for i,o in enumerate(old):
  e=[]
  for j,c in enumerate(cur):
   exact=norm(o.get('title'))==norm(c.get('title'));same=bool(oldsha[i] and c.get('sha256')==oldsha[i])
   if exact or same:e.append((0 if exact else 1,j))
  edges.append([j for _,j in sorted(e)])
 match={}
 def aug(i,seen):
  for j in edges[i]:
   if j in seen:continue
   seen.add(j)
   if j not in match or aug(match[j],seen):match[j]=i;return True
  return False
 for i in sorted(range(len(old)),key=lambda i:(len(edges[i]),i)):aug(i,set())
 matched=set(match.values());unmatched=[]
 for i,x in enumerate(old):
  if i in matched:continue
  same=[c for c in cur if oldsha[i] and c.get('sha256')==oldsha[i]]
  kind=x.get('kind') or ''
  score={'Core paper':100,'Applied Data Science':90,'Experimental':75,'PDF archive':50}.get(kind,60)
  title=x.get('title') or ''
  if re.search(r'\s\([0-9]+\)$',title):score-=35
  if same and kind=='PDF archive':score-=10
  if x.get('quote'):score+=8
  unmatched.append({'score':score,'title':title,'kind':kind,'category':x.get('category'),'quote':x.get('quote'),'quote_attribution':x.get('quote_attribution'),'old_sha256':oldsha[i],'resolved_old_path':oldpath[i],'canonical_id':same[0].get('id') if same else None,'canonical_title':same[0].get('title') if same else None})
 selected=sorted(unmatched,key=lambda x:(-x['score'],x['title'].casefold()))[:20]
 excluded=sorted(unmatched,key=lambda x:(-x['score'],x['title'].casefold()))[20:]
 report={'old_count':len(old),'current_count':len(cur),'matched_old_count':len(matched),'historical_context_candidates':len(unmatched),'selected_to_restore':selected,'excluded_because_new_current_cards_are_retained':excluded}
 print(json.dumps(report,ensure_ascii=False,indent=2))
 print('RESTORE20:')
 for x in selected:print(f"- {x['kind']}: {x['title']} -> {x['canonical_id'] or 'NO CANONICAL MATCH'}")
 if len(old)!=106 or len(cur)!=86 or len(selected)!=20:raise SystemExit('unexpected catalog counts')
if __name__=='__main__':main()
