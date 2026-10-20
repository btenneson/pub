"""Independent four-vertex graph check for DNI v0.2."""
from itertools import product
n=4
possible_rows=[tuple(j for j in range(n) if mask & (1<<j)) for mask in range(1,1<<n)]
finite_count=infinite_count=0
for graph in product(possible_rows,repeat=n):
    reachable=[[j in graph[i] for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reachable[i][j] |= reachable[i][k] and reachable[k][j]
    on_cycle=[reachable[i][i] for i in range(n)]
    finite_condition=all(not on_cycle[i] or len(graph[i])==1 for i in range(n))
    counts=[1]*n
    totals=[sum(counts)]
    for _ in range(11):
        counts=[sum(counts[z] for z in graph[y]) for y in range(n)]
        totals.append(sum(counts))
    if finite_condition:
        finite_count+=1
        assert totals[-1]==totals[-2]
    else:
        infinite_count+=1
        assert totals[-1]>totals[3]
assert (finite_count,infinite_count)==(904,49721)
print(f'PASS: all {finite_count+infinite_count:,} four-state support graphs')
print(f'      finite graph cases: {finite_count}; infinite graph cases: {infinite_count}')
