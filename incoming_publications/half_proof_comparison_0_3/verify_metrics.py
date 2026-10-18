from pathlib import Path
s = Path('Exact_Addressing_3_3_2_Capstone_Section_15.tex').read_text()
a = s.index(r'\begin{proof}[Proof of Theorem')
b = s.index(r'\end{proof}', a)
reference = s[s.index('\n',a)+1:b]
candidate = Path('candidate_proof.tex').read_text()
t4 = candidate.index(r'\medskip\noindent\textbf{T4:')
assert len(reference.split()) == 395
assert len(candidate.split()) == 515
assert len(candidate[t4:].split()) == 333
print('Original source tokens:', len(reference.split()))
print('Visible prefix:', 197, '(', round(100*197/395,2), '%)')
print('Hidden suffix:', 198)
print('Normalized candidate tokens:',len(candidate.split()))
print('Normalized candidate continuation tokens:',len(candidate[t4:].split()))
try:
    import sympy as z
    N,g,p,q,p0,g0,a0,A,a3,L,K=z.symbols('N g p q p0 g0 a0 A a3 L K')
    G=p*(g+1)/2+(1-p)*(g+(N-g+1)/2)
    assert z.simplify(G-(N+g+1-p*N)/2)==0
    assert z.simplify((N+1)/2-G-(p*N-g)/2)==0
    b=(p0*N-g0)/2-A*L-a3
    assert z.simplify(K*L*b-a0*N*L-L*((K*p0/2-a0)*N-K*A*L-K*g0/2-K*a3))==0
    print('Three algebraic identities: verified with SymPy')
except ImportError:
    print('SymPy unavailable; algebra verification skipped.')
