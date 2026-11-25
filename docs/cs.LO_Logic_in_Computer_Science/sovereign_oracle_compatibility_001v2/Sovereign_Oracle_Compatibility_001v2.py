"""ATLAS v2: executable finite B11 witness. Standard library only.
Not an independent proof checker for unrestricted GBG+S or deployed Picard.
Run with Python 3 (assertions enabled).
"""
from itertools import product, combinations
from dataclasses import dataclass, replace

T = frozenset({'p', 'q'})
S, P1 = 'S', 'P1'
ROLES = (S, P1)

def evaluate(phi, b):
    if phi == 'p': return int((not b) or b)
    if phi == 'q': return int(b or not b)
    raise ValueError(phi)

def check(phi, cert):
    return (isinstance(phi, str) and phi in T and type(cert) is tuple
            and len(cert) == 2 and all(type(x) is int and x in (0, 1) for x in cert)
            and cert == tuple(evaluate(phi, b) for b in (0, 1)) == (1, 1))

def donor():
    return tuple((b, evaluate('q', b)) for b in (1, 0))

def translate(rows):
    if (type(rows) is not tuple or len(rows) != 2 or
        any(type(row) is not tuple or len(row) != 2 or
            any(type(x) is not int or x not in (0, 1) for x in row) for row in rows)
        or {b for b, _ in rows} != {0, 1}):
        raise ValueError('bad native encoding')
    return tuple(v for _, v in sorted(rows))

def admitted(pairs):
    return frozenset((phi, cert) for phi, cert in pairs if check(phi, cert))

def conclusions(ledger):
    return frozenset(phi for phi, _ in ledger)

INITIAL = ('p', (1, 1))
NATIVE = donor()

def baseline():
    yield INITIAL

def upgraded():
    yield INITIAL
    yield ('q', translate(donor()))

def donor_atp():
    yield ('q', translate(donor()))

# Comparison class is fixed before gift execution.
CLASS = (baseline, upgraded, donor_atp)
K0, K1, KD = (conclusions(admitted(a())) for a in CLASS)

@dataclass(frozen=True)
class State:
    record: str
    name: str
    mode: str
    registry: frozenset
    ledger: frozenset
    roles: tuple = ROLES
    native: tuple = NATIVE
    ordinary: str = 'z'

empty = frozenset()
initial_ledger = admitted(baseline())
d0 = State('G1', 'd0', 'dormant', empty, initial_ledger)
u0 = replace(d0, record='H1', name='u0', mode='active')
d1 = replace(d0, record='G2', name='d1', registry=frozenset({'B11'}))
u1 = replace(d1, record='H2', name='u1', mode='active')
v1 = replace(u1, name='v1', ledger=admitted(upgraded()))
STATES = (d0, u0, d1, u1, v1)

def trade(state, actor):
    if (state != u1 or actor != S or state.mode != 'active' or 'B11' not in state.registry):
        return None
    try: cert = translate(state.native)
    except ValueError: return None
    if not check('q', cert): return None
    return replace(state, name='v1', ledger=state.ledger | {('q', cert)})

for phi, cert in product(sorted(T), product((0,1), repeat=2)):
    assert check(phi, cert) == (cert == (1,1))
assert NATIVE == ((1,1),(0,1))
assert not check('q', NATIVE)
assert translate(NATIVE) == (1,1)
assert check('q', translate(NATIVE))
# Exhaust all well-shaped two-row bit inputs; exactly 8 have distinct assignments.
rows = tuple(product((0,1), repeat=2))
for r in product(rows, repeat=2):
    if r[0][0] == r[1][0]:
        try: translate(r)
        except ValueError: pass
        else: raise AssertionError('duplicate assignments accepted')
    else:
        assert translate(r) == tuple(v for _,v in sorted(r))
        assert check('q', translate(r)) == all(v == 1 for _,v in r)
for bad in (None, (), ((0,1),), ((2,1),(0,1)), ((0,True),(1,1)), ((0,1,1),(1,1)), [ (0,1),(1,1) ]):
    try: translate(bad)
    except ValueError: pass
    else: raise AssertionError('malformed native encoding accepted')
for phi, cert in [('r',(1,1)), ('p',(True,1)), ('q',[1,1]), (None,(1,1)), ('p',None)]:
    assert not check(phi, cert)

# Complete finite transition relation computed, rather than copied from the table.
actual_edges = {(x.name, a, y.name) for x in STATES for a in ROLES if (y := trade(x,a)) is not None}
assert actual_edges == {('u1', S, 'v1')}
assert trade(u1,S) == v1
for x in STATES:
    assert x.roles == ROLES and x.roles.count(S) == 1 and x.ordinary == 'z'
    assert all(check(phi, cert) for phi,cert in x.ledger)
    assert x.native == NATIVE
    if x.mode == 'dormant': assert all(trade(x,a) is None for a in ROLES)
assert not any(trade(u0,a) for a in ROLES)
assert trade(u1,P1) is None
assert u0.ledger == u1.ledger == initial_ledger
assert conclusions(v1.ledger) == K1 and conclusions(u0.ledger) == K0
assert not tuple(combinations(('B11',),2))

# Outer administrative constructor: fixed singleton-domain transitions.
operations = ('announce roles', 'establish identifiers', 'announce contract',
              'install dormant target', 'announce evidence gate', 'return specification')
outer = tuple(operations[:i] for i in range(7))
def outer_move(state, actor):
    if actor != 'p0' or state not in outer[:-1]: return None
    return outer[len(state)+1]
assert sum(outer_move(x,a) is not None for x in outer for a in ('p0','p1','p2')) == 6
x = outer[0]
for _ in operations: x = outer_move(x,'p0')
assert x == outer[-1]

# Independent comparison of all four possible knowledge subsets.
def oracle(K, profiles): return not any(K < L for L in profiles)
def least(K, profiles): return all(L <= K for L in profiles)
profiles = (K0,K1,KD)
assert (K0,K1,KD) == (frozenset({'p'}),T,frozenset({'q'}))
assert not oracle(K0,profiles) and least(K1,profiles) and oracle(K1,profiles)
for flags in product((0,1),repeat=2):
    K = frozenset(p for p,b in zip(sorted(T),flags) if b)
    assert T-K1 <= T-K
# Separate fixed truth contract; same checker and programs.
T_res = T | {'r'}
assert T_res-K1 == {'r'} and T_res-K0 == {'q','r'}
assert all(T_res-K1 <= T_res-K for K in profiles)
print('PASS: 8 canonical cases; 16 native row pairs; malformed inputs;')
print('3 executed ATPs; 5 state rows; 1 legal trade; 6 constructor edges; S3;')
print('4 knowledge subsets; nonempty-residual contract.')
print('Restricted finite model only; no independent formal-proof receipt.')
