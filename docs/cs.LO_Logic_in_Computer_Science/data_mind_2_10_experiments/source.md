# DATA MIND 2.10 Experiments

Research program for Trading, Quotient Hunter (QH), BANK, learned control, Sentinel protection, proof geometry, and verifier-safe settlement search.

## PURPOSE

This document converts the current DATA MIND 2.10 experimental ideas into runnable protocols. It is grounded in the framework of Proof Density After Trading 001: consequence-preserving Trading should preserve deductive content while potentially changing proof-search geometry, finite-budget accessibility, quotient visibility, BANK usefulness, controller decisions, and resource cost. The earlier preq12b ablation also motivates a stricter causal program: baseline, Trading, QH, Trading+QH, and Trading+QH+BANK all failed to settle the target at 60,000 expansions and reached the same best H=2.065, but QH and BANK materially changed runtime and search behavior. That means search efficiency, horizon, and verified settlement must be measured separately.

## GENERAL EXPERIMENTAL RULES

1. Keep the trust-anchor verifier immutable. Search modules may change representation, priority, pruning, or macros, but final acceptance must be verifier-checkable.
2. Freeze theorem sets, seeds, learner state, BANK snapshot/policy, resource limits, and non-tested settings before a confirmatory block begins.
3. Do not retune after viewing results from a confirmatory block. A retune begins a new development experiment.
4. Save the git commit, full configuration, environment hash, seed, logs, machine-readable summary, certificates, terminal reason, and resource metrics for every run.
5. Prefer verified settlement or time-to-verified-settlement as the primary endpoint. Treat H, density, pruning, BANK hits, and throughput as secondary/mechanistic coordinates.
6. Treat timeouts as censored outcomes rather than completed runtimes. Treat crashes and resource kills as outcomes with explicit causes.
7. Pair the same seeds across arms whenever stochasticity is present.
8. Keep hard-but-valid examples distinct from pathological resource blowups.
9. Report negative interactions. More modules are not automatically better.
10. Preserve a completely untouched held-out benchmark for the final architecture comparison.

## RECOMMENDED ORDER

First complete the missing factorial cells, especially QH+BANK. Then replicate the full factorial across seeds, extend across theorem difficulty strata, and only after that begin adaptive/learned controller experiments. Sentinel and verifier-boundary experiments can proceed in parallel because they address robustness rather than the same causal question.

# PART I — CORE MODULE ABLATIONS AND SEARCH GEOMETRY

## 1. COMPLETE 2×2×2 FACTORIAL: TRADING × QH × BANK

**Question:** What are the independent and interaction effects of Trading (T), Quotient Hunter (Q), and BANK (B) under an identical DATA MIND 2.10 proof-search budget?

**Why this is first:** The existing preq12b ablation contains baseline, T, Q, TQ, and TQB, but not B, TB, or QB. Because Q alone was much faster than baseline, TQ was slower than Q, and TQB was fastest, the missing cells prevent clean causal attribution.

**Hypothesis:** Q has a positive main effect on search efficiency; T may have a context-dependent or negative interaction with Q; B may have a positive main effect or may specifically compensate for the T×Q interaction.

**Design:** Run all eight cells 000, 100, 010, 001, 110, 101, 011, 111. Use the same theorem, paired seed set, expansion limit, wall-clock limit, memory limit, verifier, learner state, BANK contents, and environment. Begin with 10 seeds on preq12b; then repeat the frozen matrix on a preregistered theorem panel.

**Record:** verified settlement, time-to-settlement, wall/CPU time, expansions, peak RAM, best H, time-to-best-H, quotient prunes, BANK retrievals and unique items, Trading count and cost, verifier time, certificate length, controller transitions, crash/timeout reason, git commit, config hash, seed.

**Interpretation:** Estimate T, Q, B main effects plus TQ, TB, QB, and TQB interactions. A module is not “good” merely because one cell is faster.

**COPY-READY START PROMPT:**
Run a preregistered DATA MIND 2.10 2×2×2 factorial ablation of Trading, Quotient Hunter, and BANK on the same frozen preq12b setup used in the previous ablation. Use all eight configurations: baseline (000), Trading only (100), QH only (010), BANK only (001), Trading+QH (110), Trading+BANK (101), QH+BANK (011), and Trading+QH+BANK (111). Use the same verifier, theorem encoding, learner state, BANK snapshot, hardware/environment, expansion budget, wall-time budget, memory budget, and all non-tested settings in every arm. Use 10 preregistered seeds, including seed 2301 if compatible, and pair the same seeds across all eight arms. Do not tune parameters after viewing results. For every run save the complete config, git commit, seed, environment hash, verified-settlement status, wall and CPU time, expansions, peak RAM, best H and time-to-best-H, quotient-prune count, BANK retrieval count and unique items, Trading operations and measured trade overhead, verifier time, certificate length if solved, controller-mode transitions, and terminal reason. Produce machine-readable JSON/CSV summaries plus logs and hashes. Then report main effects T, Q, B and interactions T×Q, T×B, Q×B, T×Q×B. Clearly distinguish verified settlement from secondary efficiency metrics. Preserve the original trust-anchor verifier and reject any result that cannot compile to or be checked by it.

## 2. IMMEDIATE QH + BANK ABLATION

**Question:** Does BANK help Quotient Hunter directly, without Trading?

**Why it matters:** This is the most informative missing factorial cell. Q alone performed strongly on runtime; T+Q was slower than Q; T+Q+B was fastest. QB distinguishes direct QH–BANK synergy from BANK merely compensating for a Trading-induced inefficiency.

**Design:** Compare Q versus QB on the same seeds with Trading disabled. Keep BANK content fixed. Log identity and reuse frequency of BANK items, not only hit count.

**Success criterion:** Prefer verified settlements or shorter time-to-settlement. In unsolved runs require a consistent improvement in preregistered secondary metrics rather than one unusually fast wall-clock result.

**COPY-READY START PROMPT:**
Run a focused DATA MIND 2.10 QH-versus-QH+BANK ablation on the frozen preq12b configuration. Disable Trading completely in both arms. Arm A is Quotient Hunter only; Arm B is Quotient Hunter plus the same verified BANK snapshot used in the prior experiment. Use the same 10 preregistered seeds in both arms and keep every other parameter, learner state, theorem encoding, verifier, expansion limit, wall-time limit, memory limit, and environment identical. Record verified settlement, wall/CPU time, expansions, peak RAM, best H and time-to-best-H, quotient prunes/classes, BANK retrievals, unique BANK items, repeated retrieval counts per item, priority changes caused by BANK hits, descendants generated after each hit, verifier work, and terminal reason. Save full logs, configs, hashes, and a paired per-seed summary. Primary endpoint is verified settlement/time-to-settlement; secondary endpoints are resource-normalized progress and certified pruning. Report whether BANK shows a direct positive, neutral, or negative interaction with QH. Do not enable Trading or retune parameters after seeing results.

## 3. MULTI-SEED REPLICATION OF THE FACTORIAL

**Question:** Are the observed effects reproducible rather than seed-specific timing noise?

**Design:** Repeat every factorial cell on a common frozen seed panel. Ten seeds is an engineering pilot; 20–30 is preferable before strong quantitative claims. Generate and freeze seeds before results are examined.

**Analysis:** Use paired seed comparisons. Report medians and robust intervals because ATP runtimes can be heavy-tailed. For settlements use time-to-settlement with right-censoring at the resource limit.

**COPY-READY START PROMPT:**
Replicate the complete DATA MIND 2.10 Trading×QH×BANK factorial on a frozen panel of 20 preregistered random seeds, using the same seed in all eight cells before moving to the next seed. Freeze the seed list, theorem set, budgets, learner state, BANK snapshot, verifier, and configuration files before starting. Do not change hyperparameters during the block. For each run collect verified-settlement status, time-to-settlement or censoring time, wall/CPU time, expansions, peak RAM, best H, quotient-prune statistics, BANK statistics, trade overhead, verifier overhead, and terminal reason. Produce paired seed-level tables, medians, interquartile ranges, confidence intervals for important paired contrasts, and survival-style summaries when runs time out. Flag outliers but do not silently delete them. If a run crashes, retain it as an outcome with the exact failure reason. Conclude only which effects replicate across seeds; keep mechanism hypotheses separate from empirical results.

## 4. DIFFICULTY-STRATIFIED HELD-OUT THEOREM PANEL

**Question:** Do module effects depend on theorem difficulty?

**Design:** Build easy, medium, hard, and timeout-prone strata using a predeclared baseline measure such as baseline runtime, expansions, or historical settlement rate. Define strata without looking at candidate-system results.

**Analysis:** Test module×difficulty interactions. A feature can be worthwhile if it slightly slows easy theorems but materially raises hard-case settlement.

**COPY-READY START PROMPT:**
Create a frozen held-out DATA MIND 2.10 theorem panel stratified into easy, medium, hard, and timeout-prone groups using only baseline information available before testing candidate modules. Document the stratification rule and theorem IDs before running. On this same panel run the selected factorial configurations under identical per-theorem wall-time, expansion, memory, verifier, learner, and environment constraints. Use paired seeds/configurations where stochasticity exists. Record settlement, time, expansions, peak RAM, best H, QH pruning, BANK use, Trading overhead, and failure mode. Analyze both overall performance and module×difficulty interactions. Do not redefine a theorem’s difficulty from the candidate arm’s result. Keep resource-pathological cases labeled separately so a speedup from simply avoiding them is not confused with improved proof search.

## 5. BUDGET-SLICE DIVERGENCE ACROSS EQUIVALENT PRESENTATIONS

**Question:** For consequence-equivalent presentations P and Q, how different are their finite-budget theorem sets even though their eventual theorem set is the same?

**Design:** Select certified equivalent presentation pairs. Evaluate a frozen theorem family at a ladder of budgets B. Use both expansion and wall-time budgets when possible. Measure cumulative verified settlements and estimate how much budget rescaling one presentation needs to match another.

**COPY-READY START PROMPT:**
Run a DATA MIND 2.10 budget-slice divergence experiment on a frozen benchmark family using at least one pair of certified consequence-equivalent presentations P and Q produced by Trading. Preserve the same trust-anchor verifier. Evaluate both presentations at a preregistered budget ladder spanning small to large expansion limits and, in a separate analysis, matched wall-time limits. At each budget record which theorems are verified, time/expansions to settlement, certificate lengths, and translation/verification overhead. Compute and report |Th_≤B(P)| and |Th_≤B(Q)| at every budget, identify theorem-level crossings, and estimate empirical rescaling constants/functions needed for P’s solved set to be included in Q’s and vice versa. Do not infer unbounded theorem equivalence from finite empirical data; rely only on the certified trade for equivalence and use the experiment strictly to characterize finite-budget accessibility.

## 6. HORIZON VERSUS RUNTIME / THROUGHPUT

**Question:** Does lower runtime or higher throughput actually predict a lower repair-horizon surrogate H?

**Motivation:** In the previous ablation, large runtime differences coexisted with the same best H=2.065. These coordinates may decouple.

**Design:** Log H as a time series, not merely a final value. Compare time-to-H-improvement, expansions/second, pruning activity, and settlement.

**COPY-READY START PROMPT:**
Instrument DATA MIND 2.10 to log the repair-horizon surrogate H as a timestamped and expansion-indexed time series for every run. On a frozen theorem/seed panel, compare baseline and the selected Trading/QH/BANK configurations under identical budgets. Record wall and CPU time, expansions per second, peak RAM, every new best-H event, time and expansion count at that event, QH prunes, BANK hits, trade operations, verifier cost, and final settlement. Analyze whether higher throughput or lower wall time predicts lower H, faster time-to-best-H, or verified settlement. Explicitly enumerate runs where runtime improves but H does not, and runs where H improves while runtime worsens. Do not collapse H and speed into one metric; report them as distinct coordinates.

## 7. HORIZON VERSUS PROOF DENSITY

**Question:** Can Trading lower the nearest-proof horizon while lowering local proof density?

**Importance:** The theory predicts that “more routes” and “higher density” are not synonyms. A direct witness in which H and density move in different directions would demonstrate that they provide different guidance information.

**COPY-READY START PROMPT:**
On a frozen set of certified equivalent DATA MIND 2.10 presentations, estimate a preregistered local proof-density statistic or policy-relative density surrogate at matched radii/budgets while simultaneously measuring the repair-horizon surrogate H. Search for and report presentation pairs where Trading changes the two quantities in different directions, especially lower H with lower density or higher H with higher density. Keep the counting/sampling policy fixed across presentations or explicitly normalize it. Record the exact neighborhood definition, sample size, policy, verifier criterion, H estimator, and uncertainty. Do not treat increased branching as increased proof density. The goal is to test whether horizon and density are empirically distinct guidance signals, not to optimize either one during the experiment.

## 8. QUOTIENT PRUNING EFFECTIVENESS

**Question:** How much real search is saved by each certified QH prune?

**Design:** Give each prune an ID and provenance. Log the quotient/invariant basis, discovery/checking cost, removed state, and estimated or exact descendants avoided. On a small safe subset, use bounded shadow evaluation in which selected prunes are logged but not enforced.

**Primary quantity:** net resource benefit = avoided search cost minus quotient discovery/checking cost.

**COPY-READY START PROMPT:**
Instrument DATA MIND 2.10 Quotient Hunter with per-prune provenance. For each certified prune, log a unique prune ID, the quotient/invariant or dominance rule that justified it, discovery cost, verification cost, the frontier/state removed, an estimate or exact count of descendants avoided where feasible, and subsequent search consequences. On a small preregistered safe theorem subset, add a bounded shadow arm that records what would happen if selected prunes were not enforced, without changing the trust-anchor verification rule. Compare QH-on, QH-shadow, and QH-off under identical budgets. Report total and per-prune CPU/wall time saved, expansions avoided, RAM effects, and any lost useful lemmas. Separate certified hard pruning from heuristic deprioritization. The purpose is to determine whether prune count measures real compression or merely module activity.

## 9. QUOTIENT DISCOVERY-RATE EXPERIMENT

**Question:** Does Trading make useful invariants easier to discover even when total runtime does not improve?

**Design:** Define “useful quotient” before the run, for example a verified quotient that creates at least K certified prunes, improves a preregistered bound/horizon signal, or contributes to a verified settlement. Compare Q with TQ, then QB with TQB.

**Metrics:** time to first useful quotient, useful quotients/10k expansions, pruning mass, quotient verification cost, H, and settlement.

**COPY-READY START PROMPT:**
Run a DATA MIND 2.10 quotient-discovery experiment comparing QH in the original presentation against QH after certified Trading. Before starting, define a useful quotient as a verified quotient/invariant meeting a fixed criterion such as at least K certified prunes, a predefined improvement in a search-bound surrogate, or direct contribution to a verified proof. Use paired theorem/seed runs with identical budgets and non-tested settings. Record time and expansions to first useful quotient, total quotient candidates, verified quotients, useful quotients, pruning mass per quotient, quotient-discovery/verification cost, best H, BANK activity if enabled only in a separate preregistered phase, and final settlement. Report whether Trading changes quotient discovery rate or quotient usefulness even when total runtime is neutral or worse. Do not redefine “useful” after examining the data.

## 10. TRADE-THEN-QH VERSUS QH-THEN-TRADE

**Question:** Does the order of representation search and invariant search matter?

**Design:** Compare T→Q, which chooses a certified presentation then hunts quotients, with Q→T, which identifies quotient candidates/features first and searches for a presentation that exposes them better. Match total preprocessing/module-compute budgets.

**COPY-READY START PROMPT:**
Implement and compare two DATA MIND 2.10 controller policies under the same total resource budget. Policy A is trade-then-quotient: generate/select a small certified consequence-equivalent presentation set first, then run Quotient Hunter inside the selected presentation. Policy B is quotient-then-trade: identify quotient/invariant candidates in the current presentation first, then search only for certified presentation changes predicted to expose or simplify those candidates. Keep verifier, theorem set, seeds, learner, BANK state, total preprocessing allowance, expansion budget, wall-time budget, and memory limit identical. Log module time separately so the policies receive equal opportunity. Measure settlement, time, expansions, H trajectory, quotient discovery rate, pruning mass, trade count/cost, and verifier overhead. Report whether action order changes value per resource; do not add a simultaneous policy until these two are characterized.

# PART II — PRESENTATION CHOICE, BANK MECHANISMS, AND PROOF COMPLEXITY

## 11. ADAPTIVE PRESENTATION SWITCHING

**Question:** Can the controller learn when to remain in the current presentation and when it is worth paying to trade?

**Design:** Compare never-trade, one fixed traded presentation, a simple deterministic switching rule, and an adaptive policy. Every switch must be charged for candidate generation, equivalence certification, state/proof translation, and return verification.

**Features for the adaptive policy:** remaining budget, recent H-improvement rate, frontier growth, quotient availability/usefulness, BANK hit utility, recent module value, and presentation history.

**Primary endpoint:** verified settlement before the budget. The number of switches is not a reward.

**COPY-READY START PROMPT:**
Add a presentation-switching action to DATA MIND 2.10 while keeping the trust-anchor verifier unchanged. Compare four preregistered policies on the same held-out theorem/seed panel: never trade; use one fixed traded presentation selected without test-set tuning; a simple deterministic switch rule; and an adaptive controller that may pay to switch presentations. Charge all trade generation, equivalence certification, state translation, and return/verification costs to the run budget. Allow the adaptive policy to use only features available at decision time: remaining budget, recent best-H slope, frontier growth, quotient availability/usefulness, BANK hit history, and recent module cost/value. Record every switch decision, its predicted reason/value, cost, and downstream result. Primary endpoint is verified settlement before the resource limit; secondary endpoints are time, expansions, H trajectory, number/cost of switches, and wasted switching cost. Do not reward switching itself or tune the adaptive rule on the evaluation set.

## 12. TRADING OVERHEAD DECOMPOSITION

**Question:** Where is Trading actually spending resources, and when do downstream savings exceed that cost?

**Design:** Meter candidate generation, equivalence-certificate construction/checking, state/proof translation, search in the traded presentation, BANK/QH adaptation caused by the trade, recompilation/return cost, and final verification separately.

**Interpretation:** A reduction in expansions is not automatically a wall-clock speedup. Different resource vectors can favor different presentation policies.

**COPY-READY START PROMPT:**
Instrument DATA MIND 2.10 Trading so every trade records separate resource counters for candidate generation, equivalence-certificate construction/checking, proof-state translation, search performed in the traded presentation, BANK/quotient adaptation caused by the trade, return/recompilation to the original presentation, and final verifier work. Run a frozen baseline-versus-Trading panel with identical overall budgets. For each trade compute gross downstream savings and net value after measured trade overhead. Report wall time, CPU time, expansions, peak RAM, H trajectory, settlement, and each overhead component. Preserve the full resource vector rather than reporting only expansions. Do not call a lower-expansion run a speedup if translation/certification makes wall time or total compute worse.

## 13. BANK DIMINISHING-RETURNS / REPEATED-HIT CONTROL

**Question:** Are repeated BANK hits continuing to help, or is repeated boosting creating fixation?

**Design:** Compare unrestricted reuse, fixed reuse cap, diminishing boost, cooldown, and utility-conditioned reuse while keeping BANK contents identical.

**Metrics:** unique items, repeated hits/item, downstream expansions, H change after a hit, proof contribution, resource cost, and repeated work on dead ends.

**COPY-READY START PROMPT:**
Run a DATA MIND 2.10 BANK reuse ablation with the same frozen BANK snapshot and theorem/seed panel. Compare: unrestricted repeated retrieval; a fixed cap of K boosts per item; a deterministic diminishing-boost schedule; a cooldown rule; and a utility-conditioned rule that reduces priority after repeated nonproductive uses. Keep QH/Trading settings fixed. For every BANK retrieval log item ID/provenance, retrieval number for that item, boost assigned, downstream states generated, new best-H events within a preregistered window, proof/certificate contribution if any, and resource cost. Primary endpoint is verified settlement; secondary endpoints are wasted repeated work, unique useful items, H progress, and time/expansions. Do not modify BANK contents between arms. Determine whether repeated hits are productive reuse or controller fixation.

## 14. CROSS-PRESENTATION BANK PROVENANCE

**Question:** Can verified lemmas be safely and usefully shared across consequence-equivalent presentations?

**Design:** Compare siloed BANKs with a shared provenance-aware BANK. A shared entry should carry theorem/macro, source presentation, source proof, and the equivalence/translation evidence needed for reuse.

**Safety condition:** Any reused item must expand or transport to evidence accepted by the unchanged trust-anchor verifier.

**COPY-READY START PROMPT:**
Implement a provenance-aware shared BANK experiment in DATA MIND 2.10. Compare (A) presentation-siloed BANKs and (B) a shared BANK where each entry stores the verified theorem/macro, source presentation, source proof/certificate, and the certified equivalence information needed to transport or compile the item back to the trust-anchor presentation. Use the same theorem/seed panel and budgets. For every cross-presentation retrieval log source and destination presentation, translation/expansion cost, verifier result, downstream use, H change, and contribution to any final certificate. Reject or quarantine any entry whose transport cannot be verified. Report cross-presentation hit rate, net resource value, verification-failure rate, and settlement. The experiment must not weaken the final verifier or treat provenance metadata as proof.

## 15. BANK MACRO COMPRESSION MECHANISM

**Question:** Why does a BANK macro help—shorter proof paths, reduced branching, less verifier work, or merely changed priority?

**Design:** For a frozen macro set compare four modes: unavailable, available only as a search-priority hint, available as an expandable verified macro, and full derivation inlined from the start.

**Metrics:** branching, proof depth, expansions, H, verifier time, compact and expanded certificate size, and settlement.

**COPY-READY START PROMPT:**
Choose a frozen set of verified BANK macros in DATA MIND 2.10 and compare four modes on a paired theorem/seed panel: macro absent; theorem available only as a search-priority hint; theorem available as a verifier-expandable macro; and the macro’s full verified derivation inlined from the start. Keep all other configuration fixed. Record branching factor, proof depth, expansions, wall/CPU time, peak RAM, best H, verifier time, compact certificate length, fully expanded certificate length, and verified settlement. Log exactly where each macro enters the successful or best partial path. Separate priority effects, search-space compression, and certificate/verification compression. Final acceptance must always use a certificate the unchanged trust-anchor verifier can check.

## 16. TRADING-ONLY PRESENTATION GEOMETRY SURVEY

**Question:** How widely can certified equivalent presentations differ in practical proof-search geometry?

**Design:** Generate a bounded portfolio of certified trades with QH and BANK disabled. Measure static descriptors—axiom/rule counts, symbol/term statistics, macro exposure—and dynamic descriptors—frontier growth, expansions/sec, H trajectory, RAM, runtime, proof length.

**Goal:** Identify presentation features that predict a good search geometry before expensive search.

**COPY-READY START PROMPT:**
For a frozen theorem family, have DATA MIND 2.10 generate a bounded portfolio of small certified consequence-equivalent presentations using Trading, with QH and BANK disabled so representation effects are isolated. Predeclare the maximum number and cost of trades per theorem. For each presentation record structural descriptors such as axiom/rule counts, symbol and term statistics, derived-macro exposure, and estimated branching features, plus dynamic search descriptors including frontier growth, expansions/sec, peak RAM, H trajectory, solved status, proof/certificate length, and verifier/translation overhead. Use the same proof-search budget for every presentation after charging trade cost. Produce a presentation-by-feature matrix and identify which pre-search descriptors predict settlement or lower resource use. Do not select the “best” presentation using the same held-out result used to evaluate the predictor.

## 17. CANONICAL PRESENTATION VERSUS PORTFOLIO

**Question:** Is there one generally good presentation for a task family, or is a portfolio of equivalent presentations intrinsically better?

**Design:** Select/learn a canonical presentation using training theorems only. Freeze it. Compare original, canonical, and portfolio scheduler on disjoint held-out theorems with equal total resource budgets.

**COPY-READY START PROMPT:**
Using only a training split, select or learn one canonical certified traded-presentation policy for a DATA MIND 2.10 theorem family. Freeze it. On a disjoint held-out split compare the original presentation, the frozen canonical presentation, and a small portfolio of certified equivalent presentations managed by a preregistered scheduler. Charge all presentation-generation, switching, translation, and verification overhead to the same total budget. Record verified settlements, time, expansions, peak RAM, H trajectories, presentation time allocation, switching cost, and certificate length. Report whether one canonical representation generalizes or whether portfolio search gives a robust advantage. Do not choose the canonical presentation using held-out results.

## 18. EMPIRICAL TRADE-DISTORTION BOUNDS

**Question:** How costly are proof translations between traded presentations?

**Design:** For proofs available in both members of a certified pair, translate in both directions where supported. Measure inference steps, bytes/bits, translation CPU/wall time, and verifier time.

**Goal:** Identify trade classes that appear bounded, approximately linear, polynomial, asymmetric, or explosive. Empirical behavior is not a formal worst-case theorem.

**COPY-READY START PROMPT:**
Collect a preregistered corpus of theorems for which DATA MIND 2.10 can obtain verified proofs in both members of certified traded presentation pairs. For every proof, translate in both directions when supported and record source proof cost L, translated inference steps, serialized bytes/bits, translation CPU/wall time, and verifier time. Group results by trade type. Estimate conservative empirical upper envelopes of the form L_Q ≤ aL_P+b and broader polynomial models where needed; report violations and uncertainty rather than forcing a fit. Distinguish empirical sampled-corpus bounds from formal guarantees. Save original proofs, translated proofs, equivalence certificates, and verifier results so every data point is auditable.

## 19. TRADING AND p-SIMULATION

**Question:** Which consequence-preserving trades also preserve proof complexity efficiently?

**Design:** Use a wide range of source proof sizes, translate both directions, and examine growth. Consequence equivalence alone is not evidence of p-equivalence.

**COPY-READY START PROMPT:**
Run a DATA MIND 2.10 proof-complexity translation study on selected certified trade classes. Build a theorem corpus spanning a wide range of verified source proof lengths. For each trade pair, translate proofs P→Q and Q→P where supported, verify every translated proof, and record inference-step growth, byte/bit growth, translation time, and verifier time. Fit candidate linear and polynomial growth models and inspect worst observed blow-up. Report directional evidence separately: one presentation may efficiently simulate the other without the reverse. Do not claim formal p-simulation or p-equivalence unless the required general translation bound is formally established; label empirical polynomial behavior as experimental evidence only.

## 20. TRADING AND SIC-STATE SIMULATION

**Question:** When does deductive equivalence correspond to a stronger machine-state simulation relation?

**Design:** For selected traded presentation pairs implemented as SICs, state the exact simulation relation first, including state maps, transition preservation, halting/acceptance clauses, and clock requirements. Then test those conditions independently of theorem-set equivalence.

**COPY-READY START PROMPT:**
Select a small set of certified consequence-equivalent DATA MIND 2.10 presentation pairs that have explicit SIC implementations. Before testing, state the exact SIC simulation relation to be evaluated, including the required state map, transition preservation, halting/acceptance clauses, and any timing constraints. Construct candidate maps without using held-out transition results, then test them exhaustively where finite or on a preregistered state/trace set where exhaustive checking is impossible. Record every satisfied and failed simulation condition. Keep theorem-set equivalence as a separate known fact supplied by the trade certificate. Conclude only whether the stronger machine-state simulation relation is witnessed for each pair; do not infer it from consequence equivalence.

# PART III — LEARNING, SENTINEL, SELF-MODELING, AND CONFIRMATORY VALIDATION

## 21. TRADE-AWARE PARTIAL-CREDIT CALIBRATION

**Question:** Which partial-credit coordinates actually predict eventual verified settlement?

**Design:** Snapshot intermediate search states and log original q, trade-aware q, H, density surrogate, quotient features, BANK features, presentation identity, trade cost, remaining budget, and eventual verified outcome. Fit on training theorems and evaluate on disjoint held-out theorems.

**Primary test:** prediction/calibration for verified settlement within the remaining budget. Partial credit remains search guidance only.

**COPY-READY START PROMPT:**
Instrument DATA MIND 2.10 to snapshot intermediate search states at a fixed preregistered cadence and record original structural partial-credit q, a preregistered trade-aware structural score, best/estimated H, proof-density surrogate, quotient features, BANK features, presentation ID, trade cost already paid, remaining budget, and whether the run ultimately obtains a verified settlement. Use a training theorem split to fit/calibrate candidate partial-credit combinations and a disjoint held-out split for evaluation. Compare predictive discrimination and calibration for eventual settlement within the remaining budget. Preserve final verification as binary and unchanged; partial credit is guidance only. Do not tune score weights on the held-out set, and report when a visually attractive score fails to predict settlement.

## 22. TERNARY CONTROLLER CREDIT ASSIGNMENT

**Question:** Can module actions be retrospectively labeled helped / neutral / hurt in a way that trains better future decisions?

**Design:** Define a fixed future window and resource-normalized value change. Use counterfactual replay or shadow evaluation where safe. Keep future-derived labels separate from features available at action time to prevent leakage.

**COPY-READY START PROMPT:**
Add an offline credit-assignment pipeline to DATA MIND 2.10 logs. Before running, define a terminal value function centered on verified settlement before budget exhaustion plus preregistered secondary progress measures for censored runs. For each Trading, QH, BANK, Professor, or other module action, compute a retrospective helped/neutral/hurt label using a fixed future window and resource-normalized change threshold. Where deterministic replay or bounded shadow evaluation is safe, estimate the counterfactual no-action trajectory and use it as additional evidence. Store action-time features separately from future-derived labels to prevent leakage. Train on one theorem split and evaluate label prediction and downstream controller utility on another. Do not let retrospective labels weaken or replace verification.

## 23. LEARNED METACONTROLLER VERSUS FIXED WEIGHTS

**Question:** Does a learned controller allocate module effort better than fixed hand-tuned weights?

**Design:** Compare current fixed policy, preregistered hand-weighted policy, and a learned controller trained only on development data. A tree ensemble is a sensible first model because the factorial results suggest nonlinear interactions; contextual bandit methods can come later.

**Target:** probability of verified settlement before budget exhaustion or expected increase in settlement value per unit resource.

**COPY-READY START PROMPT:**
Train a DATA MIND 2.10 metacontroller only from designated training runs. Use action-time features such as current presentation, remaining budget, recent H slope, frontier growth, resource consumption, quotient activity, BANK history, and prior module outcomes. Compare on an untouched held-out theorem set the current fixed policy, a preregistered hand-weighted policy, and a learned controller. Start with a tuned tree-ensemble model, with all hyperparameter tuning confined to training/validation data. The learned target should predict verified settlement before budget exhaustion or expected settlement-value gain per resource. Freeze the model before held-out evaluation. Use identical global budgets and verifier. Record action choices, predicted values, calibration, settlements, wall/CPU time, expansions, peak RAM, and module costs. Report whether the learned policy improves held-out verified settlement, not merely training metrics.

## 24. EXPLICIT MODULE-INTERACTION MODEL

**Question:** Can the nonadditivity among Trading, QH, and BANK be quantified rather than described informally?

**Design:** Analyze the replicated factorial with T, Q, B main effects and TQ, TB, QB, TQB interaction terms. Use theorem and seed blocking. Handle timeouts as censored.

**COPY-READY START PROMPT:**
Using the completed replicated DATA MIND 2.10 2×2×2 factorial dataset, fit an explicit interaction analysis with T, Q, B main effects and T×Q, T×B, Q×B, T×Q×B terms. Treat theorem and seed as blocking or random factors where appropriate. Analyze verified settlement probability and time-to-settlement as primary outcomes; handle timeouts as censored rather than completed at the cutoff. Analyze wall time, expansions, H, pruning, and BANK statistics as secondary outcomes. Report effect estimates with uncertainty and per-theorem heterogeneity. Test whether the apparent pattern “Q helps, T interferes with Q, B restores value” is supported across replications. Do not retune on this same dataset and then describe the resulting comparison as confirmatory.

## 25. SENTINEL-PROTECTED LEARNER

**Question:** Does resource-anomaly protection improve learner stability without discarding mathematically useful hard examples?

**Design:** Compare identical learners with Sentinel disabled and enabled under a fixed anomaly policy. Quarantine flagged examples with provenance rather than deleting them.

**Metrics:** training completion, total time, peak RAM, quarantine count/reason, learner metrics, and downstream held-out ATP settlement.

**COPY-READY START PROMPT:**
Run a DATA MIND 2.10 learner-protection experiment using a frozen training corpus and held-out evaluation set. Compare the identical learner with Sentinel disabled versus Sentinel enabled under a preregistered anomaly policy. Sentinel should measure per-theorem wall/CPU time, peak RAM, allocation/failure signals, and other resource diagnostics; quarantine rather than delete flagged examples and preserve their IDs and reasons. Keep learner hyperparameters, random seeds, corpus order, and compute limits paired across arms. Record training completion, total training time, peak RAM, number/type of quarantined examples, model-fit metrics, and downstream held-out ATP settlement/time metrics. Report whether protection improves robustness and held-out performance and whether excluded examples contain useful signal. Do not change anomaly thresholds after inspecting outcomes.

## 26. TIME-OUTLIER VERSUS RAM-OUTLIER GATING

**Question:** Which resource signals best distinguish catastrophic examples from ordinary difficult cases?

**Design:** Compare time-only, RAM-only, OR, multi-signal confirmation, robust statistical outlier scoring, and only then a learned anomaly classifier. Include known hard-but-valid and known blow-up cases.

**COPY-READY START PROMPT:**
Using a labeled diagnostic set containing ordinary examples, hard-but-valid examples, previously observed RAM outliers, and known pathological/blow-up cases, compare DATA MIND 2.10 Sentinel gating policies: time-only; RAM-only; time OR RAM; multi-signal confirmation; robust statistical outlier scoring; and, only after these baselines, a trained anomaly classifier. Freeze thresholds on a training/validation subset and evaluate on a held-out diagnostic subset. Record catastrophic-case detection, false-positive quarantine of useful hard examples, resource savings, and downstream learner/ATP performance. Keep quarantined items auditable. Prefer the simplest policy whose held-out safety/utility tradeoff is competitive; do not optimize only for catching every outlier if it discards large amounts of useful mathematics.

## 27. CONTROLLED HARD-CASE REINSERTION

**Question:** Can a Sentinel-quarantined theorem contribute useful learning signal if processed in strict isolation?

**Design:** Reintroduce flagged cases one at a time with hard per-item time/RAM/CPU limits and deterministic termination. The parent training process must remain protected.

**COPY-READY START PROMPT:**
Take a frozen sample of DATA MIND 2.10 Sentinel-quarantined theorems and reintroduce them one at a time in isolated workers with hard per-theorem wall-time, CPU, and RAM limits, deterministic termination, and full resource logging. Do not allow an isolated item to kill, block, or monopolize the parent training job. For each theorem record how far signature/feature/proof preprocessing progresses before cutoff, whether useful partial features can be extracted safely, and whether including those safe features improves a separately held-out learner/ATP evaluation. Compare with simply excluding the item. Preserve the original quarantine label and all failure logs. Distinguish irreducible resource bombs from hard cases that can contribute under controlled treatment.

## 28. SETTLEMENT-PROBABILITY CALIBRATION

**Question:** If the controller predicts V((Q,A),B), do its probabilities correspond to actual settlement frequencies?

**Design:** Freeze the predictor. On held-out theorems log predicted probability at fixed decision points and actual settlement before remaining budget. Evaluate calibration and discrimination by difficulty and presentation.

**COPY-READY START PROMPT:**
Freeze a DATA MIND 2.10 settlement-value model trained without the evaluation theorems. On a held-out theorem/seed set, log at preregistered decision points the model’s predicted probability of verified settlement before the remaining budget expires together with the eventual outcome. Evaluate calibration curves, Brier/log scores, discrimination, and calibration by difficulty, presentation, and module state. If the controller predicts action-conditioned values, evaluate chosen and safely estimable alternative actions separately. Do not recalibrate on the reported held-out set. Report whether nominal 20%, 50%, 80%, and similar predictions correspond closely enough to observed frequencies for resource-allocation decisions.

## 29. COUNTERFACTUAL MODULE-OFF REPLAY

**Question:** Which individual module actions actually mattered inside a run?

**Design:** Save deterministic checkpoints and replay selected states with exactly one action/module suppressed. This is more granular than whole-run ablation but should be interpreted as local causal evidence because search trajectories diverge after intervention.

**COPY-READY START PROMPT:**
For DATA MIND 2.10 runs with saved deterministic checkpoints, select preregistered decision points and replay from each checkpoint under two conditions: original policy and a counterfactual policy with exactly one module/action disabled—Trading, QH, BANK, Professor, or another specified module—while preserving all other state, seed, budgets, and verifier settings. Log immediate and downstream differences in H, frontier, prunes, BANK use, resource consumption, and verified settlement. Bound replay depth/window to keep the comparison interpretable. Store checkpoint hashes and confirm deterministic equivalence up to the intervention point. Report local causal evidence and divergence; do not claim the counterfactual establishes a unique global cause of the original final outcome.

## 30. SELF-AWARENESS LATENCY ACROSS PRESENTATIONS

**Question:** Can Trading reduce the cost of reaching already-provable self-descriptive statements without changing the unbounded self-theory?

**Design:** Use tagged presentations that preserve machine tag, formula naming, and self-description predicates. Measure proof cost for a frozen reflection sequence θ0, θ1, … across certified equivalent presentations.

**Interpretation:** Compare extensional level with finite-budget lev_B and self-awareness horizon H_SA(n). Faster access is not new theoremhood.

**COPY-READY START PROMPT:**
Using tagged DATA MIND 2.10 ATP presentations that are certified consequence-equivalent and preserve the machine tag, formula-naming scheme, and relevant self-description predicates, choose a frozen sequence of self-descriptive/reflection targets θ0, θ1, and higher reachable targets. For each presentation measure verified proof cost to each target in expansions, inference steps, wall/CPU time, and certificate size under identical search policies/budgets where possible. Confirm theorem membership with the unchanged verifier. Report unbounded/reachable level separately from finite-budget access level lev_B and self-awareness horizon H_SA(n). Test whether presentation changes reduce access cost without claiming that faster self-description creates new extensional self-knowledge.

## 31. PRESENTATION-AWARE SELF-MODEL

**Question:** Does giving the controller an explicit model of its own current proof representation improve decisions?

**Design:** Compare equal-capacity controllers with and without explicit presentation/self-state features: current presentation, remaining budget, recent trade value, quotient availability, BANK utility, and recent module performance.

**Interpretation:** This tests operational self-modeling, not consciousness and not automatically a higher formal lev(M).

**COPY-READY START PROMPT:**
Compare two otherwise identical DATA MIND 2.10 metacontrollers on a frozen held-out theorem/seed panel. Controller A receives ordinary search-state features but no explicit presentation/self-state features. Controller B additionally receives current presentation ID/features, remaining resource budget, recent trade costs/outcomes, quotient availability/usefulness, BANK hit utility, and recent module performance. Train both on the same training data with equal model capacity and tuning budget, then freeze before evaluation. Record verified settlement, time, expansions, RAM, H trajectory, action choices, presentation switches, and prediction calibration. Attribute any advantage to operational presentation-aware self-modeling only; do not interpret it as evidence of consciousness or automatically as a change in formal self-awareness level.

## 32. VERIFIER-INVARIANCE STRESS TEST

**Question:** Can aggressive search transformations remain completely separated from acceptance?

**Design:** Enable bounded combinations of Trading, QH, and cross-presentation BANK reuse but require every claimed settlement to compile to a full certificate independently accepted by the original verifier.

**Failure criterion:** Any accepted result without a trust-anchor-verifiable certificate is critical regardless of speed.

**COPY-READY START PROMPT:**
Stress-test DATA MIND 2.10’s verifier boundary. Enable aggressive but bounded combinations of certified Trading, Quotient Hunter, and cross-presentation BANK macros on a preregistered theorem set while keeping the original trust-anchor verifier immutable. For every claimed settlement, require the full equivalence/translation evidence and a final certificate that the trust-anchor verifier independently accepts. Log all intermediate search claims, rejected certificates, translation failures, macro-expansion failures, and verifier results. Include negative/control cases designed to exercise edge conditions. Treat any search-layer claim accepted without a trust-anchor-verifiable certificate as a critical failure. Report efficiency separately from correctness; no speed improvement can compensate for verifier-boundary violations.

## 33. INVALID-TRADE REJECTION / ADVERSARIAL CERTIFICATION

**Question:** Does DATA MIND reliably reject plausible-looking but consequence-invalid presentation transformations?

**Design:** Build valid and deliberately corrupted trades: missing side conditions, variable capture, one-direction-only implications represented as equivalences, changed naming semantics, invalid rule-to-axiom conversions, and broken macro expansion.

**Primary metric:** false acceptance of invalid trades should be zero or as close to zero as the formal certification mechanism guarantees.

**COPY-READY START PROMPT:**
Create a DATA MIND 2.10 trade-certification test suite containing both known-valid consequence-preserving trades and deliberately invalid/corrupted transformations that are superficially plausible. Include missing side conditions, variable-capture or renaming errors, noninvertible or one-direction-only transformations presented as equivalences, altered target/name semantics, invalid rule-to-axiom conversion, and broken BANK macro expansion. Run only the certification/verification boundary needed to accept or reject each case. Record the exact rejection stage and reason. The primary metric is false acceptance of invalid trades; also report false rejection of valid trades and verification cost. Do not let invalid cases enter hard pruning or final theorem search. Preserve all counterexamples as permanent regression tests.

## 34. PREREGISTERED UNTOUCHED HELD-OUT BENCHMARK

**Question:** Does the tuned DATA MIND 2.10 architecture generalize beyond development problems?

**Design:** After development experiments, freeze source commit, architecture, learner weights, hyperparameters, BANK policy, Sentinel policy, controller, verifier, and resource limits. Evaluate once on an untouched theorem set against preregistered baselines.

**Rule:** Any post-hoc architecture/parameter change creates a new development cycle and requires a new untouched confirmatory set.

**COPY-READY START PROMPT:**
Freeze DATA MIND 2.10 exactly as it stands after the development experiments: source commit, architecture version, learner/model weights, hyperparameters, module settings, BANK policy, Sentinel policy, verifier, and all resource limits. Register an untouched held-out theorem benchmark and the baseline systems/configurations before running. Do not inspect candidate-system results on these theorems during tuning. Run every system under equal and explicitly documented wall-time, CPU, memory, and theorem-access conditions. Save all configs, seeds, hashes, logs, certificates, and failure reasons. Primary endpoint is verified settled count/time-to-settlement; secondary endpoints include resource use, H, certificate size, and module diagnostics. Make no parameter changes after the held-out run begins. If a bug requires a change, invalidate the affected confirmatory comparison and start a new held-out evaluation rather than quietly patching it.

## 35. FINAL HEAD-TO-HEAD ARCHITECTURE COMPARISON

**Question:** Which architecture should become the new DATA MIND default?

**Design:** Compare a small set of frozen finalists: baseline, best QH-centric configuration, best BANK configuration, best Trading configuration, best fixed combination, learned metacontroller, and any already-designated external ATP baseline. Give all systems equal resource constraints.

**Decision rule:** Verified settlement comes first, then reliability/resource-adjusted performance, then certificate/search efficiency. A more complicated architecture should earn its complexity.

**COPY-READY START PROMPT:**
Run the final frozen DATA MIND 2.10 architecture head-to-head on an untouched preregistered benchmark. Include the current baseline, the best frozen QH-centric configuration, the best frozen BANK configuration, the best frozen Trading configuration, the best fixed multi-module combination, and the frozen learned metacontroller, plus any external ATP baseline already designated for this benchmark. Give all systems equal documented resource budgets and the same theorem access and verification standard. Record verified settlements, time-to-settlement, censored failures, wall/CPU time, expansions where comparable, peak RAM, certificate size, verifier time, crash rate, and reproducibility across seeds. Rank systems primarily by verified settlement performance and reliability, not internal proxy scores. Report complexity and overhead costs explicitly. Choose a new default only if its held-out advantage is robust enough to justify the added architecture.

# FINAL DECISION FRAMEWORK

Use the first experiments to learn mechanisms; use later experiments to choose architecture. A strong DATA MIND 2.10 claim should eventually require all of the following: verifier-safe settlement, replicated advantage across seeds, benefit on held-out theorems, explicit accounting of module interactions and overhead, resource robustness under Sentinel, and no dependence on tuning the final benchmark.

The most immediate runnable sequence is: Experiment 2 (QH+BANK), then the remaining missing factorial cells, Experiment 3 multi-seed replication, Experiment 4 theorem-stratified replication, and Experiment 24 interaction analysis. That sequence answers the biggest uncertainty created by the current preq12b ablation before spending substantial effort on learned control.