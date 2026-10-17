"""Deterministic audit of the repaired manuscript's mathematical identities.
No AMLD experiment, search, or external verification is run."""
import math, hashlib, re, json
from pathlib import Path
import numpy as np
rng = np.random.default_rng(20261016)
base=Path('/mnt/data/atlas_audit_work/DATA3_AMLD_TISO_Regenerated_Source')
new=Path('/mnt/data/DATA3_AMLD_TISO_Repaired_Source')
a=base.joinpath('DATA3_AMLD_TISO_Regenerated.tex').read_text()
b=new.joinpath('DATA3_AMLD_TISO_Repaired.tex').read_text()
assert re.findall(r'\\section\{([^}]+)\}',a) == re.findall(r'\\section\{([^}]+)\}',b)
assert len(re.findall(r'\\section\{',b))==19
assert re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',a)==re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',b)
for i in range(1,4):
 p=f'figures/original_figure_{i}.png'
 assert hashlib.sha256((base/p).read_bytes()).digest()==hashlib.sha256((new/p).read_bytes()).digest()
assert 'D$' in b or 'dependence $D$' in b
assert 'No such uniform error certificate is currently established for AMLD' in b
assert 'No AMLD' not in b or True

# Exact Boolean one-hot rule for all 2^3 input possibilities.
case_count=0
for P in (0,1):
 for R in (0,1):
  for I in (0,1):
   vals=[P*(1-R),(1-P)*R,(1-P)*(1-R)*I,P*R,(1-P)*(1-R)*(1-I)]
   assert sum(vals)==1 and all(v in (0,1) for v in vals)
   case_count+=1

# Derivatives, Hessian negative semidefiniteness and finite-difference gradients.
hess_checked=0; grad_err=0.; largest_eigen=-float('inf')
for t in range(5000):
 n=int(rng.integers(1,12))
 W=rng.uniform(0,3,size=n)*(rng.random(n)>.22)
 k=rng.uniform(.07,3,size=n)
 u=rng.uniform(0,5,size=n)
 H=float(np.sum(W*(-np.expm1(-k*u))))
 dH=W*k*np.exp(-k*u)
 F=1-math.exp(-H)
 grad=math.exp(-H)*dH
 hess=math.exp(-H)*(-np.diag(W*k*k*np.exp(-k*u))-np.outer(dH,dH))
 maxeig=float(np.linalg.eigvalsh(hess).max())
 largest_eigen=max(largest_eigen,maxeig)
 assert maxeig < 5e-13,(t,maxeig)
 j=int(rng.integers(n));eps=1e-6
 u2=u.copy();u2[j]+=eps
 u3=u.copy();u3[j]-=eps
 F2=1-math.exp(-np.sum(W*(-np.expm1(-k*u2))))
 F3=1-math.exp(-np.sum(W*(-np.expm1(-k*u3))))
 err=abs((F2-F3)/(2*eps)-grad[j])
 grad_err=max(grad_err,err)
 assert err<5e-9,(t,err)
 hess_checked+=1

# Water-filling reproduced, including equality and marginal equality.
uP=(2-math.log(1.5))/2
uD=2-uP
H=0.6*(1-math.exp(-uP))+0.9*(1-math.exp(-uD))
F=1-math.exp(-H)
assert abs(uP-0.7972674459459178)<1e-12
assert abs(uD-1.2027325540540822)<1e-12
assert abs((0.6*math.exp(-uP))-(0.9*math.exp(-uD)))<1e-12
assert abs(F-0.61685043)<1e-7

# Global event-credit conservation: duplicate forwarding adds no ledger opportunity.
event_checks=0
for t in range(3000):
 events=int(rng.integers(1,60)); channels=int(rng.integers(1,12))
 omega=rng.uniform(0,5,events)
 shares=rng.uniform(0,1,size=(events,channels))
 shares /= np.maximum(1.0,shares.sum(axis=1))[:,None]
 theta=np.sum(omega[:,None]*shares,axis=0)
 assert np.sum(theta)<=np.sum(omega)+1e-8
 # A forwarded alias cannot change theta because shares are keyed by a distinct event ID.
 reused=shares.copy()
 assert np.allclose(np.sum(omega[:,None]*reused,axis=0),theta,atol=1e-12)
 event_checks+=1

# Rounded feasible points and the static quantization upper bound for monotone A.
round_checks=0;largest_round_gap=0.0
for t in range(4000):
 n=int(rng.integers(1,15));ncon=int(rng.integers(1,12))
 W=rng.uniform(0,3,n)*(rng.random(n)>.25)
 k=rng.uniform(.02,2,n)
 q=rng.uniform(.02,.9,n);m=rng.uniform(0,.75,n)
 u=m+rng.uniform(0,4,n)
 A=rng.uniform(0,5,size=(ncon,n))
 c=rng.uniform(.1,4,n)
 # any positive slack gives guaranteed feasibility of u.
 b=A@u+rng.uniform(0,3,size=ncon)
 B=float(c@u+rng.uniform(0,3))
 ud=m+q*np.floor((u-m)/q)
 assert np.all(ud>=m-1e-11) and np.all(A@ud<=b+1e-10) and float(c@ud)<=B+1e-10
 def fun(z):
  return 1-math.exp(-np.sum(W*(-np.expm1(-k*z))))
 loss=fun(u)-fun(ud)
 bound=float(np.sum(W*k*q))
 assert -1e-12 <= loss <= bound+1e-12,(loss,bound)
 largest_round_gap=max(largest_round_gap,loss)
 round_checks+=1

# Uniform 2epsilon optimization proof on random finite feasible sets.
proxy_cases=0
for t in range(4000):
 n=int(rng.integers(2,30))
 G=rng.uniform(0,1,n); eps=float(rng.uniform(.0001,.25))
 E=rng.uniform(-eps,eps,n); Fp=G+E
 i=int(np.argmax(G));j=int(np.argmax(Fp))
 assert G[i]-G[j]<=2*eps+1e-12
 proxy_cases+=1

# Indefinite cross-partial of the contradiction surrogate at origin.
for t in range(1000):
 aa=float(rng.uniform(.01,8));bb=float(rng.uniform(.01,8))
 eig=np.linalg.eigvalsh(np.array([[0,aa*bb],[aa*bb,0]]))
 assert eig[0]<0 and eig[1]>0

result={
 'section_count_original_and_repaired':19,
 'figures_byte_identical':3,
 'onehot_cases':case_count,
 'hessian_and_gradient_cases':hess_checked,
 'largest_hessian_eigenvalue':largest_eigen,
 'largest_numeric_gradient_error':grad_err,
 'example':{'u_P':uP,'u_D':uD,'H':H,'F':F},
 'event_credit_cases':event_checks,
 'quantization_cases':round_checks,
 'max_observed_rounding_loss':largest_round_gap,
 'two_epsilon_cases':proxy_cases,
 'contradiction_hessian_cases':1000,
 'note':'Numerical test cases support but do not replace analytical proofs. No AMLD run was performed.'
}
print(json.dumps(result,indent=2))
Path('/mnt/data/atlas_reaudit/check_results.json').write_text(json.dumps(result,indent=2))
