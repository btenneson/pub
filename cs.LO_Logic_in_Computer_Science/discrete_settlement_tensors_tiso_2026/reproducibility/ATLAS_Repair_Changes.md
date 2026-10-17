# ATLAS repair record — DATA 3.0 / AMLD TISO

Date: 2026-10-16

## Preserved
- All 19 major sections, titles, and their order.
- All three original figure files, byte-for-byte.
- D = Dependence. K is a proposed contradiction investigator while C is the existing report label. U unresolved report versus optional investigative role kept separate.
- The original numerical example (same parameters), hypotheses, fixed-verifier interpretation, and experimental controls.
- No AMLD experiment, solver, agent, implementation, or protocol was run or changed.

## Repairs
1. Explicitly modeled global conservation of credit for unique, verifier-accepted event identifiers with attribution shares across all source, recipient, region, and certificate coordinates.
2. Restricted the probability interpretation to an expressly assumed Poisson count of **deduplicated accepted terminal-certificate opportunities**; separated accounting conservation from event independence.
3. Clarified that the TISO scalar is only an aggregate settle/not-settle proxy. No unsupported class-specific probability distribution is asserted.
4. Restricted global optimality to frozen, static, continuously divisible allocation with linear charged costs and identified overhead accounting issues.
5. Added a safe floor-quantization proposition for nonnegative coupled constraint matrices, with a proved additive surrogate loss bound `sum_j W_j k_j q_j`.
6. Tightened KKT sufficiency versus necessity, strict-concavity uniqueness, constraint-bound marginals, online regret assumptions, and finite solved-graph distance.
7. Preserved conditional uniform 2-epsilon regret: it is NOT an empirically verified guarantee for AMLD.

## Second audit
- Report: `ATLAS_Reaudit_DATA3_AMLD_TISO_2026-10-16.pdf`
- Reproducible mathematical check script: `checks.py`
- Check results: `check_results.json`
- Status: mathematical pass for explicitly defined and hypothesized surrogate; operational claims remain unvalidated.

## Compilation
From `DATA3_AMLD_TISO_Repaired_Source/` run `pdflatex DATA3_AMLD_TISO_Repaired.tex` twice. The figures are relative assets. The audit report PDF is separately included.
