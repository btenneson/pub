# DATA MIND 2.12 — set.mm 95/5 Held-Out Results

**Why 14 attempts?** The experiment began with 1 random held-out theorem, then 4 more, then 9 more: **1 + 4 + 9 = 14**.

Training used 95% of the frozen `set.mm` corpus and targets were drawn from the held-out 5%. A success means DATA MIND produced a certificate accepted by a fresh Metamath verifier. `BOUNDED_UNKNOWN` is listed here as a failure to settle within the experiment's search bounds, not as evidence that the theorem is false.

| # | Target | Result | Experimental value |
|---:|---|---|---|
| 0 | `ax13dgen4` | **SUCCESS — SETTLED** | **High.** First clean held-out verified settlement; strong proof-of-concept, pending duplicate-statement audit. |
| 1 | `abrexdom2jm` | **FAILURE — BOUNDED_UNKNOWN** | **Medium.** Very fast exhaustion; useful evidence of a search/portfolio blind spot. |
| 2 | `pm14.18` | **FAILURE — BOUNDED_UNKNOWN** | **High diagnostic value.** Consumed essentially the full 30-minute budget; a genuinely hard negative case for this architecture. |
| 3 | `bj-xpima1snALT` | **FAILURE — BOUNDED_UNKNOWN** | **High diagnostic value.** Long search without settlement; useful hard-case trajectory. |
| 4 | `isfin3-4` | **FAILURE — BOUNDED_UNKNOWN** | **Medium.** Quick bounded failure; useful for premise/ranking analysis. |
| 5 | `prmone0` | **FAILURE — BOUNDED_UNKNOWN** | **High diagnostic value.** Hidden proof is short, yet DATA failed after substantial search; points to a ranking/search-geometry gap. |
| 6 | `1sdom2ALT` | **NOMINAL SUCCESS — SETTLED** | **Low / invalid benchmark value.** DATA used the already-available identical theorem `1sdom2` as a one-step proof. This exposed a statement-level leakage issue. Do not count as a meaningful held-out success. |
| 7 | `afv2eq2` | **FAILURE — BOUNDED_UNKNOWN** | **High diagnostic value.** No candidate proof was found; fresh verifier gate therefore did not run. Hidden proof length was 17 steps, but DATA exhausted essentially the full 30-minute budget (1799.88 s), indicating a serious search/ranking miss on a relatively short theorem. |
| 8 | `sbf2` | **SUCCESS — SETTLED** | **High.** Clean compositional reconstruction; verifier accepted a 9-step proof. |
| 9 | `ex-eprel` | **FAILURE — BOUNDED_UNKNOWN** | **Medium-high diagnostic value.** Substantial search without a certificate; useful negative trajectory. |
| 10 | `pm5.62` | **SUCCESS — SETTLED** | **Very high.** DATA found a verifier-accepted 300-step alternative to a much shorter hidden proof, strong evidence of actual certificate search rather than simple proof reproduction. |
| 11 | `nelbrnelim` | **FAILURE — BOUNDED_UNKNOWN** | **High diagnostic value.** No candidate proof was found; fresh verifier gate therefore did not run. Hidden proof length was 18 steps, but DATA used essentially the full 30-minute budget (1799.81 s), another strong short-proof search/ranking failure case. |
| 12 | `2exnexn` | **SUCCESS — SETTLED** | **High.** Reconstructed a valid 16-step quantifier proof; strong learned proof-pattern transfer. |
| 13 | `pred0` | **SUCCESS — SETTLED** | **Very high.** DATA found a verifier-accepted 15-step route versus the 23-step hidden proof; especially interesting alternative proof discovery. |

## Final interpretation

All **14 of 14 attempts have finished**. There were **6 nominal verifier-accepted settlements**, but `1sdom2ALT` should not be counted as a meaningful held-out success because an identical statement remained available in training. Excluding that duplicate-statement case leaves **13 evaluable non-duplicate targets**, of which **5 were meaningfully settled and 8 were bounded failures**, for a provisional meaningful settlement rate of **5/13 ≈ 38.5%**.

This rate should still be treated as provisional because the benchmark has not yet been fully re-audited for other identical or equivalent statements. The next benchmark revision should split the corpus **modulo identical theorem statements**, not merely theorem labels and proof dependencies, before quoting a formal generalization rate.
