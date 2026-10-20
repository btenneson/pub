"""Reproducible finite-state checks for DNI v0.2.
These finite tests supplement mathematical proofs.
"""
from itertools import product
from functools import lru_cache
from fractions import Fraction
N=3
options=[tuple(j for j in range(N) if mask & (1<<j)) for mask in range(1,1<<N)]
def cycle_vertices(graph):
    result=set()
    for start in range(N):
        if start in graph[start]:
            result.add(start);continue
        stack=[(child,{start,child}) for child in graph[start] if child!=start]
        while stack:
            node,seen=stack.pop()
            if start in graph[node]:
                result.add(start);break
            for next_node in graph[node]:
                if next_node not in seen:
                    stack.append((next_node,seen|{next_node}))
    return result
def prefix_counts(graph,max_length):
    counts=[1]*N
    totals=[sum(counts)]
    for _ in range(1,max_length):
        counts=[sum(counts[z] for z in graph[y]) for y in range(N)]
        totals.append(sum(counts))
    return totals
passing=failing=0
for graph in product(options,repeat=N):
    cyclic=cycle_vertices(graph)
    condition=all(len(graph[v])==1 for v in cyclic)
    totals=prefix_counts(graph,11)
    if condition:
        passing+=1
        @lru_cache(None)
        def count_paths(v):
            return 1 if v in cyclic else sum(count_paths(z) for z in graph[v])
        assert totals[-1]==totals[-2]==sum(map(count_paths,range(N)))
    else:
        failing+=1
        assert totals[-1]>totals[1]
assert (passing,failing)==(39,304)
X,Y=range(4),range(3)
f=[2,3,2,3]
R=[0,0,1,2]
K=[[Fraction(0),Fraction(1,3),Fraction(2,3)],
   [Fraction(0),Fraction(1),Fraction(0)],
   [Fraction(0),Fraction(0),Fraction(1)]]
E=[[Fraction(1,3),Fraction(2,3),Fraction(0),Fraction(0)],
   [Fraction(0),Fraction(0),Fraction(1),Fraction(0)],
   [Fraction(0),Fraction(0),Fraction(0),Fraction(1)]]
for y in Y:
    for z in Y:
        assert sum(E[y][x] for x in X if R[x]==z)==(1 if y==z else 0)
    for x in X:
        assert sum(E[y][u] for u in X if f[u]==x)==sum(K[y][z]*E[z][x] for z in Y)
print('PASS: all 343 three-vertex nonempty successor graphs checked.')
print('  good graph supports:',passing,'bad graph supports:',failing)
print('PASS: four-hidden-state witness exactly satisfies S1 and S2.')
