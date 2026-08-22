---
name: martech-stack-auditor
description: Audit a company's marketing technology stack — utilization, overlap, cost, and consolidation. Use when the user mentions "martech audit", "tool audit", "stack review", "are we paying for tools we don't use", "consolidate tools", "martech budget", "tool renewal", or budget season pressure on the software line. Produces the audit report and renewal-decision calendar.
---
# Martech Stack Auditor
Read the active client pack's `stack.md` — it's the audit's starting inventory (and the audit's output updates it).

## 1. Inventory (trust invoices, not memory)
Build the true list from: finance's software spend report (catches shadow tools bought on cards), SSO/identity provider app list, and the team's claimed stack. For each tool: annual cost, owner (a name, not a team), renewal date + auto-renew terms + notice window, seats purchased vs. seats active (pull usage where the tool or MCP exposes it, via resource-hub), and the job it was bought to do.

## 2. Score each tool on three axes
- **Utilization:** active users / paid seats, and depth (logins ≠ usage — is the core feature used?). Under 40% seat utilization = automatic review.
- **Redundancy:** map tools to jobs (email, analytics, SEO, enrichment, social, CMS, webinar, attribution…). Two tools per job needs a written reason; three is a decision waiting.
- **Criticality:** what breaks if it vanishes tomorrow, and how painful is migration (data gravity, integrations, retraining).

## 3. Decisions
Bucket every tool: KEEP (used, earning), CONSOLIDATE (job moves to an adjacent tool already paid for — the usual biggest saving), DOWNGRADE (fewer seats/lower tier), KILL (with a migration/export note), WATCH (renewal-time decision, calendared). Typical finding at $30–100M companies: 15–30% of martech spend is recoverable without capability loss — but net the switching cost (migration hours, retraining, integration rebuild) before claiming savings.
Renewal calendar: every renewal date with its notice deadline and the pre-made decision — auto-renews are where dead tools hide.

## 4. Deliverable & cadence
Audit report: inventory table, spend by job category, the decision buckets with annualized savings, top 3 consolidation moves with effort estimates, and the renewal calendar. Update `stack.md` and the resource-hub per-client routing notes to match reality. Run annually (budget season) plus a light renewal-calendar check quarterly. Adding tools between audits requires: the job named, the incumbent tool's failure named, and an owner — write it into stack.md at purchase.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
