# The GEO / AI-Citation Case for Wikipedia

This is the evidence base for the strategic pitch in SKILL.md — useful when a CMO or exec sponsor asks "why does this matter now" or wants the numbers behind the claim.

## The core finding, converged on across independent sources

Multiple independent analyses of AI citation behavior in 2026 converge on the same directional finding even though their exact percentages differ by methodology:

- Wikipedia accounts for **47.9% of ChatGPT's top-cited sources** for factual queries — this figure recurs across several independent write-ups analyzing the same underlying citation dataset.
- One analysis frames the structural reason clearly: Wikipedia isn't the most frequently cited source in AI answers. It's the most influential one — operating through three pathways: as foundational training data (~22% of major LLM training data by influence weight), as the primary source for Google's Knowledge Graph (feeding AI Overviews on 54.61% of all global searches), and as a live retrieval source.
- A separate writeup states the implication plainly: for most factual questions about a brand, a founder, a product, or a category, Wikipedia presence is not a factor in AI visibility. It is the factor... a complete, accurate, current Wikipedia article is one of the highest-leverage assets a brand can hold.
- This dominance is consistent across engines, not unique to ChatGPT: similar Wikipedia dominance shows up across Claude, Perplexity, and Google AI Overviews. The percentages differ; the directional signal is identical.

## Why this happens structurally (useful for explaining "why Wikipedia specifically" to skeptics)

Three structural drivers explain the concentration: Wikipedia was one of the largest, cleanest datasets in every major LLM's training corpus; Wikipedia ranks at or near the top of AI retrieval pools because its domain authority is high and its articles parse cleanly; and Wikipedia is a low-cost, high-credibility citation for the model.

This has been true since early LLM training, not just a recent AI-search-era phenomenon: Wikipedia content makes up 3% of GPT-3's training data — a small percentage of total data, but disproportionate influence given the encyclopedia's role as a reference training base.

## Why accuracy on Wikipedia specifically propagates outward

This is the mechanism worth explaining to a skeptical exec: fixing something on Wikipedia isn't just fixing one page, it's fixing the upstream source multiple AI tools draw from.

The pattern is recognizable: ChatGPT's answer about a company often follows the structure of the Wikipedia lead section, uses the same descriptive language, and incorporates the same key facts. That makes Wikipedia accuracy directly material to ChatGPT accuracy... when clients see an AI engine giving an unfair description of them, the underlying source is most often the Wikipedia article. Fixing the article is usually the highest-leverage intervention available, because the change propagates into ChatGPT and the other engines on their respective update cycles.

## Wikidata's specific role (the lower-bar entry point)

Distinct from Wikipedia itself, structurally: Wikidata is the data layer underneath: a structured database where each entity has a unique identifier (a Q number) and a set of factual statements expressed as property-value pairs. When Google's Knowledge Graph resolves your brand name, it queries Wikidata.

Direct consequence for visibility: when Google's Knowledge Graph contains accurate entity data, engines that draw on Google — Gemini, AI Overviews — inherit that accuracy.

## Caveats worth flagging to set realistic expectations

- AI platforms diverge meaningfully in *which* other sources they pair Wikipedia with and how much weight they give real-time vs. training-data sources: the platforms diverge significantly: ChatGPT relies heavily on Wikipedia and parametric knowledge, Perplexity emphasizes real-time Reddit content, Google AI Overviews favor diversified cross-platform presence... only 11% of domains are cited by both ChatGPT and Perplexity. Don't assume a Wikipedia-only strategy covers all AI surfaces equally — it's the highest-leverage single move, not the only one needed.
- Even holding a top organic search ranking doesn't guarantee AI Overview inclusion: across tens of thousands of keywords where Wikipedia holds an organic ranking and an AI Overview is present, Wikipedia makes it into the AIO on fewer than half of those queries — when it is cited, it holds a top-3 organic ranking 75% of the time, suggesting accurate facts alone aren't sufficient without surrounding SEO/discoverability work too.
- Treat specific percentage figures as illustrative of a real, large, and consistent effect rather than precise enough to build a single KPI around — they come from third-party analyses of proprietary citation datasets with differing methodologies, not from official Wikipedia or model-provider disclosures.
