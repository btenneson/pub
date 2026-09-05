#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'search-index.json'
HOME=ROOT/'docs'/'index.html'
TITLE='The Invariant Core and the Geometry of Settlement'
READER='papers/invariant_core_geometry_settlement/'
PDF=READER+'The_Invariant_Core_and_the_Geometry_of_Settlement.pdf'
SOURCE=READER+'source.html'
ARCHIVE='cs.LO_Logic_in_Computer_Science/The_Invariant_Core_and_the_Geometry_of_Settlement.pdf'
QUOTE=('The deepest potential contribution of this combined framework is therefore not a claim that any one mechanism '
       'makes theorem proving faster. It is a framework in which such speedups can be located, decomposed, certified '
       'where possible, and experimentally attributed.')

def sync(items):
    page=HOME.read_text(encoding='utf-8')
    data=json.dumps(items,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    page,n=re.subn(r'const DATA=.*?;\nconst q=',lambda _m:'const DATA='+data+';\nconst q=',page,count=1,flags=re.S)
    if n!=1:
        raise SystemExit('could not update homepage DATA payload')
    HOME.write_text(page,encoding='utf-8')

def main():
    payload=json.loads(INDEX.read_text(encoding='utf-8'))
    items=[dict(x) for x in payload['items']]
    matches=[x for x in items if x.get('title')==TITLE or x.get('archive_path')==ARCHIVE or x.get('href')==READER]
    if len(matches)>1:
        raise SystemExit(f'duplicate invariant-core entries: {len(matches)}')
    if matches:
        inv=matches[0]; items.remove(inv)
    else:
        inv={}
    inv.update({
        'title':TITLE,'kind':'Core paper','category':'Research Papers','tags':[],
        'href':READER,'pdf':PDF,'source':SOURCE,'archive_path':ARCHIVE,
        'search':' '.join([TITLE,'Trading Induction Formal Self-Awareness Hyperfinite Epistemic Horizons Counterfactual Dreaming DATA MIND Research Papers',ARCHIVE,QUOTE,'Brian Tenneson']),
        'quote':QUOTE,'quote_attribution':'Brian Tenneson'
    })
    # Story remains card #1. Put Invariant Core immediately after it, otherwise first.
    pos=1 if items and items[0].get('title')=='The Gedanbedai of Wake Island' else 0
    items.insert(pos,inv)
    payload={'schema_version':1,'count':len(items),'items':items}
    INDEX.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sync(items)
    print('Invariant Core card position:',pos+1)

if __name__=='__main__': main()
