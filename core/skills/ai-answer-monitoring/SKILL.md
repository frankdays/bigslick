---
name: ai-answer-monitoring
description: Measure and report a company's visibility in AI-generated answers — ChatGPT, Perplexity, Claude, Google AI Overviews. Use when the user mentions "AI visibility", "share of voice in AI", "does ChatGPT recommend us", "GEO reporting", "AI search monitoring", "how do AI tools describe us", "LLM citations", or wants a recurring report on AI-answer presence vs competitors. This is the measurement layer above the reddit, wikipedia, and review-site citation skills — it produces the AI Visibility Report and routes gaps back to those skills.
---

# AI Answer Monitoring & Share of Voice

Read the active client pack — ICP language defines the query set; the competitor list defines who we score against.

## 1. Build the query set (once per client, refresh quarterly)

30–60 queries across four intents, phrased how buyers actually ask (mine from: sales call language, `geo-query-finder` output, ICP pain points):
- **Category**: "best [category] software for [segment/vertical]"
- **Comparison**: "[client] vs [competitor]", "alternatives to [competitor]"
- **Problem**: "how do I solve [pain the product addresses]"
- **Brand**: "what is [client]", "is [client] good for [use case]"
Lock the set. Consistency across runs is what makes trends real; changing queries mid-stream invalidates the trend line.

## 2. Run the sweep (monthly)

Query each engine in scope — ChatGPT, Perplexity, Google AI Overviews, Claude — via resource-hub (`research_synthesis` capability + upstream `geo-analysis`/`ai-citations-report` tools where wired; manual spot-runs where APIs aren't available; log the method per engine).
Methodology discipline (this is what makes the report defensible):
- Same queries, fresh sessions, no account personalization, logged date/engine/model version.
- 2–3 runs per query per engine where feasible — AI answers vary; single samples are anecdotes. Score on the aggregate.
- Store raw answers; the quotes are the qualitative gold.

## 3. Score

Per query/engine, record: client mentioned? (position: recommended / listed / absent), sentiment/framing of the description (accurate? stale? wrong?), competitors mentioned, and **which sources were cited** for the answer (the attribution that drives strategy).
Roll up to: **Share of Voice** (% of queries where client appears, weighted by position), SoV vs. each competitor, and citation-source mix (Reddit / Wikipedia / review sites / own site / press / other).

## 4. The AI Visibility Report (monthly recurring deliverable)

1. Headline: SoV this month vs. last, vs. top competitor.
2. Wins/losses: queries gained or lost, with the answer excerpts.
3. **How AI describes us** — the verbatim framings, flagged where wrong or stale (this section reliably gets exec attention).
4. Citation-source analysis: what's driving competitor appearances that we lack.
5. Action routing — every gap maps to an owner skill: community gaps → `reddit-b2b-tech-strategy`; knowledge-graph/comparison-page gaps → `wikipedia-b2b-citation-strategy`; review gaps → `review-site-strategy`; own-content gaps → `ai-seo` / `seo-content-brief`; wrong facts about the company → correction plan (source-by-source).
6. Trend appendix: SoV line per engine since tracking began, annotated with (a) known engine/model releases and (b) the month each GEO action shipped (wikipedia edit live, review campaign run, reddit thread traction) — without action annotations the trend supports no causation claim, and the report will get asked for one.

## 5. Honest limitations (state in every report)

Sampling variance is real; month-over-month noise of a few points is not signal — act on 2–3 month trends. Engine model updates can reset landscapes overnight — annotate known model releases on the trend line. This measures *answer presence*, not revenue; pair with source-referral data where engines send traffic.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
