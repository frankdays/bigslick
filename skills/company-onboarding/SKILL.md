---
name: company-onboarding
description: Tailor the entire marketing skill system to a specific business. Use when starting a new client engagement, joining a company as CMO, setting up Big Slick for the first time, or when the user says "onboard [company]", "set up a new client", "create a context pack", "configure this for my business", or when any skill finds no company context. Offers a 10-minute express path, a standard interview, and a full audit. Produces the context pack every other skill reads, plus an installable company-context skill. Run this FIRST.
---

# Company Onboarding

Configures the library for one business. Everything else in Big Slick gives generic advice
until this has run.

## Pick a depth first — ask, don't assume

Say what the three cost and let the user choose. Most people should start at Express; a
70%-complete pack today beats a perfect one that never gets finished.

| | Time | Good for |
|---|---|---|
| **Express** | ~10 min | Getting to useful answers today. You draft, they correct. |
| **Standard** | ~40 min | A real engagement. Structured interview. |
| **Full** | 2–4 hrs, usually across sessions | Fractional CMO or new-in-seat. Adds audit, economics, competitive teardown. |

Express and Standard can be upgraded later — say so, so nobody feels they picked wrong.
Never fabricate: mark anything unknown `TBD (owner: ___)`.

---

## EXPRESS — 10 minutes

The point is to do the work *for* them and have them correct it. Correcting a draft is far
easier than answering from a blank page, and it is why this path actually gets finished.

1. **Ask for three things only:** the company URL, one sentence on what they sell, and who
   they sell to.
2. **Go and read.** Fetch the site — homepage, pricing, about, customers. Pull positioning,
   ICP signals, proof points, voice, and named competitors from what is actually published.
3. **Draft the whole pack from that**, marking every inference `(assumed)`.
4. **Show them the summary and ask for corrections in one pass.** "Here's what I concluded.
   What's wrong?" Not a question list.
5. **Ask only the two things a website never reveals:** what actually generates revenue today
   (inbound/outbound/PLG/sales-led), and their single biggest marketing problem right now.
6. Write the pack, generate the context skill, done.

---

## STANDARD — the interview

Run as a structured interview, OR extract from provided materials (website, deck, prior docs)
and confirm gaps. Time-box it: a working session, not a research project.

1. **Business basics** — what they sell in one sentence, ARR band, funding stage, growth target, business model (sales-led / PLG / hybrid), ACV band, sales cycle length.
2. **GTM motion** — how revenue actually happens today: inbound/outbound mix, top 2 working channels, top 2 failed channels, marketing team size and roles, sales team size.
3. **ICP & buying committee** — firmographics, the 2–3 personas who champion/approve/block, trigger events that start a buying process, disqualifiers.
4. **Positioning** — category claim, alternative the buyer would otherwise choose, top 3 value props with proof points, 1–2 sentences on why they win and why they lose.
5. **Competitors** — 3–5 named, with one-line "how we beat them" and "where they beat us" each.
6. **Voice** — 3 adjectives, 3 banned phrases/claims, one example of on-brand copy they love.
7. **Stack & data** — CRM, analytics, SEO/ads tools + who pays for each, where pipeline numbers live, known data-quality problems.
8. **Funnel definitions & baselines** — agreed definitions of MQL/SQL/opp/sourced/influenced (get sales ops' version, note disputes), plus last 4 quarters of actuals: pipeline created, funnel conversion by stage, closed-won by source, new vs. expansion ARR split. Validate against CRM reality — treat unaudited CRM numbers as claims, not facts. Write to `metrics-baseline.md`; `pipeline-review`, `performance-report` and `revops` depend on this file.
9. **Constraints** — budget band, sacred cows, compliance/legal review requirements, exec opinions that shape marketing whether right or wrong.

---

## FULL — the audit tier

Everything in Standard, then the work a new CMO would do in their first fortnight. Expect
several sessions; save after each phase so nothing is lost.

**F1 — Revenue reality.** Last 8 quarters: pipeline created and closed-won by source, win
rate by segment, sales-cycle length by ACV band, new vs expansion split, CAC by channel and
payback period. Ask what they believe drives revenue, then check it against the numbers and
name the gap — that gap is usually the most valuable output of the whole engagement.

**F2 — Buying committee.** For the last 5 wins and 5 losses: who championed, who signed, who
blocked, what triggered the search, what the runner-up was, why they won or lost. Themes here
beat any persona template.

**F3 — Competitive teardown.** For the 3–5 competitors that actually appear in deals: their
positioning claim, pricing model, where they beat you, where you beat them, and the objection
each one plants in a prospect's head. Note which are real threats versus mentioned-once noise.

**F4 — Channel economics.** Per channel: spend, sourced pipeline, cost per opportunity,
payback. Rank by efficiency, not volume. Identify the one channel to cut and the one to
double — and say so plainly.

**F5 — Content and demand audit.** What exists, what ranks, what converts, what is stale.
Map to funnel stage and find the gaps where prospects go unanswered.

**F6 — Stack and data quality.** Beyond the tool list: who owns each system, what the
attribution model actually is, where numbers disagree between tools, what nobody trusts.

**F7 — Constraints and politics.** Budget band and who controls it, sacred cows, compliance
and legal review, exec opinions that shape marketing whether right or wrong, and what has
already been tried and failed. Skipping this produces plans that die on contact.

**F8 — The first 90 days.** From everything above: 3 priorities, what to stop, what to
measure, and what "working" looks like at day 90. This is the deliverable the engagement is
judged on.

---

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
| Sales-led enterprise | `sales-enablement`, `battlecard-generator`, `competitor-intel`, `customer-story-builder`, `pipeline-review`, `predictable-revenue` |
| PLG / self-serve | `signup`, `onboarding`, `cro`, `churn-prevention`, `paywalls`, `growth-funnel`, plus `attribution` for the PQL path |
| OSS-led | `open-source`, `github-repo-signals`, `community-marketing`, `reddit-marketing`, `ai-seo` |
| Hybrid | Both lanes, ranked separately — never averaged |

Most of those live in opt-in bundles rather than the default install, so name the bundle
alongside the skill (`bigslick-gtm`, `bigslick-lifecycle`, `bigslick-seo`, `bigslick-social`)
and tell the user which one or two to install. Recommending a skill they do not have is worse
than recommending nothing.

**Step 3 — Rank 5–10 by first-90-days impact,** each with a named first deliverable. A priority skill with no deliverable is a preference, not a priority.

**Step 4 — Record what is deprioritised and what is not applicable,** with the reason and the trigger to revisit. This half matters more than the priority list: it is what stops the system reaching for a skill that does not fit this business.

Cross-check against `stack.md` — a skill whose tooling the client does not own is aspirational; flag it rather than listing it as ready.

## Phase D — Team map and decision rights

Write `team-map.md` (scaffold in `_template`). It records who actually holds each marketing
seat, so you know what to delegate to the client's people and what to run yourself.

For each lane — positioning/product marketing, growth/demand, content/SEO, comms/PR, field
and events, revenue ops — record one of:

- **vacant** — nobody holds it; you run the lane outright
- **held** — a real human owns it; you draft, pressure-test and hand over, never override
- **above marketing** — owned by a founder or CEO (positioning and analyst relations often
  are); you raise questions and stop there

Note agency and contractor coverage too: an outsourced lane is a held seat with a slower
loop, not an empty one.

Then capture **decision rights** explicitly — budget sign-off, messaging sign-off, reporting
line, board-facing owner. Most stalled marketing plans are a decision-rights problem wearing
a strategy costume.

`marketing-council` reads this file when it reviews a plan, so it knows which objections land
on someone real and which are yours to resolve.

## Completion — make the context portable, then prove it works

The pack on its own is markdown in a folder, and skills locate it by a relative path. That
only resolves when Claude Code runs from this repo. In the desktop app, or from the user's own
project directory, it silently does nothing — and the user cannot tell, because skills that
find no context just quietly ask more questions. Do not leave them there.

**1. Activate the pack** (never ask the user to run scripts — that is your job):

```bash
bash scripts/activate_client.sh <company>
```

**2. Build the portable context skill:**

```bash
python3 scripts/make_context_plugin.py <company>
```

This packages the pack as a `company-context` skill that loads wherever Claude runs. The
script prints the two install routes; give the user the one matching their app:

- **Claude Code:** `claude plugin marketplace add <printed path>` then `claude plugin install bigslick-context-<company>`
- **Desktop app:** upload the printed `company-context.zip` under Settings → Capabilities → Skills

Tell them to re-run the script after any change to the pack.

**3. Verify it landed.** Ask a question only their pack can answer — "who's our ICP?" or "who
do we lose deals to?" A correct answer means the context is live. A request to describe their
business again means it is not, and the install step did not take.

**4. Report honestly.** Present the pack summary, the open `TBD`s with owners, and which depth
tier was run. If they chose Express, say plainly what is still assumed and what upgrading to
Standard or Full would add.

Run `bash scripts/check_client_pack.sh <company>` if you want a mechanical check of what was
actually written.
