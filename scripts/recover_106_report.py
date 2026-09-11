#!/usr/bin/env python3
"""Recover the exact historical cards not represented in the current catalog."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='6a2ce29ddc308747d75ca82f58c3b35604a8b744'
def norm(s): return re.sub(r'\s+',' ',(s or '').casefold().replace('—','-').replace('–','-')).strip()
def git_bytes(path):
 p=unquote((path or '').strip())
 if not p or p.endswith('/') or p.startswith(('http://','https://')): return None
 r=subprocess.run(['git','show',f'{BASE}:{p}'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 return r.stdout if r.returncode==0 else None
def old_blob(x):
 cand=[]
 for k in ('archive_path','pdf','href','source'):
  raw=x.get(k) or ''
  if raw.startswith(('http://','https://')):
   raw=urlsplit(raw).path
   for marker in ('/btenneson/pub/blob/main/','/btenneson/pub/main/'):
    if marker in raw: raw=raw.split(marker,1)[1]
  raw=unquote(raw).lstrip('/')
  if raw and not raw.endswith('/'): cand += [raw,'docs/'+raw]
 for p in dict.fromkeys(cand):
  b=git_bytes(p)
  if b is not None:return b,p
 return None,None
def compact(x): return {k:x.get(k) for k in ('title','kind','category','href','pdf','source','archive_path','quote','quote_attribution')}
def main():
 old=json.loads(subprocess.run(['git','show',f'{BASE}:docs/search-index.json'],cwd=ROOT,stdout=subprocess.PIPE,check=True).stdout)['items']
 cur=json.loads((ROOT/'scripts/publications.json').read_text())['items']
 old_sha=[];old_path=[]
 for x in old:
  b,p=old_blob(x);old_sha.append(hashlib.sha256(b).hexdigest() if b else None);old_path.append(p)
 # Build edges. Exact historical title is strongest; identical bytes is the migration's own identity test.
 edges=[]
 for i,o in enumerate(old):
  row=[]
  for j,c in enumerate(cur):
   title=(norm(o.get('title'))==norm(c.get('title')))
   sha=bool(old_sha[i] and c.get('sha256')==old_sha[i])
   if title or sha: row.append((0 if title else 1,j))
  edges.append([j for _,j in sorted(row)])
 # Maximum bipartite matching, current card -> one historical card.
 match={}
 def aug(i,seen):
  for j in edges[i]:
   if j in seen:continue
   seen.add(j)
   if j not in match or aug(match[j],seen):match[j]=i;return True
  return False
 # Constrained items first, then exact-title-rich items.
 order=sorted(range(len(old)),key=lambda i:(len(edges[i]),0 if any(norm(old[i].get('title'))==norm(cur[j].get('title')) for j in edges[i]) else 1,i))
 for i in order:aug(i,set())
 matched_old=set(match.values())
 unmatched=[]
 for i,x in enumerate(old):
  if i in matched_old:continue
  rec=compact(x);rec['old_sha256']=old_sha[i];rec['resolved_old_path']=old_path[i]
  rec['same_bytes_current']=[{'title':c.get('title'),'id':c.get('id')} for c in cur if old_sha[i] and c.get('sha256')==old_sha[i]]
  unmatched.append(rec)
 report={'baseline_commit':BASE,'old_count':len(old),'current_count':len(cur),'matched_old_count':len(matched_old),'unmatched_old_count':len(unmatched),'unmatched_old_cards':unmatched}
 print(json.dumps(report,ensure_ascii=False,indent=2))
 print(f"RECOVERY: old={len(old)} current={len(cur)} matched={len(matched_old)} unmatched={len(unmatched)}")
 if len(old)!=106:raise SystemExit('baseline is not 106')
 if len(matched_old)!=len(cur):raise SystemExit(f'Only {len(matched_old)} of {len(cur)} current cards map to the 106-item baseline; inspect before restoration')
 if len(unmatched)!=20:raise SystemExit(f'Expected exactly 20 historical cards to restore; got {len(unmatched)}')
if __name__=='__main__':main()
