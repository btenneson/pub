# From Search Dynamics to Semi-Ideal Computers - v0.1

**Primary arXiv classification:** cs.LO (Logic in Computer Science)  
**Secondary:** cs.AI (Artificial Intelligence)  
**Cross-list candidate:** math.CO (Combinatorics / graph-theoretic methods)

The paper is now organized **maze first**. It begins with the minimum graph theory needed for the sequel: directed mazes, entrances and exits, paths/tours, sparse versus dense graphs, unit and exact rational edge weights, BFS/DFS/Dijkstra/A*/DAG shortest paths, the usual explicit-graph worst-case bounds, and the usual exponential tree-search bounds for implicitly generated mazes. It then constructs the theorem maze whose vertices are cumulative proof states and whose edges are verified inference-rule applications.

The unit normalization `w(e)=1` makes shortest maze distance equal shortest inference count. Exact nonnegative rational weights are treated as costs, not as fractional logical inferences. Fractional iteration/continuous-semigroup ideas are postponed to the later dynamical-control layer.

After the maze primer the source bundle develops rationally weighted theorem mazes, exact graph-search transfer principles, theorem-tour quotients, Horizon/Depths search-space reductions, cumulative verified histories and the SIC lift, ATP/ALD/AMLD specializations, benchmarks with explicit disclaimers, reflective meta-ATPs, and DATA as a distinguished case.

All external algorithmic sources are cited. Citations to Brian Tenneson's earlier research use live GitHub references. This sequel does not cite itself as a bibliography item.

The rational-weight restriction is deliberate: weighted-maze algorithms are imported into ATP search only where their correctness hypotheses hold for exact nonnegative rational edge weights and the corresponding graph class. Logical acceptance remains verifier-gated.

The L*=100 table is explicitly labeled as a synthetic dry benchmark from the Proof Horizon technical companion, not a production benchmark or a claim of general superiority on natural mathematics.

Compile `main.tex` with pdfLaTeX.
