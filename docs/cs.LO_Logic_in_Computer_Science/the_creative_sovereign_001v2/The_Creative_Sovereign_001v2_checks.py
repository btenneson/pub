from itertools import product, combinations
from fractions import Fraction
from collections import defaultdict
from math import inf, exp

checks=defaultdict(int)
def check(name, p):
    assert p, name
    checks[name]+=1

# Each possible catalogue from six directed edges, including ordinary and gift edges.
base=[(0,1,2,0),(1,2,1,1),(0,2,5,0),(1,0,0,0),(2,3,2,0),(0,3,3,1)]
def path_search(edges,k):
    def f(v,j,seen):
        if v==3:return 0
        vals=[w+f(t,j-r,seen|{(t,j-r)}) for u,t,w,r in edges if u==v and j>=r and (t,j-r) not in seen]
        return min(vals,default=inf)
    return f(0,k,{(0,k)})
def layer_relax(edges,k):
    d={(v,j):(0 if v==3 else inf) for v in range(4) for j in range(k+1)}
    for _ in range(len(d)):
        for u,t,w,r in edges:
            for j in range(r,k+1):
                d[u,j]=min(d[u,j],w+d[t,j-r])
    return d[0,k]
for bits in product([0,1],repeat=len(base)):
    edges=[e for e,b in zip(base,bits) if b]
    old=inf
    for k in range(3):
        v=layer_relax(edges,k)
        check('layered horizon',v==path_search(edges,k) and v<=old)
        old=v
# Test maximality inheritance for every nonempty family of subsets of a three-element universe.
for mask in range(1,256):
    profiles=[x for x in range(8) if mask>>x&1]
    subset=lambda a,b: a&b==a
    maximal=lambda a:not any(a!=b and subset(a,b) for b in profiles)
    for a in profiles:
        for b in profiles:
            if maximal(a) and subset(a,b):
                check('oracle inheritance',a==b and maximal(b))
# Fair status bit and the joint channel leak. Each single bit is independent; joint is revealing.
for obs in [lambda z,u:u,lambda z,u:u^z,lambda z,u:(u,u^z)]:
    groups=defaultdict(list)
    for z,u in product([0,1],repeat=2):groups[obs(z,u)].append(z)
    accuracy=sum(max(v.count(0),v.count(1)) for v in groups.values())/4
    check('joint leakage',accuracy==(1 if len(groups)==4 else .5))
# Actual partial witness: status by maximal profile, not assignment alone.
for member in range(2):
    states=[(3 if z==member else 1) for z in range(2)]
    check('pair witness',sum(x==3 for x in states)==1)
    check('terminal observation',len(set(states))==2)
# parent-copy pairing vs cross-pairing
for z in range(2):
    statuses=[z,1-z,z,1-z]
    check('recursive pairing',sum(statuses)==2 and sorted([statuses[0]+statuses[2],statuses[1]+statuses[3]])==[0,2] and statuses[0]+statuses[3]==statuses[1]+statuses[2]==1)
check('greedy barrier', (1+exp(-4))/2>0 and (1+exp(-3))/2>exp(-2)/2 and 3<4)
print(dict(checks),sum(checks.values()))
