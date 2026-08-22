---
name: abm-builder
description: Design and run account-based marketing programs — tiered account selection, play design, and orchestration across channels. Use when the user mentions "ABM", "target accounts", "account-based", "named accounts", "1:1 or 1:few campaigns", "account list", "land big logos", or wants marketing pointed at specific companies rather than segments. Unifies the upstream prospecting, apollo-outreach, cold-email, linkedin, and events skills into account plays.
---
# ABM Campaign Builder
Read the active client pack — ABM only pays at sufficient ACV (rule of thumb: >$30k for 1:few, >$75k for true 1:1) and requires sales co-ownership. If sales hasn't agreed to work the list, stop: build the alignment first (`sales-marketing-alignment`).

## 1. Account selection (with sales, never for sales)
Score candidates on: ICP fit (firmographic + technographic via enrichment/`similarweb-traffic`/`apollo-outreach` through resource-hub), intent signals (hiring patterns, tech changes, funding, engagement history in CRM), and sales conviction (an account no AE believes in is dead weight). Tier the list:
- **T1 (1:1):** 10–25 accounts. Custom everything.
- **T2 (1:few):** 50–150 accounts in 3–5 clusters by vertical/pain.
- **T3 (programmatic):** ICP-matched broader list; personalized at segment level.
Budget guardrail: T1 plays realistically cost meaningful program dollars per account per year (content, events, ads, exec time) — size the tier to the budget, not the ambition. And you do not need an ABM platform to start: CRM discipline + a shared account list + this playbook covers the first two quarters; buy tooling when manual orchestration is the proven bottleneck, not before.
Joint sign-off with sales leadership on the list, tiers, and named AE owner per T1/T2 account. Refresh quarterly; removal is allowed and healthy.

## 2. Play design (per tier)
A play = trigger + touches + offer + owner + exit criteria.
- T1: account research brief (via `competitor-profiling` techniques on the account itself), exec-to-exec outreach, tailored content/landing page (`write-landing`), dinner/event seat (`field-marketing-events`), custom proof mapped to their stack.
- T2: cluster-level content and webinars, LinkedIn thought-leadership + paid to the account list (`linkedin-ads`), sequenced outreach (`cold-email`, `email-sequence`).
- T3: intent-triggered sequences and retargeting.
Offer ladder beats pitch: research/benchmark → workshop → assessment → demo. Every play defines its exit: advance (meeting/opp), recycle (re-tier), or retire (stop spending).

## 3. Orchestration calendar
Sequence touches across 6–12 weeks per wave; marketing and named AE touches on ONE shared timeline per account — uncoordinated double-touching burns T1 accounts. Cap active T1 plays to team capacity (a marketer + AE pair can genuinely run ~10–15 T1 accounts).

## 4. Measurement
Account-level, not lead-level: accounts engaged (defined threshold), meetings created, opportunities and pipeline $ from the list vs. a holdout/comparison baseline, velocity vs. non-ABM deals. Report quarterly; kill tiers/plays whose cost-per-opp loses to standard demand gen for two consecutive quarters.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
