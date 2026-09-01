---
name: resource-hub
description: Central registry of LLM providers, APIs, and external capabilities for all marketing skills. ALWAYS load this skill before making any external LLM call, API request, data-enrichment lookup, web research beyond built-in search, image generation, or SERP/SEO data pull from within another skill. Also use when the user wants to add, swap, or configure a model or API provider, asks "which model/tool should handle X," or mentions routing, fallbacks, API keys, or provider costs. First-party skills consult this hub instead of hardcoding any provider, model string, or endpoint; vendored upstream skills name their own and are documented in INVENTORY.md.
---

# Resource Hub

A shared capability layer for the marketing skill library. Skills describe **what** they need (e.g., "deep research," "bulk classification," "contact enrichment"); this hub decides **which provider** fulfills it and **how** to call it.

## Design contract (read this first)

1. **No skill ever hardcodes a provider, model string, endpoint, or API key.** Skills request a *capability* by name.
2. **All provider specifics live in `config/registry.yaml`.** Changing a model or adding an API means editing that one file — no skill files change.
3. **All credentials come from environment variables** named in the registry. Never write keys into any file.
4. **Client context stays in client packs, never here.** This hub is provider knowledge only.

## Scope (read this second)

This hub is authoritative for **first-party skills in `core/skills/`** and for the user's own
provider configuration. The 207 vendored upstream skills are read-only and were written
without it — where they need an external service they name it directly, and `INVENTORY.md`
records which env vars each one expects. Do not rewrite an upstream skill to route through
here; if the routing genuinely matters for one, add a patch under `overlay/patches/<skill>/`
and accept the merge cost at the next upstream refresh.

So: use the registry as the single place to record what is configured and which key lives
where, and as the routing layer for anything first-party. It is not a claim that every
skill in the distribution obeys it.

## How other skills call the hub

Any skill that needs an external capability includes one line in its own SKILL.md:

> *For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.*

Then, at execution time:

1. Read `config/registry.yaml` to find the provider assigned to the needed capability.
2. If you need call details (auth pattern, request shape, quirks), read the matching section in `references/providers.md`.
3. For LLM calls from code, use `scripts/call_llm.py` — it reads the registry so the calling skill stays provider-agnostic:

```bash
python scripts/call_llm.py --capability research_synthesis --prompt "..."
python scripts/call_llm.py --capability bulk_classification --prompt-file items.txt
```

4. If the primary provider fails or its env var is missing, follow the `fallbacks` chain in the registry. If all fallbacks are exhausted, tell the user which env var or provider is missing rather than silently degrading.

## Capability routing

The registry defines these capability slots (see `references/routing.md` for the full decision guide):

| Capability | Use for | Default class of provider |
|---|---|---|
| `deep_reasoning` | Strategy docs, positioning, complex analysis | Frontier LLM |
| `research_synthesis` | Web research with citations | Search-native LLM / web search |
| `bulk_classification` | Tagging, scoring, cleaning lists at volume | Small/cheap LLM |
| `long_context_analysis` | Analyzing transcripts, big docs, exports | Large-context LLM |
| `embeddings` | Similarity, clustering, content dedupe | Embedding API |
| `image_generation` | Ad concepts, social visuals | Image model API |
| `serp_seo_data` | Keywords, rankings, backlinks | SEO data API |
| `contact_enrichment` | Person/company data for ABM & outreach | Enrichment API |
| `crm_data` | Contacts, deals, campaign data | CRM (HubSpot MCP, etc.) |
| `social_data` | LinkedIn profiles, posts, engagement | Social API/MCP (ConnectSafely, etc.) |

## Environment awareness

Where this library runs changes what's callable:

- **Claude Code / local / n8n:** full registry available — any provider whose env var is set.
- **Claude.ai chat/Cowork:** outbound network from code is restricted to an allowlist (Anthropic API works; most third-party APIs do not). Prefer built-in tools (web search, connected MCPs like HubSpot) for those capabilities, and note the substitution to the user.
- Before calling any provider from code, check the env var exists; if not, fall back per the registry or use a built-in equivalent.

## Maintaining the hub

- **Add a provider:** append it under `providers:` in `config/registry.yaml`, add a short section to `references/providers.md`, and (optionally) point a capability at it.
- **Swap a model:** change the `model` field in the registry. Done.
- **Retire a provider:** remove it from capability assignments first, then from `providers:`.
- Review quarterly alongside the skill-library review: check per-capability costs, new model releases, and whether fallbacks ever fired.
