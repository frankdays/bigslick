# Capability Routing Guide

How to pick the right capability slot when a skill needs external help. Read this when the mapping isn't obvious; the assignments themselves live in `config/registry.yaml`.

## Decision rules

**Default to built-in tools first.** If the current environment already has web search, an MCP connector (HubSpot, ConnectSafely, Google Drive), or native document handling, use it. Reach for the registry when you need a capability the environment lacks, a specific provider's strength, or programmatic volume.

**deep_reasoning** — one-shot, high-stakes thinking: positioning frameworks, strategy docs, complex tradeoff analysis. Cost per call is irrelevant; quality is everything. Never route bulk work here.

**research_synthesis** — questions answerable from the live web with citations: competitor moves, market stats, trend scans. Also the slot for GEO monitoring (querying AI engines about how they describe a brand vs. competitors).

**bulk_classification** — anything run over a list: lead tagging, content audits, sentiment on reviews, cleaning CSV exports. Route to the cheapest model that passes a 20-row spot check; escalate the failures (and only the failures) to a stronger model.

**long_context_analysis** — single large inputs: call transcripts, analytics exports, a quarter of blog content. Pick by context window, not reasoning strength.

**embeddings** — similarity work: dedupe content ideas, cluster keywords, match case studies to prospects.

**image_generation** — concept visuals and social graphics. Client brand assets belong in the client pack, not here.

**serp_seo_data / contact_enrichment / crm_data / social_data** — structured data pulls. Always prefer an MCP connection when one is available in the environment; fall back to raw APIs in code-first environments (Claude Code, n8n).

## Multi-client note

Provider choice is global (this hub); *budget* is per-client. If a client pays for their own Ahrefs/Semrush/Clay seat, record that in the client pack's `stack.md` and use their subscription for their work — the registry lists which providers are interchangeable per capability.

## Anti-patterns

- A skill naming a model ("use GPT-x for this step") — name a capability instead.
- Routing bulk jobs to frontier models "to be safe."
- Storing an API key anywhere but an environment variable.
- Silently substituting a weaker provider without telling the user a fallback fired.
