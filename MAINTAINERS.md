# BigSlick — Maintainer Guide
**Architecture, build system, and customization. End-user setup lives in README.md.**
Built for running marketing across multiple B2B software clients with one library, and designed to convert cleanly into a single-company system if you take a full-time CMO seat.

---

## What this is (60 seconds)

Three layers, strictly separated:

| Layer | What lives there | Rule |
|---|---|---|
| `upstream/` | 7 vendored open-source skill distributions (Corey Haines, OpenClaudia, Anthropic, goose-skills, kostja-marketing, rampstack, wondel), versions pinned in `upstream/VERSIONS` | **Never edit.** Refresh with a script. |
| `overlay/` | `manifest.yaml` — which upstream skills are enabled/excluded — plus `patches/` for modifications to upstream skills | The merge, as config. Edit here, not in upstream. |
| `core/` | Client context packs, the roadmap, and `skills/` — 2 first-party MIT infrastructure skills (`company-onboarding`, `resource-hub`). The source-available proprietary layer was removed in v0.2 and is not coming back. | Packs are your data; `core/skills/` is MIT and ships. |

`scripts/compose.py` builds the deployable library into `dist/skills/` from those three layers. `dist/PROVENANCE.txt` records where every skill came from.

**The other key idea: skills are engines, clients are data.** No skill contains client specifics. Each client gets a context pack in `core/clients/<name>/`; you activate one client at a time and every skill reads that pack. Switching clients is one command.

---

## Quick start

```bash
# 1. Build the library
pip install pyyaml
python scripts/compose.py                      # -> dist/skills/ (209 skills) + plugin manifest

# 2. Install as a Claude Code plugin (dist/ is a valid plugin after compose)
claude plugin marketplace add /path/to/bigslick   # or the repo's git URL once pushed
claude plugin install bigslick
#    (Cowork: Settings -> Plugins -> install from the same marketplace path)
#    Alternative, no plugin system: point Claude Code at dist/skills/ as a skills directory.

# 3. Onboard your first client (creates the context pack)
#    In Claude (with the plugin installed): "Onboard <company>"
#    -> runs company-onboarding -> writes core/clients/<company>/
#    (Or copy core/clients/_template yourself and fill it in.)

# 4. Activate the client
./scripts/activate_client.sh <company>

# 5. Work
#    "Build a marketing plan for <company>"     -> marketing-plan
#    "Define our ICP"                           -> icp-builder
#    "Run this plan past the marketing council" -> marketing-council
#    After changing any skill: re-run compose + reinstall so the plugin picks up changes.
```

Use in **Claude Code** (full capability — API keys, MCPs, file access) or upload individual skills to **Claude.ai / Cowork** (built-in tools and connected MCPs substitute for raw APIs). Note the Claude.ai path is experimental — see the last section.

---

## The skills, by job

207 of the 209 are vendored from upstreams (the other 2 are first-party infrastructure);
the full table with source, licence and external
dependencies is **[INVENTORY.md](INVENTORY.md)**. Orientation by area:

**Strategy & positioning** — `good-strategy-bad-strategy`, `blue-ocean-strategy`,
`crossing-the-chasm`, `obviously-awesome`, `jobs-to-be-done`, `pmf`, `marketing-plan`,
`growth-strategy`, `okr-design`, `traction-eos`

**Research & customer** — `icp-builder`, `icp-identification`, `buyer-persona-generator`,
`customer-discovery`, `mom-test`, `voice-of-customer-synthesizer`, `journey-mapping`,
`competitor-intel`, `battlecard-generator`

**SEO, content & AI search** — `seo-audit`, `keyword-research`, `content-strategy`,
`write-blog`, `pillar-content-architecture`, `programmatic-seo`, `schema`, plus the
GEO/AI-citation set: `geo`, `aeo`, `ai-seo`, `ai-citations-report`, `ai-traffic`,
`entity-seo`, `eeat-signals`, `grokipedia`

**Paid & channels** — `ads`, `google-ads`, `facebook-ads`, `linkedin-ads`, `reddit-ads`,
`ad-creative`, `video-ad-analysis`, `affiliate-marketing`, `influencer-marketing`

**GTM & pipeline** — `prospecting`, `outbound-prospecting-engine`, `cold-email`,
`predictable-revenue`, `pipeline-review`, `sales-enablement`, `revops`, `demand-gen`,
`performance-report`, `investor-call-prep`

**Lifecycle & retention** — `onboarding`, `churn-prevention`, `churn-risk-detector`,
`retention`, `improve-retention`, `paywalls`, `pricing`, `emails`, `email-sequence`

**Review & orchestration** — `marketing-council` convenes a simulated board of advisors
(Godin, Ogilvy, Dunford, Sutherland and others) against a document. It is the nearest
thing to the old `staff-meeting`, though it reviews from marketing-canon perspectives
rather than a company org chart.

## Everyday commands

| You want to… | Do this |
|---|---|
| Start a new client | Run `company-onboarding` in Claude, then `./scripts/activate_client.sh <name>` |
| Switch clients | `./scripts/activate_client.sh <other-name>` |
| See which client is active | `ls -l core/clients/_active` |
| Rebuild after any change | `python scripts/compose.py` |
| Pull upstream updates (quarterly) | `./scripts/update_upstreams.sh` → review reported adds/renames → adjust `overlay/manifest.yaml` → recompose |
| Modify an upstream skill | Copy the changed file into `overlay/patches/<skill-name>/` — never edit `upstream/` |
| Add your own skill | Marketing skills: don't — vendor an upstream clearing the ≥500-star + MIT/Apache-2.0 bar instead. Infrastructure skills: add to `core/skills/` under the root MIT licence, never a per-skill LICENSE.md (T4 fails on one) |
| Disable an upstream skill | Add it to the `exclude:` list in `overlay/manifest.yaml` → recompose |
| Retire a client | Archive `core/clients/<name>/` — skills are untouched |

---

## House rules (what keeps this maintainable)

1. **Client specifics live in client packs only.** If you're typing a company name into a skill file, stop.
2. **`upstream/` is read-only.** Changes go through `overlay/patches/`.
3. **Everything shipped is redistributable.** Upstreams are MIT/Apache-2.0; `core/skills/` is MIT under the root LICENSE. `test.sh` T4 fails on a per-skill LICENSE.md in `core/skills/` — that is how source-available terms would creep back.
4. **The quant skills trust `metrics-baseline.md`.** If a client won't agree definitions and share actuals, the models degrade — that's a client conversation, not a config problem.
5. **Quarterly maintenance (~1 hr):** refresh upstreams, regenerate INVENTORY.md, re-check any benchmark tables (reference numbers age), prune skills nobody used.

## Troubleshooting

- **A skill gives generic output** → no active client pack, or the pack is thin. Check `core/clients/_active` and fill in the gaps in that folder's markdown files.
- **Wrong skill triggers** (e.g., upstream `reddit-marketing` instead of your strategy skill) → tighten either skill's frontmatter `description` via `overlay/patches/`, or exclude the upstream one in the manifest.
- **compose.py errors** → `pip install pyyaml`; check YAML indentation in `overlay/manifest.yaml`.
- **Skills can't find the client pack** → skills resolve `.agents/product-marketing.md` relative to the repo root — run Claude Code from the repo directory, and re-run `activate_client.sh` after moving/cloning the repo.
- **A provider call fails** → for first-party skills, `resource-hub` walks fallbacks and names the missing env var; set it or reassign the capability in `config/registry.yaml`. For vendored upstream skills, check that skill's `INVENTORY.md` row for the env var it expects.
- **In Claude.ai, external APIs unreachable** → expected; the sandbox only reaches the Anthropic API. Use connected MCPs there, or run the skill in Claude Code.
- **`pip install pyyaml` fails with "externally-managed-environment"** → PEP 668. Use a venv: `python3 -m venv .venv && .venv/bin/pip install pyyaml`.

## Licensing

Every upstream is MIT or Apache-2.0 and redistributable — original licence files are preserved in each `upstream/` folder and in `licenses/`. Keep them intact. Per-skill source, licence, and external dependencies live in `INVENTORY.md`; regenerate it with `python scripts/gen_inventory.py` after any manifest change. Merge decisions and provenance: `overlay/manifest.yaml` and `dist/PROVENANCE.txt`. Build history and remaining roadmap: `core/ROADMAP.md`.

## Claude.ai packaging — experimental, maintainer-only (decided 2026-08-22)

`scripts/package_for_claude_ai.py` works, but the path is ~3% complete: 7 of 209 skills have
hand-written short descriptions in `overlay/claude-ai/descriptions.yaml`, and 125 exceed
Claude.ai's 200-character description cap. Because the description *is* the trigger logic,
auto-compressed skills install but may never fire — a failure the user cannot see or diagnose.

Decision: keep the tooling, exclude the path from the end-user download, and document it as
experimental. Generated zips are build output; never commit them and never ship a stale set.
v0.1's asset shipped 131 zips built three weeks earlier, under the old brand, including skills
the manifest excludes.

To promote this to supported: write `descriptions.yaml` entries for the skills that matter,
starting with the leadership set, and re-check with `--all --check` until the fallback list is
empty for that set.
