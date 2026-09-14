# From Search Dynamics to Semi-Ideal Computers - v0.2

**Primary arXiv classification:** cs.LO (Logic in Computer Science)  
**Secondary:** cs.AI (Artificial Intelligence)  
**Cross-list candidate:** math.CO (Combinatorics / graph-theoretic methods)

Version 0.2 keeps the paper **maze first** but adds a prominent big-picture section before the maze primer. The central diagnosis is that classical shortest-path algorithms are not the main bottleneck: an explicitly presented maze is comparatively well behaved, while an implicitly generated theorem maze may contain exponentially or worse many proof states. The research program is therefore organized around **shrinking the maze before searching it**.

The new priority ranking puts the strongest near-term emphasis on: (1) verifier-respecting quotient spaces, symmetry and partial-order reduction, and proof-DAG canonicalization; (2) admissible abstraction combined with A*/branch-and-bound and a verified Proof-Horizon incumbent; (3) conservative compilation, verified shared landmarks, and dynamic programming over repeated proof structure; and (4) min-plus/tropical path algebra for exact rational costs. Learned cost-to-go, portfolio/Hilbert ordering, IFS/fractional iteration, and reflective meta-ATP are retained but placed later according to how directly they attack state explosion and how much exact theory currently supports them.

A new abstract-distance proposition formalizes the most promising synthesis. If an abstract/relaxed theorem maze maps every concrete route to one of no greater cost, then its exact distance-to-exit is an admissible lower bound. With a verified incumbent of cost `B`, the improving search may be restricted to states satisfying `g(v)+h(v)<B`. Quotienting reduces duplicates first; the abstract heuristic supplies the lower bound; the incumbent supplies the upper bound.

The new min-plus section observes that sequential edge costs compose by ordinary addition while alternative successful proofs are compared by minimum. On finite/effectively proper layers, the weighted Proof Horizon is therefore an algebraic-path value over the min-plus semiring. This is a structural unification, not a claim that tropical algebra by itself removes state explosion.

The rest of the bundle retains the v0.1 maze primer, theorem-tour quotient, rational graph-search transfer principles, SIC/ATP/ALD/AMLD lift, benchmark disclaimers, reflective construction, and DATA case study. Citations to Brian Tenneson's earlier work use live GitHub references; the sequel does not cite itself as a bibliography item.

Compile `main.tex` with pdfLaTeX.
