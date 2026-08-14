# From Search Dynamics to Semi-Ideal Computers -- v0.4

This directory contains the fully integrated Version 0.4 source edition of **From Search Dynamics to Semi-Ideal Computers**.

Version 0.4 preserves the complete v0.3 Discovery edition and adds two new sections:

1. **The Abel equation and approximate discovery coordinates**
   - exact Bellman-Abel correspondence for discovery;
   - unit-cost and rational-cost forms;
   - approximate Abel drift and Bellman-Abel residuals;
   - Abel discovery advantage versus binary discovery gain;
   - action-gap stability under approximation error;
   - leak-free fitting of approximate Abel coordinates from earlier rungs only.

2. **Experimental design for iterative discovery control**
   - the rule `learn between experiments; freeze within experiments`;
   - rung / trajectory / transition as distinct statistical units;
   - a mechanically auditable forward-chain protocol;
   - matched five-arm comparisons: ordinary search, motif development, residual-goal repair, representation modulation, and counterpoint search;
   - the first strict nine-rung H2 forward-chain result as a negative control;
   - the next `Discovery Abel v4` design with transition-level Abel logging;
   - escalation to larger solved-rung libraries and sealed cross-family replication.

The first H2 discovery forward-chain run used matched budget `R=8` verifier calls per target per action. All five arms reached the same two of nine rungs. Accordingly, binary matched discovery gain was zero for all nonbaseline arms; this negative result is retained rather than tuned away and motivates the graded Abel-state experiment.

The source remains certificate-first: learned hazard, Abel, motif, and controller quantities can guide search but never replace the independent verifier.

Suggested arXiv classifications remain: primary `cs.LO`, secondary `cs.AI`, cross-list candidate `math.CO`.
