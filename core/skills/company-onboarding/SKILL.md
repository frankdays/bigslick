---
name: company-onboarding
description: Tailor the entire marketing skill system to a specific business. Use when starting a new fractional client engagement, joining a company as CMO, or when the user says "onboard [company]", "set up a new client", "create a context pack", "configure the system for", or when any skill finds no active client pack. Produces the client context pack, resource wiring checklist, skills profile, and persona calibration. Run this FIRST for any new company — every other skill reads its output.
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

## Phase C — Skills profile

Write `skills-profile.md` (scaffold in `_template`). Relevance is data, never build config — the library stays global and is never recomposed per client.

**Step 1 — Call the motion,** from `icp.md` and `product-marketing.md`, not from what the client calls themselves. ACV and who signs decide it: under ~$15k with self-serve entry is PLG; six figures with a committee is sales-led enterprise; a public repo as the top of funnel is OSS-led. Say which and cite the evidence — a mislabelled motion mis-selects every skill below it.

**Step 2 — Map motion to a shortlist:**

| Motion | Load first |
|---|---|
| Sales-led enterprise | `abm-builder`, `field-marketing-events`, `sales-marketing-alignment`, `win-loss-program`, `case-study-builder` |
| PLG / self-serve | upstream `signup`, `onboarding`, `cro`, `churn-prevention`, plus `attribution-diagnostics` for the PQL path |
| OSS-led | `oss-devrel-gtm` first, then `reddit-b2b-tech-strategy`, `wikipedia-b2b-citation-strategy`, `ai-answer-monitoring` |
| Hybrid | Both lanes, ranked separately — never averaged |

**Step 3 — Rank 5–10 by first-90-days impact,** each with a named first deliverable. A priority skill with no deliverable is a preference, not a priority.

**Step 4 — Record what is deprioritised and what is not applicable,** with the reason and the trigger to revisit. This half matters more than the priority list: it is what stops the system reaching for a skill that does not fit this business.

Cross-check against `stack.md` — a skill whose tooling the client does not own is aspirational; flag it rather than listing it as ready.

## Phase D — Persona calibration

Write `team-map.md` (scaffold in `_template`). `staff-meeting` reads it to decide, per persona, whether to defer to a real human or run the seat outright.

Walk all seven charters — `persona-cmo`, `persona-product-marketing-director`, `persona-vp-growth`, `persona-field-marketing-director`, `persona-comms-manager`, `persona-content-seo-director`, `persona-vp-sales` — and assign each a mode:

- **full authority** — nobody holds the seat; the persona owns the lane and makes the call
- **support** — a real human holds it; the persona drafts, pressure-tests, and hands over, never overrides
- **defer** — held by someone senior to marketing (a founder doing positioning, a CEO owning analyst relations); the persona raises questions and stops there

`persona-vp-sales` is the antagonist and always runs regardless of who holds sales — its job is adversarial review, which a real VP of Sales will not do on marketing's behalf.

Then capture **decision rights** explicitly — budget sign-off, messaging sign-off, reporting line, board-facing owner. Most stalled marketing plans are a decision-rights problem wearing a strategy costume, and `staff-meeting` produces sharper output when it knows who actually decides.

Note agency and contractor coverage too: an outsourced lane is a held seat with a slower loop, not an empty one.

## Completion

Activate the client yourself by running `bash scripts/activate_client.sh <company>` from the repo root (never ask the user to run scripts — that’s your job), then run a smoke test: ask one upstream skill (e.g., `positioning` question via `product-marketing`) and verify it picks up the pack. Present the pack summary + open TBDs as the engagement's first deliverable.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
