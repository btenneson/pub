# From Search Dynamics to Semi-Ideal Computers - v0.2.1

**Primary arXiv classification:** cs.LO (Logic in Computer Science)  
**Secondary:** cs.AI (Artificial Intelligence)  
**Cross-list candidate:** math.CO (Combinatorics / graph-theoretic methods)

Version 0.2.1 keeps the paper **maze first** and retains the v0.2 priority on shrinking the implicit theorem maze before trying to outrun it. The core exact program remains verifier-respecting quotient spaces, symmetry and partial-order reduction, admissible abstraction with A*/branch-and-bound and Proof-Horizon incumbents, conservative compilation/shared landmarks, and min-plus path algebra for exact rational costs.

The August 14 update adds a substantial **control-AMLD theory** layer. An AMLD is treated as a feedback-controlled settlement system whose actions allocate computation among proof, refutation, independence, representation change, bank use, and meta-level reasoning without giving the controller certificate authority. The new section develops drift and finite-budget variance bounds, robust control-Lyapunov margins, Bellman-value benchmarking on finite theorem mazes, and a concave-resource water-filling theorem for P/R/I scheduling under explicit assumptions. It also states five deliberately open control-AMLD conjectures, including low-dimensional performance signatures, emergent Abel coordinates, Lyapunov representations, P/R/I switching surfaces, and a fast-global/slow-local learning law.

The manuscript now incorporates the public settlement-compass experiment sequence. Experiment 004 is the clean frozen-shell/MAX diagnostic using one sealed 20-target test set and nested training shells `10, 20, 40, 80, 160, MAX`, with MAX containing all 3,612 eligible remaining true proof-DAG roots. Global AUC reaches a plateau around the 80-160 region, while the MAX condition produces the strongest local navigation: precision@10 = 0.670, median first direct-parent rank = 57, and direct-parent ordering beating random on 17/20 targets.

Illustrative saturation fits are included as design diagnostics rather than universal laws. On the aggregate data, the fitted AUC scale is about 14.3 training roots, distance-Spearman about 21.8, and precision@10 about 137.6; the latter is roughly 9.6 times the AUC scale. A simple power-law fit to direct-parent rank is also reported, emphasizing that the sparse `160 -> 3612` interval is not sufficient to identify a unique local learning law. Intermediate shells near `320, 640, 1280, 2560` are therefore recommended.

Experiment 005 begins the transition from static ranking to retrospective executed control trajectories and Abel/Bellman diagnostics. A recorded 160-shell aggregate is deliberately highlighted because it is a useful negative control result: despite positive aggregate learned drift, the tested controller settled 0/100 trajectories, frequently leaving the proof DAG through distractor selections. This demonstrates why a good static compass is not automatically a good closed-loop controller and motivates direct measurement of drift, variance, Abel residual, Bellman regret, failure modes, and hitting time.

The source entry point is `main.tex`; the new material is in `part_05_control_amld_experiments.tex`. The repository workflow compiles the primary LaTeX source and copies the resulting PDF into the cs.AI folder.
