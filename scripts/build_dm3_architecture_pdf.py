#!/usr/bin/env python3
"""Build the DATA MIND 3.0 provisional module-and-interface freeze PDF."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cs.LO_Logic_in_Computer_Science" / "DATA_MIND_3_0_Module_and_Interface_Freeze.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontSize=19, leading=22, spaceAfter=8))
styles.add(ParagraphStyle(name="SubTitle", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9.5, leading=12, textColor=colors.HexColor("#555555"), spaceAfter=13))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontSize=13, leading=16, spaceBefore=8, spaceAfter=6))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontSize=10.5, leading=13, spaceBefore=6, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=8.7, leading=11.2, spaceAfter=5))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7.3, leading=9.2, spaceAfter=2))
styles.add(ParagraphStyle(name="Quote", parent=styles["BodyText"], fontSize=10, leading=13, leftIndent=14, rightIndent=14, spaceBefore=4, spaceAfter=8, borderColor=colors.HexColor("#6f8fa6"), borderWidth=1, borderPadding=7, backColor=colors.HexColor("#eef5f9")))
styles.add(ParagraphStyle(name="Monoish", parent=styles["BodyText"], fontName="Courier", fontSize=7.7, leading=10, leftIndent=10, spaceAfter=6))


def P(text, style="BodyX"):
    return Paragraph(text, styles[style])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(0.55 * inch, 0.32 * inch, "DATA MIND 3.0 - Provisional Module and Interface Freeze")
    canvas.drawRightString(7.95 * inch, 0.32 * inch, f"Page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUT), pagesize=letter, rightMargin=0.48*inch, leftMargin=0.48*inch,
    topMargin=0.48*inch, bottomMargin=0.52*inch,
    title="DATA MIND 3.0 Module and Interface Freeze",
    author="Brian Tenneson and ChatGPT",
)

story = [
    P("DATA MIND 3.0", "TitleCenter"),
    P("Provisional Module-and-Interface Freeze", "SubTitle"),
    P("<b>Governing rule.</b> No module gains mathematical authority merely because it is intelligent, predictive, reflective, highly cleared, or favored by the controller."),
    P("The Verifier remains the sole mathematical trust anchor. BANK contains verifier-accepted material; FUTUREBANK contains represented possibilities; all other intelligence changes search, allocation, visibility, or presentation rather than theoremhood."),
    P("Core architectural distinction", "H1x"),
    P("<b>Verifier:</b> decides whether a mathematical certificate is accepted. <b>BANK:</b> preserves verified reusable mathematics. <b>FUTUREBANK:</b> quarantines speculative futures. <b>Professor:</b> allocates resources. <b>Partial Credit:</b> measures unfinished progress. <b>Sentinel:</b> enforces runtime safety. <b>Awareness/Clearance:</b> controls what a module may formally know or inspect."),
]

rows = [
    ["Entity", "Main job", "Reads", "Produces / writes", "BANK / trust boundary"],
    ["Verifier (VE)", "Mathematical trust anchor", "Candidate certificates; admissible dependencies", "ACCEPT / REJECT; verifier record", "Sole admission gate to trusted mathematics"],
    ["P1/P2", "Proof settlement", "Active state; Librarian shelf; Compass; partner advice", "Proof steps; candidate lemmas/certificates", "Read; deposits only through VE"],
    ["R1/R2", "Refutation settlement", "Same typed views", "Refutation candidates/certificates", "Read; deposits through VE"],
    ["I1/I2", "Independence settlement", "Same typed views", "Independence candidates/certificates", "Read; deposits through VE"],
    ["C1/C2", "Integrity / contradiction settlement", "Same typed views", "Integrity/contradiction candidates", "Read; deposits through VE"],
    ["BANK", "Verified past", "Verifier-accepted objects", "Append-only verified records", "Protected, typed, provenance-aware memory"],
    ["FUTUREBANK", "Possible futures", "Speculative branches", "Hypotheses; histories; dependency graphs", "Never trusted merely by membership"],
    ["Librarian", "Retrieve relevant verified knowledge", "Clearance-permitted BANK", "Active working shelf", "Heavy read; never changes theoremhood"],
    ["Shortcut Engine", "Cheap verified macro transitions", "BANK / Librarian shelf", "Macro proposals; expandable certificates", "Macro admission remains verifier-gated"],
    ["Presentation Manager / Trading", "Certified equivalent presentations", "Presentation; verified trades; cost model", "Candidate P'; translation/equivalence certificates", "Presentation authority, not truth authority"],
    ["Quotient Hunter", "Quotients, invariants, obstructions", "Presentation; BANK; search state", "Quotient/invariant proposals", "Hard pruning only after certification"],
    ["Proof Compass K1", "Rank mathematical moves", "Proof state; features; permitted BANK evidence", "Transition scores", "Advice only"],
    ["Policy Compass K2", "Rank controller actions", "Global control state", "Policy-action scores", "Advice only"],
    ["Partial Credit", "Measure unfinished progress", "State; horizons; verified structure; trajectories", "PC vector; uncertainty; trajectory", "Measurement, never certification"],
    ["Professor", "Allocate resources", "PC; Compass; tensor; Scout; Sentinel risk; BANK stats", "Allocation plan", "Scheduling authority only"],
    ["Scout", "Cheap bounded probes", "Proposed action; sandbox budget", "Empirical probe report", "Strictly budget-limited"],
    ["Quicksand Monitor", "Detect stagnant attractive basins", "PC/horizon/certificate-density/cost", "Stagnation or bailout signal", "Diagnostic only"],
    ["Skeptic / Counselor", "Challenge misleading estimates", "PC calibration; Professor predictions; Compass; history", "Challenge/calibration report", "Independent critic, no proof authority"],
    ["Creativity Engine", "Generate structurally different ideas", "Search summaries; failures", "Novel candidate strategies", "Speculative output"],
    ["Revision Engine", "Change search controls", "Quicksand; Skeptic; Professor state", "Revised policy/control coordinates", "Strategy authority only"],
    ["Sentinel", "Operational containment/security", "RAM/time/growth/access/worker behavior", "Allow; throttle; quarantine; kill; checkpoint", "Safety veto; never changes theoremhood"],
    ["Awareness / Self-Model", "Clearance and formal system model", "Authorized telemetry/state descriptions", "Clearance-compatible views", "Controls knowledge/visibility, not truth"],
    ["Historian / Transaction Ledger", "Immutable episode history + analysis", "Decisions; resources; PC; trades; BANK hits; Sentinel events", "Event ledger; episode traces", "Audit record, not mathematical memory"],
    ["Distiller", "Extract reusable structure after episodes", "Proof; history; trades; QH; BANK hits", "Lemma/shortcut/invariant/training proposals", "Mathematical proposals still pass VE"],
    ["Learner", "Train horizon/gain/PC/retrieval/policy models", "Target-clean historical data", "Frozen model versions", "Heuristic learning never rewrites BANK truth"],
    ["Baseline Lane", "Protected untouched search", "Original presentation", "Ordinary candidate certificates", "Protected resource share"],
    ["Benchmark / Evaluation", "Ablations and falsifiability", "Logs; certificates; costs", "Metrics/reports", "No trusted-state mutation"],
    ["Reflective Orchestrator", "Run iterative cycle", "Module outputs", "Calls; events; coordination", "No special trust merely by orchestration"],
]
wrapped = [[P(f"<b>{x}</b>" if r == 0 else x, "Small") for x in row] for r, row in enumerate(rows)]
t = Table(wrapped, colWidths=[0.92*inch, 1.18*inch, 1.75*inch, 1.72*inch, 1.55*inch], repeatRows=1, hAlign="CENTER")
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#dfeaf1")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#1c3443")),
    ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#aebcc6")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("LEFTPADDING", (0,0), (-1,-1), 3), ("RIGHTPADDING", (0,0), (-1,-1), 3),
    ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f9fa")]),
]))
story += [P("DATA MIND 3.0 interface matrix", "H1x"), t, Spacer(1, 7)]

story += [
    P("The wiring backbone", "H1x"),
    P("Three principal information paths are frozen before policy implementation."),
    P("<b>1. Mathematical path</b>", "H2x"),
    P("Search / QH / Trading / Distiller -> candidate -> Verifier -> BANK", "Monoish"),
    P("There is no other path into BANK. A learned, speculative, high-partial-credit, or high-clearance claim remains outside trusted mathematical memory until verified."),
    P("<b>2. Fast adaptive loop</b>", "H2x"),
    P("Search -> Partial Credit -> Professor -> {Scout, allocation, Revision} -> Search", "Monoish"),
    P("Professor does not accept Partial Credit blindly. Skeptic challenges calibration, Quicksand supplies stagnation evidence, Sentinel supplies operational risk, Compass supplies directional estimates, and Scout can cheaply probe an action before a major allocation."),
    P("<b>3. Slow learning loop</b>", "H2x"),
    P("Episode -> Historian -> Distiller / Learner -> {Verifier -> BANK | frozen learned models} -> future episodes", "Monoish"),
    P("This separates two forms of learning: reusable mathematics must be verified before entering BANK, while heuristic lessons are stored as learned policy/retrieval models and remain non-authoritative."),
    P("Trading has a specific wire", "H1x"),
    P("Trading does not sit in the middle of every inference. The Presentation Manager proposes a bridge from one deductive presentation to another; certification establishes admissibility; then ordinary search, QH, BANK macros, Compass, Professor, Scout, and other search machinery may operate within the selected presentation."),
    P("P0 <-> P1 <-> P2 ... (certified proof translations / equivalence bridges)", "Monoish"),
    P("The protected original presentation remains available as a trust-anchor/baseline route. Trading changes search geometry; it does not itself assert speed or mathematical truth."),
    P("BANK = vertical reuse; Trading = horizontal movement.", "Quote"),
    P("BANK lets DATA MIND reuse verified knowledge through time and across agents. Trading lets DATA MIND move sideways among certified presentations of the same mathematics."),
    P("Clearance and separation are wired from day one", "H1x"),
    P("DATA MIND 3.0 should not begin as one giant object with unrestricted shared state. Each module receives an explicit interface and a permitted view. A generic BANK view can be written schematically as:"),
    P("BANKView(M) = { b in BANK : classification(b) <= clearance(M) }", "Monoish"),
    P("Clearance determines what a module may know or touch; capability determines which operations it may execute; Sentinel determines whether the authorized behavior may safely continue. High clearance therefore does not imply authority to certify or mutate BANK."),
    P("Examples: Professor receives reports rather than Sentinel internals; P receives a Librarian shelf rather than unrestricted BANK internals; Scout receives a bounded sandbox; Creativity/Dreamer-style speculation writes to FUTUREBANK; Distiller may propose a reusable lemma or shortcut but cannot admit it to BANK."),
]

story += [
    PageBreak(),
    P("New 3.0 additions", "H1x"),
    P("<b>Librarian.</b> BANK remembers everything verified; Librarian retrieves the small target-, role-, presentation-, and state-specific working shelf that is worth considering now."),
    P("<b>Scout.</b> Before Professor commits a large budget to a transformation or basin, Scout can run a cheap bounded probe and report partial-credit change, horizon movement, branching, BANK hits, RAM slope, novelty, and related evidence."),
    P("<b>Historian.</b> The old append-only Transaction Log becomes the factual substrate of an analytical Historian that records what was tried, why, at what resource cost, with what intermediate signals, and with what final result."),
    P("<b>Skeptic / Counselor.</b> An independent critic tests whether Partial Credit, Compass values, Professor predictions, and presentation-gain estimates remain calibrated instead of becoming self-reinforcing proxies."),
    P("<b>Distiller.</b> After a verified success or informative failure, Distiller asks what reusable structure should survive: a lemma, macro shortcut, invariant, useful trade, proof motif, or training example."),
    P("Security and operational protection", "H1x"),
    P("Separation is a security property, not merely a software-engineering preference. No module receives another module's internal mutable state merely because both belong to DATA MIND. Communication crosses explicit authorized interfaces."),
    P("Sentinel is independent of proof authority. A worker can be fully authorized to process a theorem and still be throttled or quarantined for abnormal RAM, time, process growth, queue growth, verifier-failure streaks, or other unsafe behavior. Sentinel can stop the worker without declaring its mathematics false."),
    P("Protected components should include the Verifier, BANK, transaction history, baseline lane, and recovery reserve. Failure of one worker should not imply failure of DATA MIND as a whole."),
    P("Child compatibility note", "H1x"),
    P("Earlier DATA-MIND topology names a Child endpoint, but the reviewed material does not yet define a sufficiently precise, nonredundant DATA MIND 3.0 responsibility for it. The architecture should preserve compatibility with the endpoint without inventing a role merely to preserve the name."),
    P("Provisional freeze summary", "H1x"),
    P("<b>Trust:</b> the Verifier remains sovereign."),
    P("<b>Verified memory:</b> BANK is append-only, typed, provenance-aware, and entered only through verification."),
    P("<b>Speculation:</b> FUTUREBANK is explicitly non-authoritative."),
    P("<b>Adaptive control:</b> Search -> Partial Credit -> Professor -> Scout/allocation/Revision -> Search."),
    P("<b>Vertical reuse:</b> Librarian retrieves; Shortcut Engine exposes verified reusable routes; BANK retains the underlying certificate."),
    P("<b>Horizontal search:</b> Trading and QH alter certified search geometry while the original presentation remains protected."),
    P("<b>Protection:</b> clearance, capability separation, Sentinel containment, and compartmentalized interfaces are architectural rather than after-the-fact additions."),
    P("<b>Long-term learning:</b> Historian and Distiller turn episodes into auditable experience, learned policies, and verifier-gated reusable mathematics."),
    P("This is the provisional DATA MIND 3.0 module-and-interface freeze to use as the wiring contract. New modules should be added only when implementation reveals a genuinely missing function."),
]

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
