# CLAUDE.md — Big Slick (read me first, every session)

## What this is
Big Slick: a fully open-source marketing skills distribution for Claude ("Red Hat for Claude marketing skills"). 207 marketing skills are vendored from MIT/Apache-2.0 upstreams; 2 first-party infrastructure skills live in `core/skills/` under the repo's MIT licence. v0.2 removed the source-available proprietary layer and there is no private repo. Owner: Frank Days. Executable build: BUILD-BIGSLICK.md. Per-skill source/licence/deps: INVENTORY.md. Licensing map: LICENSING.md. Maintainer guide: MAINTAINERS.md.

## Architecture (5 rules — never violate)
1. `upstream/` is READ-ONLY vendored open source, pinned in `upstream/VERSIONS` (7 upstreams). Modify upstream skills only via `overlay/patches/<skill>/`.
2. `overlay/manifest.yaml` is the merge (include/exclude per upstream). The `core:` key adds `core/skills/`, which wins every name collision. `core/` is for MIT **infrastructure** only — `company-onboarding` (writes client packs) and `resource-hub` (provider config). Marketing content belongs upstream.
3. Client specifics live ONLY in `core/clients/<client>/` packs. Never put a company name in a skill file. Client packs are the user's own data, not part of the distributed library.
4. Everything shipped must be redistributable. `test.sh` T4 fails on unrecognised provenance **and** on any per-skill `LICENSE.md` in `core/skills/` — that file is how the removed Reserved Component License would creep back.
5. Curation-first: no new marketing-skill authoring. Growth = admit open-source skills that clear the bar in INVENTORY.md — **≥500 GitHub stars and MIT or Apache-2.0** (reject GPL/AGPL/no-license). Record star count at vendoring time.

## Build & release
- System Python is PEP 668 externally-managed, so `pip3 install pyyaml` fails. Use a venv: `python3 -m venv .venv && .venv/bin/pip install pyyaml`, then run scripts with `.venv/bin` on PATH.
- `python3 scripts/compose.py` → `dist/skills/` (build output, gitignored) **and** `skills/` + `.claude-plugin/plugin.json` at the repo root (committed — this is the plugin itself). Expect **209** skills (207 upstream + 2 core).
- `python3 scripts/gen_inventory.py` after any manifest change — `test.sh` T5 fails if a composed skill is missing from INVENTORY.md.
- `bash scripts/test.sh` — release gate (T1 counts, T2 frontmatter, T3 exclusions, T4 provenance, T5 inventory, T6 manifests, F1 client lifecycle). Must print ALL TESTS PASS.
- `bash scripts/package_release.sh` → `bigslick-<version>.zip`, the end-user download (dist/ prebuilt, installer, marketplace manifest, client packs). `scripts/package_dmg.sh` wraps it for macOS.
- Client activation: `bash scripts/activate_client.sh <client>` (relative symlinks). New packs start as `cp -r core/clients/_template core/clients/<name>`.
- Quarterly: `bash scripts/update_upstreams.sh` → review add/removes → edit manifest → recompose → gen_inventory → test → bump `overlay/plugin/plugin.json` version.

## Working conventions
- The repo root IS the plugin: `marketplace.json` says `"source": "."`, and `skills/` + `.claude-plugin/plugin.json` are committed, so `claude plugin marketplace add https://github.com/frankdays/bigslick` works. **Recompose and commit `skills/` whenever a skill changes** — T7 fails the gate if it drifts or goes untracked. The release `.zip`/`.dmg` ships the identical layout.
- Execution finds what review misses: run any changed skill once against the Hansel AI sample client (`core/clients/hansel-ai`) before committing.
- Commit messages: imperative, one line, what + why. Never commit `dist/`, `.agents/`, build zips, or real client packs (gitignored; only `_template` and `hansel-ai` are public). Do commit `skills/` — it is the published plugin, not a build artifact.
- Don't reformat or "improve" upstream skill content unasked. Patches go in `overlay/patches/`, and every patch is a merge-conflict cost at the next upstream refresh.

## Git
- Public: github.com/frankdays/bigslick (this repo). No private repo — `bigslick-pro` was never created.
- Push directly when asked; tag releases `v0.x`. `v0.1` is published and points at `1a20221`; don't move a published tag.
- The 29 removed core skills (personas, staff-meeting, company-onboarding, resource-hub, pipeline-math, and the rest) are recoverable at **4373503**, the commit before the v0.2 merge.

## Known gaps
- Nothing creates client packs any more — `company-onboarding` was removed in v0.2 and no upstream skill replaces it. Packs are a manual copy-and-fill from `_template`.
- `resource-hub` is gone, so there is no capability-routing layer. No shipped skill references it (verified 0). Skills that need an external API name it directly or rely on connected MCPs.
- `DESIGN-SPEC.md` is referenced in older docs but has never existed in this repo.
