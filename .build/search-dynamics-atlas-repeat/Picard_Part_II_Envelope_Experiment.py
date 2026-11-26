"""Exhaustive finite proof-maze model; Python standard library only."""
from itertools import product
from collections import Counter
import csv
from pathlib import Path
V = ('s','a','b','z')
E = [('s','z',2),('s','b',1),('b','z',1),('a','b',1),('b','a',1),('s','a',2),('s','a',3),('a','z',3)]
U=set(range(6)); known={6,7}

def optimistic(edges):
    # enumerate simple paths and break ties lexicographically by edge ID
    def visit(v, seen, cost, path):
        if v=='z':
            yield cost,path
            return
        for i in sorted(edges):
            a,b,w=E[i]
            if a==v and b not in seen:
                yield from visit(b,seen|{b},cost+w,path+(i,))
    return min(visit('s',{'s'},0,()),default=(float('inf'),()))

def actual_distance(edges):
    # independent Bellman-Ford relaxation, not path enumeration
    d={v:float('inf') for v in V}; d['s']=0
    for _ in range(len(V)-1):
        for i in sorted(edges):
            a,b,w=E[i];d[b]=min(d[b],d[a]+w)
    return d['z']

def run(actual,active):
    legal=known.copy();negative=set(); q=0
    while True:
        low,path=optimistic(known|U-negative)
        high,_=optimistic(legal)
        assert low<=actual_distance(actual)<=high
        if low==high:return q,low
        unresolved=U-legal-negative
        i=min(set(path)&unresolved) if active else min(unresolved)
        if i in actual:legal.add(i)
        else:negative.add(i)
        q+=1
        assert q<=len(U)

def main():
    rows=[]
    for mask in range(64):
        actual=known|{i for i in U if mask>>i&1}
        a,x=run(actual,True); b,y=run(actual,False);z=actual_distance(actual)
        assert x==y==z
        rows.append((mask,z,a,b))
    out=Path(__file__).with_name('Picard_Part_II_Envelope_Experiment.csv')
    with out.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['mask','optimal_cost','active_queries','fixed_queries']);w.writerows(rows)
    for j in (2,3):print(j, 'total',sum(r[j] for r in rows),'min',min(r[j] for r in rows),'max',max(r[j] for r in rows),'counts',dict(sorted(Counter(r[j] for r in rows).items())))
    print('active wins/ties/losses',sum(r[2]<r[3] for r in rows),sum(r[2]==r[3] for r in rows),sum(r[2]>r[3] for r in rows))
    print('optimal costs',dict(sorted(Counter(r[1] for r in rows).items())))
if __name__=='__main__':main()
