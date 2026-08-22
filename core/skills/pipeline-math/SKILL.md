---
name: pipeline-math
description: Reverse-engineer a revenue target into a pipeline and budget model. Use when the user mentions "pipeline model", "pipeline coverage", "how many MQLs/SQLs do we need", "marketing budget for next year/quarter", "can we hit the number", "revenue planning", "bookings target", "funnel math", or when building/defending a marketing plan or budget. Also use to stress-test whether an existing plan's targets are achievable. Produces the quantitative model behind the marketing plan — the artifact CEOs and CFOs actually interrogate.
---

# Pipeline Math & Revenue Planning

Read the active client pack (`.agents/product-marketing.md`) first — ACV, sales cycle, motion, and team size change every formula. If no pack exists, run `company-onboarding`.

## Step 1 — Collect the inputs (never model on guesses silently)

**Step 0 — Split the target.** Separate new-logo ARR from expansion/renewal ARR (at $30–100M ARR, expansion is typically 30–50% of growth). Model each motion separately: expansion pipeline runs on customer-marketing/CS triggers with different conversion rates and cycle times. Never present a new-logo-only model as "the" pipeline model.
Use the funnel definitions in the client pack (`metrics-baseline.md`) — if MQL/SQL/sourced/influenced aren't defined and agreed with sales ops, stop and define them first; a model on disputed definitions is a fight, not a plan.

Required: new-ARR target for the period (split per Step 0), current ACV, win rate (SQL→closed-won or opp→won — state which), sales cycle length, funnel conversion rates (MQL→SQL, SQL→opp), current open pipeline by stage, marketing budget (if fixed) or CAC/payback constraint.
If the client can't provide a number, use the benchmark table below, mark it `ASSUMED`, and list all assumptions in the model header. An assumptions block is mandatory output.

## Step 2 — The core chain

Work backwards. Show every step of arithmetic in the output:

```
Bookings target ÷ ACV                = closed-won deals needed
÷ win rate                           = opportunities needed
÷ SQL→opp rate                       = SQLs needed
÷ MQL→SQL rate                       = MQLs needed
Opportunities × avg deal size × coverage factor = pipeline $ needed
```

Then time-shift: pipeline must be created one sales-cycle ahead of when it closes. Build a month-by-month creation-vs-close waterfall — a Q4 bookings target is a Q2 pipeline-creation problem.

**Hybrid/PLG motions: model lanes separately.** A blended-ACV chain hides the real requirement — build one chain per lane (enterprise sales-led on MQL→SQL→opp; PLG on signups→PQL→conversion, using the pack's PQL definition) and sum them. Report the enterprise lane's own MQL/SQL need explicitly; that's the number sales capacity must match.

Split the model by source: marketing-sourced vs. sales/outbound-sourced vs. partner-sourced (get the split from the pack or ask). Marketing owns its slice, reports on all three.

## Step 3 — Channel allocation under constraint

Distribute required MQLs/SQLs across channels using: historical conversion + cost per SQL by channel (from CRM/analytics via resource-hub), channel capacity ceilings (a channel rarely scales >50% QoQ without efficiency decay — flag any plan that assumes it), and ramp time for new channels (assume 1–2 quarters to productive).
Constraint check: total spend must satisfy the CAC payback target (default benchmark: <18 months for VC-backed; <12 is strong). If the math doesn't close, say so — present the gap, not a fantasy plan.

## Step 4 — Scenarios & risk

Always produce three cases: Base (inputs as given), Downside (win rate −20%, conversion −15%), Upside (modest +10–15%). Report the downside's revenue miss explicitly. Identify the 2–3 assumptions the model is most sensitive to.

## Benchmarks (B2B SaaS reference — replace with client actuals ASAP)

| Metric | Typical range |
|---|---|
| MQL→SQL | 10–25% |
| SQL→Opp | 40–60% |
| Opp→Won | 15–30% |
| Pipeline coverage | 3–4x target (early GTM: 4–5x) |
| Sales cycle, mid-market | 60–120 days |
| Sales cycle, enterprise | 4–9 months |
| Marketing % of new-ARR spend (venture-backed) | 25–45% |

## Output

Deliver as a markdown model in chat for iteration; offer an xlsx (via the xlsx workflow) once numbers stabilize. Structure: Assumptions → Core chain → Monthly waterfall → Channel allocation table → Scenarios → Sensitivities → "What would have to be true."
This model feeds `board-reporting` directly — keep metric names consistent between the two.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
