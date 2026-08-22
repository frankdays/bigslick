# Big Slick
**The open-source marketing distribution for Claude — 133 skills: 104 curated from open source, 29 proprietary.**

*The best starting hand a marketer can be dealt.*

Marketing work you'd normally hire for — pipeline models, board decks, ABM programs, win-loss, PR, AI-search visibility — as skills Claude can actually run. Built for running marketing across several B2B software companies at once, and it converts cleanly to a single company if you take a full-time seat.

---

## Install

Download the latest `.dmg` from [Releases](https://github.com/frankdays/bigslick/releases), drag the `bigslick` folder to Documents, then right-click `INSTALL.command` → Open. (A `.zip` is there too.)

**[Full install guide →](INSTALL.md)** — five minutes, no technical background needed, including the macOS security prompt that trips most people up.

Then open Claude in the folder and say:

```
Onboard my company
```

It interviews you about your business and writes everything down. Every other skill reads what it wrote, so you never edit a file by hand.

---

## How it works (60 seconds)

**Skills are engines; companies are data.** No skill contains anything about your business. Each company gets its own context pack — positioning, ICP, competitors, voice, tooling, funnel numbers — and every skill reads whichever pack is active. Switching companies is one command, and nothing about the skills changes.

That's what makes it work across a client roster: one library, many companies, no copy-pasted variants drifting apart.

A fictional sample company (`hansel-ai`) ships with it, so you can try everything before entering your own numbers.

*Building on Big Slick or curious how the library is assembled? See [MAINTAINERS.md](MAINTAINERS.md) for the layer model, the compose step, and how upstream skills are vendored and patched.*

---

## Building from source

Most people should use the download above. Build from source only if you're changing skills or the manifest.

```bash
pip install pyyaml
python scripts/compose.py                      # -> dist/skills/ (133 skills) + plugin manifest
bash install.sh                                # registers the plugin, verifies, loads the sample company
```

After changing any skill, re-run `compose.py` and reinstall so the plugin picks up the change. `bash scripts/test.sh` runs the same release gate CI runs. `bash scripts/package_release.sh` builds the end-user zip.

Big Slick runs in **Claude Code**, where it has full capability — API keys, MCP connections, file access.

### Claude.ai / desktop: experimental

Claude.ai takes one zip per skill, caps each description at **200 characters**, and has no filesystem, so repo-relative client-pack paths never resolve. `scripts/package_for_claude_ai.py` reconciles all three, bundling the active client pack into each zip and rewriting paths to match.

**Status: 7 of 133 skills are ready for this path.** The description *is* the trigger logic, and 125 skills run past the cap (median ~450 chars). Auto-compression drops the "Use when the user says…" phrases that make a skill fire, so a compressed skill installs but may never trigger. Hand-written short descriptions live in `overlay/claude-ai/descriptions.yaml`; write an entry before relying on a skill here.

This path is deliberately excluded from the end-user download — shipping skills that install but don't fire is worse than not shipping them. Generate on demand:

```bash
python scripts/package_for_claude_ai.py --all --check      # report, write nothing
python scripts/package_for_claude_ai.py persona-cmo staff-meeting
```

Then in Claude.ai: enable code execution in **Settings → Capabilities**, upload at **Customize → Skills**. Bundled packs are a snapshot — regenerate after changing a client pack.

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

**Plus 104 upstream skills** — SEO, content, copywriting, paid channels, CRO, pricing, launch, analytics tooling, and more. Browse `dist/skills/`; provenance per skill in `dist/PROVENANCE.txt`.

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

Upstream distributions are MIT / source-available — original license files are preserved in each `upstream/` folder and in `licenses/`. Keep them intact. Everything in `core/` is proprietary to you; MIT imposes no copyleft on it. Merge decisions and provenance: `MANIFEST.md` and `dist/PROVENANCE.txt`. Build history and remaining roadmap: `core/ROADMAP.md`.
