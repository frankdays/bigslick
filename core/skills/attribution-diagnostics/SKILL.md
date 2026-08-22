---
name: attribution-diagnostics
description: Diagnose where the funnel actually stalls and what actually drives pipeline — attribution methodology, reconciliation, and funnel forensics. Use when the user mentions "attribution", "what's working", "which channels drive pipeline", "funnel is leaking", "conversion dropped", "first-touch vs multi-touch", "self-reported attribution", "where should credit go", or when channel investment decisions need evidence. Companion to performance-report (which reports) — this skill diagnoses.
---
# Attribution & Funnel Diagnostics
Read the active client pack + `metrics-baseline.md`. Ground rule stated in every output: attribution is directional evidence for decisions, not courtroom truth — anyone selling certainty is selling.

## 1. The three-lens method (never rely on one)
Prerequisite check: the software lens is only as good as tracking discipline — if UTMs and source fields are inconsistent (see `crm-conventions`), fix that first or weight this lens near zero.
- **Software attribution** (CRM/MAP touchpoints): systematically over-credits trackable digital, invisible to dark social, communities, word of mouth, AI answers.
- **Self-reported attribution:** a required free-text "How did you hear about us?" on every conversion form + logged by SDRs on first call. Cheap, biased toward memorable touches, and the only lens that sees the dark funnel. If not implemented, implement it this week — it's the highest-ROI instrumentation change available.
- **Deal forensics:** for the last 20 closed-won, reconstruct the actual journey from CRM + call notes. Slow, small-n, and the best calibration for the other two lenses.
Report all three side by side. Where they agree → act with confidence. Where they diverge → that divergence IS the finding (e.g., software says paid search, buyers say "a colleague mentioned you" → paid is harvesting demand others created; budget accordingly).

## 2. Funnel stall diagnosis
For a "pipeline is down / conversion dropped" question, decompose before theorizing:
volume vs. conversion vs. velocity — which actually moved, at which stage, for which segment/source, starting when? Compare cohorts (this quarter's leads vs. last) not snapshots. Common signatures: stage-1 stall = targeting/message; mid-funnel stall = sales capacity or lead quality; late stall = pricing/competition/champion issues (→ `win-loss-program`). Pull stage data via CRM MCP; state the confidence and the n.

## 3. Channel investment calls
Rank channels by cost per SQL/opp under each lens; flag channels that only look good under one. New-channel rule: judge on a full sales-cycle lag, not week-2 CPL. Incrementality where stakes are high: geo/audience holdouts or pause-tests beat model debates.

## 4. Deliverable
Attribution readout: three-lens channel table, divergences and their interpretation, funnel decomposition with the stall named, 3 recommended shifts with expected effect and confidence level, instrumentation gaps. Feeds `pipeline-math` (channel assumptions) and `board-reporting` (never present single-lens attribution to a board).

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
