# ATLAS repair and mathematical re-audit

**Manuscript:** *The Attested Horizon Calculus: Proof, Testimony, Persistent Knowledge, and Noncomputable Finality in a Single ATP*  
**Author credit:** `<Brian Tenneson>`  
**Version audited:** 0.2 (ATLAS-repaired), October 30, 2026  
**Original baseline:** version 0.1 and the eight-finding ATLAS-style audit  
**Audit performed:** October 30, 2026, by ChatGPT in ATLAS-style review mode.

## Verdict

**PASS WITH EXPLICIT MODEL ASSUMPTIONS — paper-level mathematical re-audit.** All eight recorded version-0.1 audit findings have specific repairs in version 0.2. The central impossibility theorem is unchanged in mathematical strength and survives a fresh adversarial check. No unclosed logical contradiction was found in the repaired theorem chain. The verdict is conditional on the source's promised effective, complete, finite-branching proof-history routines; sound declared verifiers; conservative and cost-persistent BANK evolution; and, for the testimony results only, an ideal truthful oracle and reliable authenticated relay.

**Verification boundary:** This is an editorial and mathematical review by the same AI assistant, not an independent external referee, separate model, proof-assistant check, or executed AMLD+0 settlement. No implementation of the stated successor routine or truth oracle has been verified. The theorem proofs remain human-readable paper arguments; thus “PASS” is **not** a machine-certified proof verdict.

## Repair closure ledger

| Finding | Severity in 0.1 | Repair in 0.2 | Re-audit |
|:--|:--|:--|:--|
| A1. Stagewise finite successor search | Major | Uniform `Next(e,k,rho)` is promised total, complete, and finite at *every actual stage*, with finite stage BANKs, decidable legality and acceptance, and an injective canonical code. | Closed **under explicit promises**. |
| A2. Two incompatible cost conventions | Major | Distinguishes accumulating full chronology `C_chron` from unit-service restarted proof cost `C_proof(rho)=len(rho)`. Terminal checking is in the final service, with no hidden acceptance or BANK-scan fee. | Closed **for the declared metric**. |
| A3. Policy-excess nonnegativity | Moderate | Requires realized accepted history `rho_t` to belong to `Q_t intersect Hist`; sets `C_t=len(rho_t)`. | Closed; both excesses are now nonnegative. |
| A4. Missing global operational semantics | Moderate | Adds six legal event rules, an append-only event clock `t`, and a BANK-checkpoint clock `k`. A checkpoint advances `k` even with no new deposit. | Closed as an abstract transition calculus. |
| A5. Actual events not shown evidence-only | Moderate | Gives an inductive verifier-gate invariant and proves OracleEmit, RelayStore, RelayForward, and Deactivate leave BANK and the restarted proof graph fixed. | Closed for those four concrete rules. |
| A6. Too-global 'unprovable' language | Minor | Restricts negative conclusions to **the fixed sound effective finality checker**, or to the impossibility of one uniformly complete such scheme. | Closed. |
| A7. Uniform coding/indexing implicit | Minor | Adds computable Turing-code-to-AHC compilation `e -> i(e)` and canonical history code. | Closed. |
| A8. Figure/verification-status phrasing | Editorial | Replaces cramped Figure 1 dashed import line with explicit blocked-import node, dates the audit clarification, and retains all author/disclaimer qualifications. | Closed on rendered visual inspection. |

**Additional repair during re-audit:** `ProofService` now also permits a *separately charged* metalevel certificate check via the declared `V_fin`, if present. This allows a legitimate certified-finality receipt in the typed ledger without modifying the object-level proof graph or silently classifying oracle testimony as an ordinary proof. The BANK checkpoint rule also explicitly permits no-op maintenance ticks, essential to the nonhalting branch of the one-drop example.

## Independent logical checks of the theorem chain

**Local horizon exactness and finite breakthrough ladder (Section 3).** Given the explicit complete finite `Next` list at every stage, each depth has finitely many legal histories that can be exhaustively enumerated; verifier-gated acceptance is decidable. Since a stage-0 successful path is promised and old paths persist without increasing restarted proof cost, every stage has a successful path. Breadth-first exploration therefore terminates at the exact least cost, and finite enumeration gives the least-coded minimizing history. Every strict drop uses at least one unit of the initial nonnegative integer horizon; thus there are finitely many. Stage-by-stage checks are computable and relative to the specification of `Next`, **not** an independent certification of that routine's correctness. **Pass, conditional.**

**The two-ledger invariant (Sections 2 and 4).** ProofService records an accepted object proof only through `V`, with metalevel finality checked only by `V_fin`. Checkpoint/Deposit is the only event allowed to extend BANK authority, and then only after finite provenance verification. The four testimony/deactivation events alter receipts, buffers, source availability and chronology charges but leave the stage-indexed proof graph unchanged. Induction on events establishes BANK provenance and the narrower invariant of unchanged accepted proof paths and horizon for evidence-only steps. The stronger claim that *all global costs* remain fixed is **not made**. **Pass for the frozen full proof-history presentation.**

**Oracle upper bound (Theorem in Section 5).** For fixed admissible `(e,N)`, the search for a later horizon inequality computes successive `h_e(j)` and halts iff a later difference exists. It is a partial computable search, so one ordinary halting-oracle query decides its termination. A sequential `N=0,1,...` search using that oracle terminates because a finite nonincreasing natural sequence stabilizes. No decidable *admissibility test* is required; this is a promise-class reduction. **Pass.**

**Ordinary lower bound (Theorem in Section 5).** The effectively compiled one-drop family has `h_e(k)=2` until the coded machine halts by stage `k` and `h_e(k)=1` thereafter. Its sole possible new lemma has an ordinary verified proof from the fixed premise. If a computable stabilization selector yielded `N`, bounded simulation through `N` would decide whether the machine ever halts: a first halt at any time after `N` would contradict stabilization at `N`. The dummy step excludes a zero-time indexing ambiguity. The maintenance checkpoint may occur without deposit, so the formal clock realizes the whole family. **Pass.**

**Blind-relay preservation (Section 6).** OracleEmit, RelayStore, Deactivate, then RelayForward is a permitted finite sequence under the stipulated channel assumptions. The typed, authorized claim remains accessible after source shutdown. The semantic truth of the asserted finality derives solely from the separately assumed ideal oracle; neither authentication nor a relay record constitutes a proof. Chronology charges remain accounted for. **Pass under ideal source/channel premises.**

**No sound effective universally complete finality verifier (Section 7).** Suppose a fixed sound total computable verifier accepted at least one finite `(N,pi)` for each one-drop evolution. Enumerate all pairs and test each. Totality makes every check finish, completeness makes the search halt, and soundness makes the first accepted `N` a correct stabilization stage. This constructs the forbidden ordinary selector. The argument deliberately asks for *some* correct stage, not a least stage. Accordingly, for every single fixed sound effective finality checker, at least one input has no accepted finality certificate at any stage. **Pass; the strongest result.**

**Attested-but-uncertified corollary (Section 7).** Choose the input omitted by that checker. The ideal oracle can truthfully produce a stabilization stage and the relay can preserve its receipt, while `V_fin` accepts no corresponding finality proof at any stage for this input. These claims are compatible because the two types of warrants are not equated. **Pass with checker-relative reading.**

**Advice and excess decomposition (Section 9).** The corrected realized path is explicitly in the policy-accessible set, and therefore `C_t >= h^Q >= h`. The algebraic identity follows by adding and subtracting `h^Q`. Different accessible policy subsets can change the restricted minimum, but never reclassify a nonproof as a verified BANK theorem. **Pass.**

## Adversarial counterexample checks

1. **A BANK grows without a drop:** no contradiction. Old verified routes persist, and optional new premises need not help the target. A maintenance checkpoint can have no new deposit while advancing `k`.
2. **A BANK grows but the horizon rises:** the repaired theory does **not** claim otherwise unless the non-cost-increasing route-persistence promise holds. Obligatory scan/reindex fees violate that promise or change the cost model.
3. **The finality verifier finds a nonminimal stabilization stage:** allowed; the reduction only requires any correct stage.
4. **The finality verifier is partial:** excluded from the negative theorem's premise; total computable checking is essential to the exhaustive-certificate search proof.
5. **An oracle-signed receipt is offered as the proof certificate:** verification of message origin is not by itself a sound finite proof of the assertion. Treating it as a truth-producing axiom imports the explicitly noncomputable oracle-soundness assumption and is a different proof system, not an ordinary self-contained effective finality checker.
6. **One oracle answer remains after deactivation:** that single finite receipt is not an all-input oracle. Future new queries remain unavailable.
7. **A metalevel certificate really is provided:** the new ProofService variant records it through `V_fin`; it does not enter the BANK or change `h_e(k)` merely by being logged.

## Build and layout checks

- Repaired source compiled successfully with two `pdflatex` passes after the last semantic edit, with resolved cross-references and **no LaTeX errors or overfull boxes**; two benign underfull paragraph warnings remain in dense tables.
- Final manuscript: **16 pages**, US Letter. Contact-sheet inspection covers all pages and the black-and-white figures; no cropped figure, displaced title, missing author credit, or obvious overlap was found.
- The full manuscript preserves the requested exact author credit `<Brian Tenneson>`, the AI disclaimer, source bibliography, and a dated statement distinguishing paper review from machine proof.
- The unrevised 0.1 original is retained separately; the current file is numbered 0.2.

## Residual boundaries (not failures of the paper-level arguments)

These are mathematical hypotheses or implementation obligations, not independently established facts: the actual soundness and completeness of any proposed `Next` implementation; replay soundness of every future BANK deposit; soundness of the formal proof and finality checkers; the ideal halting oracle's truthfulness; and the fidelity of authentication/relay technology. Neither `0'` access nor complete finite history enumeration is claimed to be an efficient physical method. Theorems apply to the stipulated **restarted proof-service metric**, not automatically to wall-clock latency, energy, or total lifetime expenditure. The ATP is one proof controller with external evidence interfaces, not an installed multiagent AMLD+0 system.

**Final disposition:** Version 0.2 is suitable to circulate as an **ATLAS-style repaired and re-audited research draft**, with its conditional premises and review limitations retained. A claim of independent formal verification, verified implementation, or completed operational AMLD+0 settlement would be unsupported. Publication has **not** been performed.