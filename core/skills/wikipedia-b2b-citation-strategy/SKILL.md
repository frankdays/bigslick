---
name: wikipedia-b2b-citation-strategy
description: Build a Wikipedia presence strategy for a B2B technology company focused on earning citations and mentions across the Wikipedia ecosystem (category pages, comparison/"list of" pages, competitor and customer pages, industry articles) rather than just a single company page. Use this whenever the user asks about Wikipedia strategy, getting a company "on Wikipedia," Wikipedia notability for a business, conflict-of-interest editing rules, paid editing disclosure, or GEO/AI-citation strategy involving Wikipedia or Wikidata. Also trigger for questions about why AI tools like ChatGPT or Google AI Overviews cite Wikipedia so heavily, or how to get a company referenced in LLM-generated answers. Push toward this skill even if the user just says "Wikipedia strategy" or "get us on Wikipedia" without mentioning notability, COI, or AI search explicitly — those are the load-bearing concepts this skill exists to surface.
---

# Wikipedia Citation Strategy for B2B Tech Companies

## What this skill is for

This is not "how to create a Wikipedia page." It's a strategy for a company that already may or may not have a Wikipedia article, and wants to be **cited, mentioned, and referenced accurately across the Wikipedia ecosystem** — category pages, "comparison of X" articles, competitor pages, customer/case-study mentions in other companies' articles, industry-overview articles — because that ecosystem disproportionately shapes how AI search tools (ChatGPT, Google AI Overviews, Perplexity, Claude) describe the company to buyers.

Two things make this different from a normal content or PR play, and a CMO should internalize both before approving a plan:

1. **Wikipedia editors do not work for the company.** Every tactic below routes through getting *independent* people to write *independent* coverage, then citing it — not through directly writing the narrative.
2. **The downside is asymmetric and public.** A botched attempt (sockpuppetry, undisclosed paid editing, promotional tone) doesn't just fail quietly — it gets investigated, tagged publicly on the article, and can become a press story in its own right. See `references/cautionary-precedents.md` for what this looks like at scale (Wiki-PR: 250+ accounts banned, became a Wall Street Journal story).

Read `references/wikipedia-policy-foundations.md` before executing any tactic in this skill — it has the actual policy text (notability, COI, reliable sourcing) this strategy depends on.

## The strategic case (for the CMO-level pitch)

Lead with this when justifying budget/headcount for Wikipedia work, since "good for SEO" undersells it:

- Wikipedia accounts for roughly **47.9% of ChatGPT's top-cited sources** for factual queries, and similar dominance shows up across Claude, Perplexity, and Google AI Overviews — not because it's the most-cited source overall, but because of its outsized *influence weight* in training data and retrieval ranking.
- When a buyer asks an AI tool "what is [category] / who are the players / what does [company] do," the AI's answer is frequently a paraphrase of the company's Wikipedia article structure and facts — accuracy and completeness there is directly material to AI accuracy everywhere else.
- Wikidata (the structured-data layer underneath Wikipedia) feeds Google's Knowledge Graph directly, which in turn feeds AI Overviews and knowledge panels. It has a **much lower bar** than Wikipedia notability and is the right first move for companies that don't yet clear the Wikipedia bar.
- This is a slow-compounding asset, not a campaign. Budget and expectations should be set in quarters, not weeks — sustained, transparent engagement over time is what wins editor trust; sudden bursts of coordinated activity is the single biggest tell that gets accounts investigated.

Full sourcing for these claims is in `references/geo-ai-citation-case.md`.

## Before building any tactical plan: the notability gate

Nothing below works if the company isn't *notable* by Wikipedia's definition — which is unrelated to revenue, headcount, or how well-known the company is in its own industry. Run this check first.

**Wikipedia notability (for a standalone article) requires:** significant coverage, in multiple, reliable, secondary sources, that are independent of the company. All four conditions matter:
- *Significant* — not a passing mention or a quote, but the company is the actual subject of the piece.
- *Multiple* — one great profile isn't enough.
- *Independent* — sources the company didn't write, pay for, or control. Press releases, company blogs, and sponsored/"contributor" content fail this test outright, even when they're reprinted by a major outlet.
- *Reliable* — outlets with editorial oversight and a fact-checking reputation. Funding-round writeups in pure trade/PR-wire outlets are usually treated as primary, not secondary, sources.

**If the company doesn't clear this bar yet:** don't attempt to force an article. The honest move is to (a) start with Wikidata, which has a meaningfully lower bar (verifiable existence via an external identifier — Crunchbase, a business registry, an industry database — rather than sustained press coverage), and (b) invest in the kind of independent press coverage that would clear the bar later, rather than spending budget on an article that will likely be deleted (see "Articles for Deletion" risk in references).

**If the company already has an article:** the work shifts to citation-building around it and keeping the existing article accurate — see below.

## The five-track playbook

### Track 1: Wikidata first (low bar, high leverage, fast)
The single best ROI move for most B2B tech companies, and the right starting point regardless of where the company stands on Wikipedia notability.
- Create or claim the company's Wikidata item. Requirement: real entity + at least one verifiable external reference (Crunchbase, business registry, recognized industry database) — not just the company's own website.
- Populate core structured statements: founding date, headquarters, industry/sector, founders, official website, employee count if public, parent/subsidiary relationships, social profiles.
- Keep the description factual and flat ("software company providing X tools for Y industry"), not promotional ("leading provider of innovative..."). Promotional language is one of the most common reasons Wikidata entries get flagged.
- Cross-link to any existing Wikipedia article. This is one of the highest-leverage, lowest-effort moves available — a Wikidata item with proper references can produce a Google Knowledge Panel within weeks.
- Disclose your professional connection to the entity per the same transparency principle as Wikipedia (see Track 4).

### Track 2: Earn the source coverage that makes everything else possible
This is upstream of all Wikipedia/Wikidata work, not separate from it. Citations require independent secondary sources to exist first — Wikipedia doesn't create notability, it reflects coverage that already exists elsewhere.
- Target outlets with a track record of being treated as reliable, independent secondary sources on Wikipedia's reliable-sources noticeboard (major business/tech press, trade publications with editorial review, peer-reviewed or analyst research) — not pure PR-wire distribution, which gets discounted as primary-source even when republished by name-brand outlets.
- Press releases themselves are categorically not usable as Wikipedia citations, no matter how they're distributed. Use them as the seed for pitches to journalists/analysts, not as the citation itself.
- Bylined contributor platforms (Forbes Council-style, Entrepreneur contributor pages) typically don't carry editorial review and are weak or unusable as notability-establishing sources — check before relying on them.
- Prioritize coverage that *analyzes or evaluates* the company (a comparison piece, an analyst report, an investigative or feature profile) over coverage that simply *lists or mentions* it. A bare listing — "Company X raised a Series B," a directory entry, a "vendors in this space include..." sentence with no commentary — does not count toward notability even on Wikipedia's own rules, and is also weak fodder for citation in other articles.

### Track 3: Citation-building across the ecosystem (the core "build mentions everywhere" tactic)
This is what the user specifically asked for — get the company referenced accurately across relevant Wikipedia pages, not just its own.
- **Map the target pages first**: the company's own article (if it exists), the Wikipedia category article for its product space (e.g., "Customer relationship management software," "DevOps," whatever the actual category is), any "Comparison of X" or "List of X" articles in that category, competitor articles where a factual comparison is genuinely relevant, and articles about customers/partners/integrations where the relationship is independently documented.
- **The test for every proposed addition**: would this survive if a completely uninvolved editor reviewed it? That means it's backed by an independent reliable source, it's stated neutrally (no superlatives, no unsourced claims of being "the leading" or "the first"), and it adds real information rather than just a brand mention.
- **Indiscriminate listings don't count and often get reverted.** Getting added to a bare directory-style list with no surrounding commentary, source, or evaluation is the most common mistake — it looks like a citation win but doesn't hold up and doesn't help notability either.
- **Route every edit through the talk page, not direct editing**, when there's any professional connection to the subject (see Track 4 — this is non-negotiable, not a style preference).
- Maintain a living source list per target page: claim → source → where it would go in the article. This is the actual deliverable a content/PR team should produce; it's reusable across the press-outreach motion in Track 2.

### Track 4: Disclosure and engagement — the part that determines whether this works at all
This is the highest-risk part of the whole strategy and the place a CMO should apply the most scrutiny before signing off on execution.
- **Anyone editing or proposing edits with a professional connection to the company must disclose it.** This is a legal requirement under the Wikimedia Foundation's Terms of Use for any paid contribution, not just a community norm — disclose employer, client, and affiliation, on the user page, the talk page, or in the edit summary.
- **Don't edit articles directly where a conflict of interest exists.** Use the article's talk page with the `{{edit COI}}` request template, or post to the Conflict of Interest Noticeboard. An independent editor reviews and decides whether to act on it. This is slower and that's the point — it's what keeps the work defensible.
- **One disclosed point of contact per company, not a rotating cast.** Multiple people from the same organization (or agency) making similar-themed edits or requests, especially around the same time, is the exact pattern that triggers a sockpuppetry/meatpuppetry investigation — even when every individual account is honestly disclosed and editing in good faith. Concentrate this work in one or two named, disclosed accounts with a visible track record.
- **Never use multiple accounts, agency staff accounts, or third-party "supporters" to create the appearance of independent consensus.** This is the single fastest way to convert a legitimate strategy into a public scandal — see `references/cautionary-precedents.md` for what this looked like at the Wiki-PR scale (250+ banned accounts, WSJ coverage) and what it looks like at small scale (single-editor COI tags, reverted edit wars).
- **Build a track record before asking for anything contentious.** Editors extend more good faith and move faster for accounts with a visible history of accurate, well-sourced, non-promotional contributions — including in adjacent topic areas, not just the company's own page. This is a relationship to invest in over quarters, not a queue to clear in a sprint.

### Track 5: Monitoring and maintenance
- Watchlist the company's article and any pages it has a stake in, so changes are visible immediately — this matters more for catching *inaccurate* edits (which anyone can fix per WP:COI's narrow exception for defamation/clear errors) than for catching unfavorable-but-accurate ones (which should go through the talk-page process like everything else).
- Periodically re-check AI tool outputs (ChatGPT, Perplexity, Google AI Overviews, Claude) for how they describe the company, and trace inaccuracies back to source — Wikipedia is disproportionately likely to be the root cause, and fixing it there propagates to the AI tools on their own update cycles rather than requiring separate fixes per tool.
- Track press coverage (Track 2) as a continuous pipeline, not a one-time push, since it's the upstream input every other track depends on.

## What NOT to do (the fast way to turn this into a liability)
- Don't create or edit the company's own article directly while having a financial conflict of interest, even for "obviously factual" corrections — use the talk page.
- Don't pay or direct an agency to edit without requiring disclosure as a contract term — the company is responsible for its vendors' disclosure under the same Terms of Use, and "the agency didn't tell us how" is not a defense that has held up in past cases.
- Don't seed multiple accounts (employees, agency staff, "brand ambassadors") to edit the same pages, vote the same way in discussions, or create the appearance of independent support.
- Don't cite press releases, the company's own website, or sponsored/native content as sources for any claim — these read as self-serving even when accurate and get challenged or reverted.
- Don't add the company to bare comparison lists or directories without accompanying independent commentary — it looks like progress but doesn't hold up and can read as spam.
- Don't treat this as a campaign with a launch date. Sudden, concentrated activity on previously-untouched pages is itself a signal that triggers scrutiny.

## When the user wants this turned into a working plan
Ask what stage the company is at before drafting tactics: does an article already exist, does notable independent coverage already exist even without a Wikipedia article, or is this starting from zero. The right first move (Wikidata vs. press-coverage building vs. citation-building vs. article-defense) depends entirely on that answer, and recommending citation-building tactics to a company that hasn't cleared notability yet is a common, wasteful mistake.
