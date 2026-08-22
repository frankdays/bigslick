---
name: oss-devrel-gtm
description: Build and run go-to-market for an open-source or open-core product. Use when the user mentions "open source", "OSS", "open-core", "community edition", "self-hosted vs cloud", "DevRel", "developer relations", "developer advocate", "GitHub stars", "npm/PyPI/Docker downloads", "contributors", "community to cloud", "monetizing our open source", "what do we put in the paid tier", "should we relicense", "BSL/AGPL/MIT", or when planning launch, adoption, or monetization for a project whose primary distribution is a public repo. The community→cloud→enterprise motion is not the SaaS funnel with different words; use this instead of generic demand-gen skills when the product is downloaded rather than signed up for.
---

# Open-Source GTM & DevRel

Read the active client pack (`.agents/product-marketing.md`) first — the OSS model, license, and monetization boundary change every recommendation below. If no pack exists, run `company-onboarding`.

**Check this is the right skill.** Having a public repo does not make a company an OSS business. If the repo is a marketing artifact (SDK, examples, a CLI wrapper around a closed API), use the standard demand-gen path and upstream `community-marketing`; come back here only when adoption of the open artifact *is* the top of the funnel.

## Step 1 — Name the model and the monetization boundary

Everything downstream depends on which of these the client actually is. Get it in writing; teams are routinely fuzzy about it, and the fuzziness is why the paid tier doesn't convert.

| Model | Free artifact | Paid artifact | Conversion pressure comes from |
|---|---|---|---|
| Open-core | Full-featured core | Enterprise features (SSO, RBAC, audit, multi-tenancy, compliance) | Org size and governance requirements |
| COSS + managed cloud | Everything, self-hostable | Not operating it yourself | Ops burden and on-call cost |
| Source-available (BSL/SSPL) | Read/modify/use, non-compete | Production or competing use | License terms |
| Foundation-governed | The project (neutrally owned) | Support, distro, tooling, certification | Risk transfer and expertise |

Then write the **boundary rule** as one sentence the whole company can repeat — for example: *"Anything a single developer needs is free forever; anything an organization needs to run it safely is paid."* Test every proposed paid feature against it.

**The boundary error that kills adoption:** putting something in the paid tier that a solo developer hits on day one. A rate limit, a node cap, or a single-user-only auth model turns evaluation into a wall, and the developer leaves without ever seeing the value. Enterprise buyers pay for organizational needs, not for the removal of artificial friction.

## Step 2 — Build the real funnel (stars are not the funnel)

Stars are a weak leading indicator: cheap to acquire, uncorrelated with revenue, easy to game, and the metric most likely to be presented to a board in place of something that matters. Track them, never target them.

The chain to instrument, in order of increasing signal:

```
impressions (HN/Reddit/socials/search/AI answers)
  → repo visits
  → stars                      weak — interest, not intent
  → clones / downloads         npm, PyPI, crates, Docker pulls, releases
  → successful install         first run completed (needs telemetry or proxy)
  → active deployment          recurring usage, >1 instance, sustained
  → org signal                 multiple users at one domain/GitHub org
  → commercial conversation    inbound, or sourced from org signal
  → paid
```

**Instrument the install→active gap or you are flying blind.** Options in descending order of honesty: opt-in anonymous telemetry (disclose it in the README, make opt-out one flag — the disclosure is itself trust content); registry download counts (noisy, inflated by CI); docs analytics on the quickstart page vs the "next steps" page (drop-off there is a time-to-value problem, not a marketing problem).

Feed the PLG lane of `pipeline-math` with the install→active→org-signal rates. OSS conversion rates are lower and slower than SaaS trial rates and belong in their own lane — blending them into a single funnel model produces a plan that misses.

## Step 3 — Time to value is the campaign

For a downloaded product, the quickstart *is* the landing page and the docs *are* the product surface. No amount of demand generation survives a broken first run.

- **Ten minutes, one command, no signup.** Time the quickstart on a clean machine every release; treat a regression as a P1. If it needs an account, a key, or a cloud dependency to see value, adoption is capped no matter what the campaign spends.
- **Docs are ranked content.** They are usually the highest-authority pages the company owns and the most-cited by AI answer engines — coordinate with `ai-answer-monitoring` and treat docs coverage of category questions as SEO/GEO surface, not internal reference.
- **Examples over explanation.** Runnable examples per use case beat conceptual documentation for adoption; conceptual docs matter later, for the people already committed.
- **Publish the roadmap and the boundary.** Ambiguity about what will always be free is the single most common reason a cautious engineering team refuses to adopt.

## Step 4 — The community→commercial handoff, without burning the community

This is where OSS GTM most often destroys the asset it depends on. The community is not a lead list, and treating it as one is visible immediately and remembered for years.

**Legitimate sourcing signals:** multiple users from one email domain or GitHub org; enterprise-shaped questions in public channels (HA, air-gapped installs, SSO, compliance, support SLAs); scale questions that imply production; inbound from a corporate address.

**Rules that keep the well from being poisoned:**
- Answer the question in public, fully, with no gate — before any commercial motion.
- Never DM someone because they starred the repo, and never pitch inside a support thread.
- Sales must not be the first commercial contact; DevRel or a founder is.
- Never make a helpful answer conditional on a call.

**Hand off to `abm-builder`** once an org signal appears — that is the moment the account becomes a named target, and OSS usage data is the strongest account-intelligence a marketing team will ever get. Route the person-level research through `linkedin-connectsafely-search`, never through community-channel scraping.

## Step 5 — Licensing is a GTM decision, not a legal one

Advise on it explicitly; teams treat it as paperwork until it is a crisis.

| License | Adoption | Monetization leverage | Cost |
|---|---|---|---|
| MIT / Apache-2.0 | Highest — zero friction, corporate-safe | Lowest — anyone may host it | Hyperscaler competition risk |
| AGPL | Moderate — many corporates ban it | Copyleft pushes companies to a commercial license | Loses the ban-listed segment entirely |
| BSL / SSPL / source-available | Moderate — "not open source" backlash | Highest — competing use is prohibited | Foundation/OSI exclusion, community trust hit |

**Relicensing is the highest-risk move in this playbook.** Every prominent relicense has produced a hostile fork, a wave of press, and a permanent trust cost. If the client is considering it: model the fork scenario explicitly, decide whether it can survive one, communicate before rather than after, grandfather existing users, and never frame it as a community benefit when it is a revenue decision. Involve `persona-comms-manager` and treat it as a crisis-comms exercise from day one.

## Step 6 — The DevRel program

Staff and measure DevRel as a distinct function; scored as demand gen, it will be cut, and scored as support, it will be wasted.

- **Owned deliverables:** quickstart and docs quality, examples, release notes developers actually read, talks and workshops, office hours, contributor onboarding, community moderation.
- **Contributor ladder:** first issue → first PR merged → repeat contributor → maintainer. Track conversion between rungs; a project with stars and no repeat contributors is a marketing asset, not a project.
- **Measure on:** time-to-first-successful-run, docs coverage of top support questions, repeat-contributor count, community question response time, and org signals generated. Not stars, not follower counts.
- **Do not put DevRel on a lead quota.** The credibility that makes the function work is exactly what a quota destroys.

## Benchmarks (COSS reference — replace with client actuals ASAP)

| Metric | Typical range |
|---|---|
| Stars → meaningful install | 1–5% |
| Active deployments → org signal | 5–15% |
| Org signal → commercial conversation | 10–25% |
| Community edition → paid conversion (annual) | 0.1–1% of active orgs |
| Time from first install to paid | 6–18 months |
| Repeat contributors, healthy project | >10% of first-time contributors |

Treat these as priors, mark them `ASSUMED` in any model, and replace them the moment telemetry exists.

## Anti-patterns

Gating the quickstart or docs behind signup · targeting stars in a board deck · a paid tier a solo developer hits on day one · sales in community channels · closing a public channel to move conversations to a CRM · a relicense announced as a gift to users · DevRel reporting into sales with a pipeline quota · shipping the managed cloud with features the self-hosted edition silently lacks.

## Output

Deliver an **OSS GTM plan**: model and boundary rule → funnel instrumentation gaps (what cannot currently be measured, and the cheapest way to fix each) → time-to-value audit of the current quickstart → community→commercial rules of engagement → licensing position and risk → DevRel charter with its own scorecard.
Feed the funnel rates into `pipeline-math` as the PLG lane; feed adoption metrics into `board-reporting` under their own headings, never blended with MQLs; take community-channel strategy from `reddit-b2b-tech-strategy` and citation strategy from `wikipedia-b2b-citation-strategy` and `ai-answer-monitoring`; source adopter stories via `case-study-builder`.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
