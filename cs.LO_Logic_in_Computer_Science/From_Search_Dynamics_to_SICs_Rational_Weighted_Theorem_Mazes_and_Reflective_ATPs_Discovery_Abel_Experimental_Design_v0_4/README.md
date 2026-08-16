# From Search Dynamics to Semi-Ideal Computers

**Theorem Mazes, Discovery Coordinates, and Feedback Control for Automated Reasoning**

Version 0.4 · August 2026 · Brian Tenneson

[Read the PDF](./From_Search_Dynamics_to_Semi-Ideal_Computers_Discovery_Abel_Experimental_Design_v0_4.pdf)

## What this paper is about

This manuscript studies automated theorem proving as controlled navigation through an implicit theorem maze. Proof states are vertices, legal inference steps are directed edges, and verifier-accepted certificates are absorbing exits. The paper develops exact graph reductions where possible, measurable guidance when exact reduction is unavailable, and verifier-backed experimental protocols for testing whether learned guidance actually improves search.

The central principle is **certificate first**: learned models, heuristics, Abel coordinates, hazard estimates, motif scores, and controllers may guide search, but they never replace an independent proof verifier.

## Main contributions

1. **Theorem-maze formulation.** The paper separates the complexity of shortest-path search on an explicit graph from the much harder problem of exposing only a useful fraction of an implicit proof-state graph.
2. **Exact reduction before heuristic guidance.** Quotienting, partial-order reduction, admissible abstractions, verified landmarks, proof-horizon bounds, and related exact or conservative reductions are prioritized whenever their hypotheses apply.
3. **Feedback-control view of automated reasoning.** ATP, ALD, and AMLD search policies are described using measurable quantities such as drift, variance, Bellman values, and resource allocation, while settlement remains verifier-backed.
4. **Discovery as a controlled event.** Certified novelty is separated from graded readiness, discovery hazard, mechanism probability, depth, and intervention gain.
5. **Bellman–Abel discovery coordinates.** Before discovery, an optimal time-to-discovery Bellman value induces an Abel-type translation law. Approximate Abel coordinates, residuals, drift, and action-gap stability give graded signals when a binary success/failure endpoint is too coarse.
6. **Auditable iterative experimentation.** The protocol follows the rule **learn between experiments; freeze within experiments**. Training data, action grammars, budgets, features, and predictions are frozen before each held-out rung is exposed.

## What is established, and what is not

The paper contains mathematical formulations, exact correspondences under stated hypotheses, control constructions, and verifier-backed experimental designs. It does **not** claim that rational weighting makes theorem proving polynomial, that learned guidance is itself a certificate, or that the current experiments demonstrate an end-to-end ATP speedup.

The first strict nine-rung H2 forward-chain experiment is deliberately retained as a **negative control**. Under the matched budget `R = 8` verifier calls per target per action, all five intervention families reached the same two of nine rungs. Thus binary matched discovery gain was zero for every nonbaseline arm. Rather than tuning this result away, v0.4 uses it to motivate a more informative transition-level experiment based on graded Abel-state measurements.

That negative result should therefore be read as evidence about the **measurement and control problem**, not as a positive performance claim.

## Reading map

For a first reading, the recommended order is:

- **Big picture and maze primer** — what theorem mazes are and why implicit search differs from ordinary graph search.
- **Rational mazes and quotient reductions** — exact/conservative ways to shrink the search problem.
- **Control and AMLD experiments** — feedback variables, compass behavior, and successor-selection limitations.
- **Discovery** — novelty, readiness, hazard, and forward-chain evaluation.
- **Abel discovery coordinates** — the Bellman–Abel correspondence and approximate graded coordinates.
- **Experimental design** — frozen forward-chain methodology and the next transition-level experiment.

The remaining sections supply foundations, reflection machinery, DATA as a distinguished implementation case, and conclusions.

## Files

- `From_Search_Dynamics_to_Semi-Ideal_Computers_Discovery_Abel_Experimental_Design_v0_4.pdf` — compiled paper.
- `main.tex` — LaTeX entry point.
- `part_*.tex` — modular source sections.
- `references.tex` — bibliography and source notes.

A future source-layout cleanup can move the component files under `src/`; they are left at the current paths in v0.4 so the existing compiled artifact and source history remain reproducible without a disruptive binary-file rename.

## Classification

Suggested arXiv classifications: primary `cs.LO`, secondary `cs.AI`, with `math.CO` as a possible cross-list where appropriate.
