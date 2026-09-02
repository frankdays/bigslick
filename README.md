# Big Slick
**The open-source marketing distribution for Claude — 247 skills, every one of them redistributable.**

*The best starting hand a marketer can be dealt.*

Marketing work you'd normally hire for — pipeline reviews, exec reporting, prospecting, win-loss, PR, AI-search visibility — as skills Claude can actually run. Built for running marketing across several B2B software companies at once, and it converts cleanly to a single company if you take a full-time seat.

**v0.2 is fully open source.** The proprietary layer is gone. Every skill is vendored from an MIT- or Apache-2.0-licensed upstream with a documented source, licence, and dependency list — see [INVENTORY.md](INVENTORY.md).

---

## Install

If you already use Claude Code, two lines:

```bash
claude plugin marketplace add https://github.com/frankdays/bigslick
claude plugin install bigslick@bigslick
```

Prefer a download? Grab the latest `.dmg` from [Releases](https://github.com/frankdays/bigslick/releases), drag the `bigslick` folder to Documents, then right-click `INSTALL.command` → Open. (A `.zip` is there too.) That route also sets up the sample company for you.

**[Full install guide →](INSTALL.md)** — five minutes, no technical background needed, including the macOS security prompt that trips most people up.

Then open Claude in the folder and say:

```
Set up a client pack for my company
```

It walks you through your business and fills in a client pack. Every other skill reads that pack, so you configure once.

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
python scripts/compose.py                      # -> skills/ (247) + .claude-plugin/plugin.json
bash install.sh                                # registers the plugin, verifies, loads the sample company
```

After changing any skill, re-run `compose.py` and reinstall so the plugin picks up the change. `bash scripts/test.sh` runs the same release gate CI runs. `bash scripts/package_release.sh` builds the end-user zip.

Big Slick runs in **Claude Code**, where it has full capability — API keys, MCP connections, file access.

### Claude.ai / desktop: experimental

Claude.ai takes one zip per skill, caps each description at **200 characters**, and has no filesystem, so repo-relative client-pack paths never resolve. `scripts/package_for_claude_ai.py` reconciles all three, bundling the active client pack into each zip and rewriting paths to match.

**Status: 31 of 247 skills are ready for this path** — the full lean core, hand-written. The description *is* the trigger logic, and 125 skills run past the cap (median ~450 chars). Auto-compression drops the "Use when the user says…" phrases that make a skill fire, so a compressed skill installs but may never trigger. Hand-written short descriptions live in `overlay/claude-ai/descriptions.yaml`; write an entry before relying on a skill here.

This path is deliberately excluded from the end-user download — shipping skills that install but don't fire is worse than not shipping them. Generate on demand:

```bash
python scripts/package_for_claude_ai.py --all --check      # report, write nothing
python scripts/package_for_claude_ai.py pipeline-review stakeholder-communication
```

Then in Claude.ai: enable code execution in **Settings → Capabilities**, upload at **Customize → Skills**. Bundled packs are a snapshot — regenerate after changing a client pack.

---

## The skills, by job

Every skill below is open source. Source repo, licence, and external dependencies for
all 247 are listed in **[INVENTORY.md](INVENTORY.md)**.

**Start of an engagement**
- `brand-discovery`, `icp-identification`, `brand-voice-extractor`, `company-intel` — the intake set. Run these, then write the answers into `core/clients/<name>/` (copy `core/clients/_template/` to start) and `./scripts/activate_client.sh <name>`.

**Strategy and positioning** *(the framework layer)*
- `good-strategy-bad-strategy`, `obviously-awesome`, `crossing-the-chasm`, `blue-ocean-strategy`, `jobs-to-be-done`, `storybrand-messaging`, `one-page-marketing`, `monetizing-innovation`

**The CFO-facing quant layer**
- `pipeline-review` — pipeline coverage, stage health, what actually closes
- `predictable-revenue` — outbound engine design, role splits, ramp math
- `lean-analytics` — the metric that matters at this stage, and why the others are noise
- `stakeholder-communication`, `okr-design`, `after-action-report` — reporting upward and closing the loop
- `experimentation-analytics`, `analytics-strategy`, `experiment-design` — test design and readouts
- `revops` — lifecycle stages, scoring, naming, hygiene rules

**Programs**
- `targeted-prospecting`, `outbound-prospecting-engine`, `tam-builder`, `champion-tracker` — account and pipeline programs
- `event-prospecting-pipeline`, `conference-speaker-scraper` — field marketing
- `customer-story-builder`, `customer-stories`, `testimonials` — proof
- `voice-of-customer-synthesizer`, `customer-discovery`, `mom-test`, `churn-risk-detector` — win-loss and retention research
- `press-coverage`, `media-kit`, `public-relations` — PR and analyst relations
- `linkedin-post-research`, `linkedin-outreach`, `linkedin-message-writer` — executive and social presence

**The GEO / AI-citation system**
- `geo`, `aeo`, `ai-traffic`, `entity-seo`, `eeat-signals`, `grokipedia` — the citation surfaces AI engines lean on
- `ai-seo`, `ai-citations-report`, `ai-answer-monitoring`'s replacement measurement path via `seo-traffic-diagnosis`

**Community and open source**
- `open-source`, `github-repo-signals`, `cold-start-problem`, `reddit-post-finder`, `comment-mining`, `social-listening`

**Leadership & ops**
- `high-output-management`, `team-onboarding-playbook`, `roadmap-planning`, `vendor-evaluation`, `tech-stack-teardown`, `integration-orchestrator`

**Brand**
- `brand-archetype-system`, `brand-style-guide`, `creative-brief`, `brand-review`

**Plus the full upstream library** — SEO, content, copywriting, paid channels, CRO, pricing, launch, analytics tooling, and more. Browse `skills/`; provenance per skill in `dist/PROVENANCE.txt` and `INVENTORY.md`.

---

## Everyday commands

| You want to… | Do this |
|---|---|
| Start a new client | `cp -r core/clients/_template core/clients/<name>`, fill it in (use `brand-discovery` / `icp-identification` to do the interviewing), then `./scripts/activate_client.sh <name>` |
| Switch clients | `./scripts/activate_client.sh <other-name>` |
| See which client is active | `ls -l core/clients/_active` |
| Rebuild after any change | `python scripts/compose.py` |
| Pull upstream updates (quarterly) | `./scripts/update_upstreams.sh` → review reported adds/renames → adjust `overlay/manifest.yaml` → recompose |
| Modify an upstream skill | Copy the changed file into `overlay/patches/<skill-name>/` — never edit `upstream/` |
| Add your own skill | New folder + `SKILL.md` under a directory you add to `overlay/manifest.yaml` → recompose. Follow the house pattern: read the client pack, end with a named deliverable |
| Disable an upstream skill | Add it to the `exclude:` list in `overlay/manifest.yaml` → recompose |
| Retire a client | Archive `core/clients/<name>/` — skills are untouched |

---

## House rules (what keeps this maintainable)

1. **Client specifics live in client packs only.** If you're typing a company name into a skill file, stop.
2. **`upstream/` is read-only.** Changes go through `overlay/patches/`.
3. **Every skill is redistributable.** Nothing enters the manifest without a permissive upstream licence and an `INVENTORY.md` row. The bar for a new upstream is ≥500 GitHub stars and an MIT/Apache-2.0 licence.
4. **The quant skills trust `metrics-baseline.md`.** If a client won't agree definitions and share actuals, the models degrade — that's a client conversation, not a config problem.
5. **Quarterly maintenance (~1 hr):** refresh upstreams, re-check benchmark tables where reference numbers age, regenerate `INVENTORY.md`, prune skills nobody used.

## Troubleshooting

- **A skill gives generic output** → no active client pack, or the pack is thin. Check `core/clients/_active` and fill the gaps in that pack.
- **Wrong skill triggers** (e.g., `reddit-marketing` instead of `reddit-post-finder`) → tighten either skill's frontmatter `description` via `overlay/patches/`, or exclude one in the manifest.
- **compose.py errors** → `pip install pyyaml`; check YAML indentation in `overlay/manifest.yaml`.
- **Skills can't find the client pack** → skills resolve `.agents/product-marketing.md` relative to the repo root — run Claude Code from the repo directory, and re-run `activate_client.sh` after moving/cloning the repo.
- **In Claude.ai, external APIs unreachable** → expected; the sandbox only reaches the Anthropic API. Resource-hub routes to built-in tools/MCPs there; full registry works in Claude Code.

## Licensing

Every upstream is MIT or Apache-2.0 and redistributable. Original licence files are preserved in each `upstream/` folder and in `licenses/` — keep them intact. Per-skill source, licence, and external dependencies: **[INVENTORY.md](INVENTORY.md)**. Merge decisions and provenance: `overlay/manifest.yaml` and `dist/PROVENANCE.txt`.

Client packs under `core/clients/` are your own data, not part of the distributed skill library.
