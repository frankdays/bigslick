---
name: company-onboarding
description: Tailor the entire marketing skill system to a specific business. Use when starting a new fractional client engagement, joining a company as CMO, or when the user says "onboard [company]", "set up a new client", "create a context pack", "configure the system for", or when any skill finds no active client pack. Produces the client context pack, resource wiring checklist, and (v2) skills profile and persona calibration. Run this FIRST for any new company — every other skill reads its output.
---

# Company Onboarding

Configures the library for one business. Output lands in `clients/<company>/`; activate with `scripts/activate_client.sh <company>`.

## Phase A — Context intake (core deliverable)

Run as a structured interview OR extract from provided materials (website, pitch deck, prior docs) and confirm gaps. Never fabricate — mark unknowns as `TBD (owner: ___)`. Time-box: a working session, not a research project; a 70%-complete pack today beats a perfect one in three weeks.

Interview flow (adapt depth to what's already known):

1. **Business basics** — what they sell in one sentence, ARR band, funding stage, growth target, business model (sales-led / PLG / hybrid), ACV band, sales cycle length.
2. **GTM motion** — how revenue actually happens today: inbound/outbound mix, top 2 working channels, top 2 failed channels, marketing team size and roles, sales team size.
3. **ICP & buying committee** — firmographics, the 2–3 personas who champion/approve/block, trigger events that start a buying process, disqualifiers.
4. **Positioning** — category claim, alternative the buyer would otherwise choose, top 3 value props with proof points, 1–2 sentences on why they win and why they lose.
5. **Competitors** — 3–5 named, with one-line "how we beat them" and "where they beat us" each.
6. **Voice** — 3 adjectives, 3 banned phrases/claims, one example of on-brand copy they love.
7. **Stack & data** — CRM, analytics, SEO/ads tools + who pays for each, where pipeline numbers live, known data-quality problems.
8. **Funnel definitions & baselines** — agreed definitions of MQL/SQL/opp/sourced/influenced (get sales ops' version, note disputes), plus last 4 quarters of actuals: pipeline created, funnel conversion by stage, closed-won by source, new vs. expansion ARR split. Validate against CRM reality — treat unaudited CRM numbers as claims, not facts. Write to `metrics-baseline.md`; `pipeline-math` and `board-reporting` depend on this file.
9. **Constraints** — budget band, sacred cows, compliance/legal review requirements, exec opinions that shape marketing whether right or wrong.

Write the pack (use `clients/_template/` structure): `product-marketing.md` (master summary — this is what skills read), `icp.md`, `messaging.md`, `competitors.md`, `voice.md`, `stack.md`. Keep the master file under ~150 lines; depth goes in the topic files.

## Phase B — Resource wiring

From `stack.md`, produce `setup-checklist.md` in the client folder:
- Which resource-hub capabilities route to the client's own subscriptions (their Ahrefs/Semrush seat, their ad accounts) vs. your defaults — list exact `registry.yaml` deltas but do NOT edit the global registry; per-client routing notes live in `stack.md`.
- Required connections/env vars and who provides credentials.
- MCP connectors to enable (CRM, analytics) and any that are unavailable in the current environment — flag, don't emulate.

## Phase C — Skills profile (v2 — light version now)

Write `skills-profile.md`: 5–10 priority skills for this business model (e.g., PLG → onboarding/signup/cro; sales-led enterprise → abm/field-marketing-events/sales-enablement), and skills irrelevant to it. Skills read this as context. Never recompose the library per client — relevance is data, not build config.

## Phase D — Persona calibration (v2 — light version now)

Write `team-map.md`: for each persona charter, note whether a real human holds the seat (persona defers/supports) or the seat is empty (persona runs at full authority). The staff-meeting skill reads this.

## Completion

Activate the client yourself by running `bash scripts/activate_client.sh <company>` from the repo root (never ask the user to run scripts — that’s your job), then run a smoke test: ask one upstream skill (e.g., `positioning` question via `product-marketing`) and verify it picks up the pack. Present the pack summary + open TBDs as the engagement's first deliverable.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
