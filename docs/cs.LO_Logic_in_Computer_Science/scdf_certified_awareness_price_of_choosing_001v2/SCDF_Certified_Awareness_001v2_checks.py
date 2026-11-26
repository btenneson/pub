"""Finite model checks for The Price of Knowing How to Improve (001v2).
No external checker, API, timing benchmark, or deployed federation.
"""
from itertools import product, combinations
from functools import lru_cache
from fractions import Fraction as F
import json
counts = dict(coalitions=0, adaptive_contracts=0, receipt_guards=0, clock_counts=0, recurrence_gaps=0, hidden_worker_cases=0)

def costs(x,h,l,w):
    p=sum(x)%2
    return h, l if p==0 else w, l if p==1 else w

def partitions(states, inds):
    parts={}
    for x in states: parts.setdefault(tuple(x[i] for i in inds),[]).append(x)
    return tuple(tuple(xs) for xs in parts.values())

def stop(E,h,l,w,robust):
    a=list(zip(*(costs(x,h,l,w) for x in E)))
    return min(max(v) if robust else F(sum(v),len(v)) for v in a)

def dp(states,n,h,l,w,k,cap,robust):
    @lru_cache(None)
    def value(E,U):
        opt=stop(E,h,l,w,robust)
        if len(U)<=n-cap:return opt
        for i in U:
            parts=partitions(E,(i,)); rest=tuple(j for j in U if i!=j)
            sub=[value(e,rest) for e in parts]
            q=max(sub) if robust else sum(F(len(e),len(E))*v for e,v in zip(parts,sub))
            opt=min(opt,k[i]+q)
        return opt
    return value(states,tuple(range(n)))

for n in range(2,8):
    states=tuple(product((0,1),repeat=n))
    for size in range(n+1):
        for inds in combinations(range(n),size):
            cells=partitions(states,inds)
            expected=sum(F(len(e),len(states))*stop(e,8,2,14,False) for e in cells)
            worst=max(stop(e,8,2,14,True) for e in cells)
            assert expected==worst==(2 if size==n else 8)
            counts['coalitions']+=1
    for h,l,w in [(8,2,14),(5,1,10),(4,0,8)]:
        for k in [(0,)*n,(1,)*n,tuple(i%3 for i in range(n))]:
            for robust in (False,True):
                assert dp(states,n,h,l,w,k,n-1,robust)==h
                v=dp(states,n,h,l,w,k,n,robust)
                assert v==min(h,l+sum(k))
                for K in (0,1,5):
                    assert min(h,K+v)==min(h,K+l+sum(k))
                    counts['adaptive_contracts']+=1

# Receipt checker: immutable source ID, current epoch, scope, authorization,
# observed bit verified against trusted local state, no object-store writes.
def accept_receipt(x, version, allowed, r):
    i,b,epoch,scope,source=r
    return (type(i) is int and 0<=i<len(x) and i in allowed
            and source==f'agent:{i}' and epoch==version and scope=='orientation'
            and type(b) is int and b in (0,1) and b==x[i])
for x in product((0,1),repeat=3):
    for i in range(3):
        r=(i,x[i],1,'orientation',f'agent:{i}')
        for candidate,allowed,want in [(r,{0,1,2},True),((i,1-x[i],1,'orientation',f'agent:{i}'),{0,1,2},False),((i,x[i],0,'orientation',f'agent:{i}'),{0,1,2},False),((i,x[i],1,'object',f'agent:{i}'),{0,1,2},False),((i,x[i],1,'orientation','forged'),{0,1,2},False),(r,set(),False)]:
            assert accept_receipt(x,1,allowed,candidate)==want
            counts['receipt_guards']+=1

def v2(n):return (n&-n).bit_length()-1
def owner(t,j=None):
    if t%2==0:return -1
    i=v2((t+1)//2)
    return j if j is not None and i==0 else 0 if j is not None and i==j else i
for j in range(1,9):
    for swap in (None,j):
        slots=[[] for _ in range(9)]
        for t in range(2**12):
            i=owner(t,swap)
            if 0<=i<9:slots[i].append(t+1)
        for i,ts in enumerate(slots):
            r=(j if i==0 else 0 if i==j else i) if swap else i
            assert all(b-a==2**(r+2) for a,b in zip(ts,ts[1:]))
            counts['recurrence_gaps']+=1
        for m in range(1,min(len(slots[j]),50)+1):
            d=2**((0 if swap else j)+1)*(2*m-1)
            assert slots[j][m-1]==d
            counts['clock_counts']+=1
for x in product((0,1),repeat=3):
    j=1+sum(x)%2
    for m in range(2,21):
        d=2*(2*m-1)
        for swap in (None,1,2):
            served=sum(owner(t,swap)==j for t in range(d))
            assert (served>=m)==(swap==j)
            counts['hidden_worker_cases']+=1

# Independently enumerate all deterministic decision-policy cost vectors on
# two-bit worlds. Unlike the scalar Bellman recursion, enumerate every
# possible stop/action and combination of branch policies before minimizing.
counts.update(general_tree_cases=0, interval_cases=0, mixed_history_cases=0)
from random import Random
rng=Random(1402)
worlds=tuple(product((0,1),repeat=2))
weights=(1,2,3,4)
for trial in range(40):
    table=tuple(tuple(rng.randrange(0,15) for _ in range(3)) for x in worlds)
    fees=tuple(rng.randrange(0,5) for _ in range(2))
    def enumerate_vectors(E,U):
        ans={tuple(table[x][a] for x in E) for a in range(3)}
        for i in U:
            cells=[tuple(x for x in E if worlds[x][i]==z) for z in (0,1)]
            cells=[c for c in cells if c]
            for choices in product(*(enumerate_vectors(c,tuple(j for j in U if j!=i)) for c in cells)):
                d={x:v+fees[i] for c,vec in zip(cells,choices) for x,v in zip(c,vec)}
                ans.add(tuple(d[x] for x in E))
        return ans
    def objective(E,vec,robust):
        return max(vec) if robust else F(sum(weights[x]*v for x,v in zip(E,vec)),sum(weights[x] for x in E))
    def bell(E,U,robust):
        best=min(objective(E,[table[x][a] for x in E],robust) for a in range(3))
        for i in U:
            cells=[tuple(x for x in E if worlds[x][i]==z) for z in (0,1)]
            cells=[c for c in cells if c]
            vals=[bell(c,tuple(j for j in U if j!=i),robust) for c in cells]
            cost=max(vals) if robust else sum(F(sum(weights[x] for x in c),sum(weights[x] for x in E))*v for c,v in zip(cells,vals))
            best=min(best,fees[i]+cost)
        return best
    E=tuple(range(4)); U=(0,1)
    vecs=enumerate_vectors(E,U)
    for robust in (False,True):
        assert min(objective(E,v,robust) for v in vecs)==bell(E,U,robust)
        counts['general_tree_cases']+=1
    lo=tuple(tuple(max(0,v-rng.randrange(5)) for v in row) for row in table)
    hi=tuple(tuple(v+rng.randrange(5) for v in row) for row in table)
    def fixed_value(tab,J,robust):
        cells={}
        for x,w in enumerate(worlds):cells.setdefault(tuple(w[i] for i in J),[]).append(x)
        vs=[(sum(weights[x] for x in c),min(objective(c,[tab[x][a] for x in c],robust) for a in range(3))) for c in cells.values()]
        return max(v for _,v in vs) if robust else sum(F(w,sum(weights))*v for w,v in vs)
    for J in ((),(0,),(1,),(0,1)):
        for robust in (False,True):
            assert fixed_value(lo,J,robust)<=fixed_value(table,J,robust)<=fixed_value(hi,J,robust)
            counts['interval_cases']+=1

# Explicit finite transition trial. Receipt source and gate are modeled by
# trusted local state, not cryptographic authentication or a proof kernel.
# A real authority is not inferred from this stipulated transition system.
def object_check(proof):
    return proof==('s','s->t','t')
for x in product((0,1),repeat=3):
    for gift in (False,True):
        version=int(gift); cap=3 if gift else 2
        def explore(J,L,B,c):
            assert len(J)==len(L) and len(J)<=cap and B==frozenset()
            for a in (0,1,2): # 2 is slow
                charge=8 if a==2 else (2 if a==sum(x)%2 else 14)
                proof=('s','s->t','t')
                assert object_check(proof) and not object_check(tuple(str(r) for r in L))
                bank=B|{'t'}; total=c+charge
                assert bank=={'t'} and total==int(gift)+len(J)+charge
                counts['mixed_history_cases']+=1
            if len(J)<cap:
                for i in range(3):
                    if i in J:continue
                    r=(i,x[i],version,'orientation',f'agent:{i}')
                    assert accept_receipt(x,version,set(range(3))-set(J),r)
                    explore(J+(i,),L+(r,),B,c+1)
        explore((),(),frozenset(),int(gift))
print(json.dumps({'status':'PASS','counts':counts,'total_grouped_checks':sum(counts.values()),'scope':'finite mathematical model checks; not independent formal verification'},indent=2))
