#!/usr/bin/env python3
"""Finite illustrative certificate tests for Two Armies of One v0.3.
NOT a general formal proof checker or a theorem prover.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Node:
    formula: object
    kind: str
    inputs: tuple=()

P='p'; L='ell'; T='t'
def imp(a,b):return ('imp',a,b)
H={P,imp(P,L),imp(L,T)}

def verify(nodes:tuple,allowed_h=frozenset(H),allowed_o=frozenset(),max_mp=None):
    mp_count=0
    if not nodes:return False
    for i,node in enumerate(nodes):
        if node.kind=='H':
            if node.formula not in allowed_h or node.inputs:return False
        elif node.kind=='OPEN':
            if node.formula not in allowed_o or node.inputs:return False
        elif node.kind=='MP':
            if len(node.inputs)!=2 or not all(isinstance(k,int) and 0<=k<i for k in node.inputs): return False
            left,right=[nodes[k].formula for k in node.inputs]
            if right!=imp(left,node.formula):return False
            mp_count+=1
        else:return False
    return max_mp is None or mp_count<=max_mp

pi=(Node(P,'H'),Node(imp(P,L),'H'),Node(L,'MP',(0,1)))
rho=(Node(L,'OPEN'),Node(imp(L,T),'H'),Node(T,'MP',(0,1)))
composite=(Node(P,'H'),Node(imp(P,L),'H'),Node(L,'MP',(0,1)),Node(imp(L,T),'H'),Node(T,'MP',(2,3)))
neg_wrong_ports=(Node(P,'H'),Node(imp(P,L),'H'),Node(L,'MP',(1,0)))
neg_wrong_formula=(Node(P,'H'),Node(imp(P,L),'H'),Node(T,'MP',(0,1)))
neg_unclosed=(Node(L,'OPEN'),Node(imp(L,T),'H'),Node(T,'MP',(0,1)))
neg_cycle=(Node(P,'H'),Node(imp(P,L),'H'),Node(L,'MP',(2,1)))
checks={
    'full verifier accepts Probe H|-L':verify(pi),
    'full verifier accepts Scout H,L|-T':verify(rho,allowed_o={L}),
    'full verifier accepts composed H|-T':verify(composite),
    'sound one-MP-cap verifier accepts Probe':verify(pi,max_mp=1),
    'sound one-MP-cap verifier accepts Scout':verify(rho,allowed_o={L},max_mp=1),
    'sound one-MP-cap verifier rejects composite':not verify(composite,max_mp=1),
    'reject swapped MP ports':not verify(neg_wrong_ports),
    'reject incorrect MP conclusion':not verify(neg_wrong_formula),
    'reject unresolved open assumption':not verify(neg_unclosed),
    'reject backward/cyclic node index':not verify(neg_cycle),
}
for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
assert all(checks.values())
print('10/10 illustrative checks passed; this does not verify the general theorems.')
