# BigSlick — Maintainer Guide
**Architecture, build system, and customization. End-user setup lives in README.md.**
Built for running marketing across multiple B2B software clients with one library, and designed to convert cleanly into a single-company system if you take a full-time CMO seat.

---

## What this is (60 seconds)

Three layers, strictly separated:

| Layer | What lives there | Rule |
|---|---|---|
| `upstream/` | 3 vendored open-source skill distributions (Corey Haines, OpenClaudia, Anthropic), versions pinned in `upstream/VERSIONS` | **Never edit.** Refresh with a script. |
| `overlay/` | `manifest.yaml` — which upstream skills are enabled/excluded — plus `patches/` for modifications to upstream skills | The merge, as config. Edit here, not in upstream. |
| `core/` | Client context packs and the roadmap. The proprietary skills layer was removed in v0.2; `compose.py` treats the `core:` manifest key as optional. | Your data, not distributed skills. |

`scripts/compose.py` builds the deployable library into `dist/skills/` from those three layers. `dist/PROVENANCE.txt` records where every skill came from.

**The other key idea: skills are engines, clients are data.** No skill contains client specifics. Each client gets a context pack in `core/clients/<name>/`; you activate one client at a time and every skill reads that pack. Switching clients is one command.

---

## Quick start

```bash
# 1. Build the library
pip install pyyaml
python scripts/compose.py                      # -> dist/skills/ (207 skills) + plugin manifest

# 2. Install as a Claude Code plugin (dist/ is a valid plugin after compose)
claude plugin marketplace add /path/to/bigslick   # or the repo's git URL once pushed
claude plugin install bigslick
#    (Cowork: Settings -> Plugins -> install from the same marketplace path)
#    Alternative, no plugin system: point Claude Code at dist/skills/ as a skills directory.

# 3. Onboard your first client (creates the context pack)
#    In Claude (with the plugin installed): "Onboard <company>"
#    -> runs the company-onboarding skill -> writes core/clients/<company>/

# 4. Activate the client
./scripts/activate_client.sh <company>

# 5. Work
#    "Build the pipeline model for Q4"        -> pipeline-math
#    "Draft my board update"                  -> board-reporting
#    "Run this plan past the staff meeting"   -> staff-meeting (persona review)
#    After changing any skill: re-run compose + reinstall so the plugin picks up changes.
```

Use in **Claude Code** (full capability — API keys, MCPs, file access) or upload individual skills to **Claude.ai / Cowork** (built-in tools and connected MCPs substitute for raw APIs; the resource-hub skill handles the difference).

---

## The skills, by job

**Start of an engagement**
- `company-onboarding` — the keystone. Structured intake → full client pack (ICP, messaging, competitors, voice, stack, **metrics-baseline** — the funnel definitions and 4 quarters of actuals that the quantitative skills depend on). Run this first, always.

**The CFO-facing quant layer** *(deploy together — they share `metrics-baseline.md`)*
- `pipeline-math` — revenue target → pipeline/budget model, new-logo AND expansion, scenarios, channel allocation
- `board-reporting` — board/CEO narrative, forward view, CFO-attack prep
- `attribution-diagnostics` — three-lens attribution, funnel stall forensics
- `crm-conventions` — lifecycle stages, scoring, naming, hygiene rules
- `sales-marketing-alignment` — the definitions treaty, bilateral SLA, pipeline council

**Programs**
- `abm-builder`, `field-marketing-events`, `case-study-builder`, `win-loss-program`, `pr-analyst-relations`, `exec-linkedin-ghostwriting`

**The GEO / AI-citation system** *(the differentiator)*
- `reddit-b2b-tech-strategy`, `wikipedia-b2b-citation-strategy`, `review-site-strategy` — one skill per citation source AI engines lean on
- `ai-answer-monitoring` — the measurement layer; produces the monthly **AI Visibility Report** and routes gaps back to the three source skills

**Leadership & ops**
- `hiring-interview-kit`, `martech-stack-auditor`

**The personas** — 6 charters + 1 antagonist + 1 orchestrator
- `persona-cmo`, `persona-product-marketing-director`, `persona-vp-growth`, `persona-field-marketing-director`, `persona-comms-manager`, `persona-content-seo-director` — each defines a lane, decision rights, quality bar, and which function skills it orchestrates. Zero domain knowledge by design.
- `persona-vp-sales` — adversarial reviewer only; attacks plans from the revenue side
- `staff-meeting` — convenes personas against a document; produces a decision log. Ask for it before any plan ships.

**Infrastructure**
- `resource-hub` — all external LLM/API routing. Skills request *capabilities* (`research_synthesis`, `bulk_classification`…); `core/skills/resource-hub/config/registry.yaml` maps capabilities to providers. Swap models by editing that one file. Fill in the `SET_ME` model placeholders and set env vars before first use.

**Plus 100 upstream skills** — SEO, content, copywriting, paid channels, CRO, pricing, launch, analytics tooling, and more. Browse `dist/skills/`; provenance per skill in `dist/PROVENANCE.txt`.

---

## Everyday commands

| You want to… | Do this |
|---|---|
| Start a new client | Run `company-onboarding` in Claude, then `./scripts/activate_client.sh <name>` |
| Switch clients | `./scripts/activate_client.sh <other-name>` |
| See which client is active | `ls -l core/clients/_active` |
| Rebuild after any change | `python scripts/compose.py` |
| Pull upstream updates (quarterly) | `./scripts/update_upstreams.sh` → review reported adds/renames → adjust `overlay/manifest.yaml` → recompose |
| Modify an upstream skill | Copy the changed file into `overlay/patches/<skill-name>/` — never edit `upstream/` |
| Add your own skill | New folder + `SKILL.md` in `core/skills/` → recompose. Follow the house pattern: read the client pack, route APIs via resource-hub, end with a named deliverable |
| Disable an upstream skill | Add it to the `exclude:` list in `overlay/manifest.yaml` → recompose |
| Retire a client | Archive `core/clients/<name>/` — skills are untouched |

---

## House rules (what keeps this maintainable)

1. **Client specifics live in client packs only.** If you're typing a company name into a skill file, stop.
2. **`upstream/` is read-only.** Changes go through `overlay/patches/`.
3. **No skill names a model or API provider.** Capabilities via resource-hub; providers in `registry.yaml`.
4. **The quant skills trust `metrics-baseline.md`.** If a client won't agree definitions and share actuals, the models degrade — that's a client conversation, not a config problem.
5. **Quarterly maintenance (~1 hr):** refresh upstreams, re-check benchmark tables in `pipeline-math` / `pr-analyst-relations` (reference numbers age), review resource-hub costs/models, prune skills nobody used.

## Troubleshooting

- **A skill gives generic output** → no active client pack, or the pack is thin. Check `core/clients/_active`, re-run `company-onboarding` on the gaps.
- **Wrong skill triggers** (e.g., upstream `reddit-marketing` instead of your strategy skill) → tighten either skill's frontmatter `description` via `overlay/patches/`, or exclude the upstream one in the manifest.
- **compose.py errors** → `pip install pyyaml`; check YAML indentation in `overlay/manifest.yaml`.
- **Skills can't find the client pack** → skills resolve `.agents/product-marketing.md` relative to the repo root — run Claude Code from the repo directory, and re-run `activate_client.sh` after moving/cloning the repo.
- **A provider call fails** → resource-hub walks fallbacks and names the missing env var; set it or reassign the capability in `registry.yaml`.
- **In Claude.ai, external APIs unreachable** → expected; the sandbox only reaches the Anthropic API. Resource-hub routes to built-in tools/MCPs there; full registry works in Claude Code.

## Licensing

Every upstream is MIT or Apache-2.0 and redistributable — original licence files are preserved in each `upstream/` folder and in `licenses/`. Keep them intact. Per-skill source, licence, and external dependencies live in `INVENTORY.md`; regenerate it with `python scripts/gen_inventory.py` after any manifest change. Merge decisions and provenance: `overlay/manifest.yaml` and `dist/PROVENANCE.txt`. Build history and remaining roadmap: `core/ROADMAP.md`.

## Claude.ai packaging — experimental, maintainer-only (decided 2026-08-22)

`scripts/package_for_claude_ai.py` works, but the path is ~3% complete: 7 of 207 skills have
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
