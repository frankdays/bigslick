# Provider Notes

Call details and quirks per provider. Read the section you need; the authoritative assignments are in `config/registry.yaml`.

## Anthropic (Claude)
- Auth: `x-api-key` header + `anthropic-version: 2023-06-01`; POST to `/v1/messages`.
- Response text is in `content[]` blocks of `type: "text"` — concatenate them; don't assume position.
- The only LLM API reachable from the Claude.ai code sandbox.
- Docs: https://docs.claude.com/en/api/overview

## OpenAI-compatible providers (OpenAI, Perplexity, many others)
- Auth: `Authorization: Bearer <key>`; POST to a `/chat/completions` endpoint.
- Response text: `choices[0].message.content`.
- Perplexity responses include citations — preserve them in research outputs.
- `scripts/call_llm.py` uses this shape for any provider without a dedicated caller, so most new LLM APIs work by just adding a registry entry.

## Google (Gemini)
- Different request shape from the two above; if used heavily, add a dedicated caller to `call_llm.py`. Until then, treat as fallback-only.

## SEO data (DataForSEO / Ahrefs / Semrush)
- DataForSEO: basic auth (login+password env vars), task-based endpoints, pay-per-call — good default for a fractional practice with no fixed subscription.
- Ahrefs/Semrush: subscription APIs — prefer when the client already pays for one (record in client pack `stack.md`).

## Enrichment (Apollo / Clay / ZoomInfo)
- Apollo: simple REST, generous free tier — good default.
- Watch credit consumption on bulk enrichment; batch and dedupe before calling.
- LinkedIn-sourced data should flow through the ConnectSafely MCP + its skill rules instead of scraping.

## MCP connectors (HubSpot, ConnectSafely, Google Drive, Gmail)
- Not called from scripts — use the environment's connected MCP tools directly.
- In artifacts/web apps, MCP servers can be passed to the Anthropic API's `mcp_servers` parameter.
- If a needed connector isn't available in the current environment, say so rather than emulating it.

## Adding a new provider (checklist)
1. Add an entry under `providers:` in `config/registry.yaml` (kind, api_base, api_key_env, models).
2. If it's not OpenAI-shape or Anthropic, add a caller function in `scripts/call_llm.py`.
3. Point one or more capabilities at it (as primary or fallback).
4. Add a short section here with auth pattern + one quirk worth remembering.
5. Set the env var; run a smoke test: `python scripts/call_llm.py --capability <cap> --prompt "test"`.
