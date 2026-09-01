# CLAUDE.md — Big Slick (read me first, every session)

## What this is
Big Slick: a fully open-source marketing skills distribution for Claude ("Red Hat for Claude marketing skills"). Every shipped skill is vendored from an MIT- or Apache-2.0-licensed upstream — as of v0.2 there is no proprietary layer and no private repo. Owner: Frank Days. Executable build: BUILD-BIGSLICK.md. Per-skill source/licence/deps: INVENTORY.md. Licensing map: LICENSING.md. Maintainer guide: MAINTAINERS.md.

## Architecture (5 rules — never violate)
1. `upstream/` is READ-ONLY vendored open source, pinned in `upstream/VERSIONS` (7 upstreams). Modify upstream skills only via `overlay/patches/<skill>/`.
2. `overlay/manifest.yaml` is the merge (include/exclude per upstream). `compose.py` still supports an optional `core:` key, but v0.2 removed that layer — don't reintroduce it without a licensing decision.
3. Client specifics live ONLY in `core/clients/<client>/` packs. Never put a company name in a skill file. Client packs are the user's own data, not part of the distributed library.
4. Every composed skill must resolve to a vendored upstream with a redistributable licence. `test.sh` T4 fails the build if anything provenances to `core`.
5. Curation-first: no new marketing-skill authoring. Growth = admit open-source skills that clear the bar in INVENTORY.md — **≥500 GitHub stars and MIT or Apache-2.0** (reject GPL/AGPL/no-license). Record star count at vendoring time.

## Build & release
- System Python is PEP 668 externally-managed, so `pip3 install pyyaml` fails. Use a venv: `python3 -m venv .venv && .venv/bin/pip install pyyaml`, then run scripts with `.venv/bin` on PATH.
- `python3 scripts/compose.py` → `dist/skills/` + provenance + plugin manifest. Expect **207** skills, all upstream.
- `python3 scripts/gen_inventory.py` after any manifest change — `test.sh` T5 fails if a composed skill is missing from INVENTORY.md.
- `bash scripts/test.sh` — release gate (T1 counts, T2 frontmatter, T3 exclusions, T4 provenance, T5 inventory, T6 manifests, F1 client lifecycle). Must print ALL TESTS PASS.
- `bash scripts/package_release.sh` → `bigslick-<version>.zip`, the end-user download (dist/ prebuilt, installer, marketplace manifest, client packs). `scripts/package_dmg.sh` wraps it for macOS.
- Client activation: `bash scripts/activate_client.sh <client>` (relative symlinks). New packs start as `cp -r core/clients/_template core/clients/<name>`.
- Quarterly: `bash scripts/update_upstreams.sh` → review add/removes → edit manifest → recompose → gen_inventory → test → bump `overlay/plugin/plugin.json` version.

## Working conventions
- `dist/` is gitignored and absent from GitHub, so `marketplace.json`'s `./dist` source only resolves locally. The public install path is the **release asset** (`.zip`/`.dmg`) + `install.sh`, per INSTALL.md — not `claude plugin marketplace add <github url>`, which cannot work.
- Execution finds what review misses: run any changed skill once against the Hansel AI sample client (`core/clients/hansel-ai`) before committing.
- Commit messages: imperative, one line, what + why. Never commit `dist/`, `.agents/`, build zips, or real client packs (gitignored; only `_template` and `hansel-ai` are public).
- Don't reformat or "improve" upstream skill content unasked. Patches go in `overlay/patches/`, and every patch is a merge-conflict cost at the next upstream refresh.

## Git
- Public: github.com/frankdays/bigslick (this repo). No private repo — `bigslick-pro` was never created.
- Push directly when asked; tag releases `v0.x`. `v0.1` is published and points at `1a20221`; don't move a published tag.
- The 29 removed core skills (personas, staff-meeting, company-onboarding, resource-hub, pipeline-math, and the rest) are recoverable at **4373503**, the commit before the v0.2 merge.

## Known gaps
- Nothing creates client packs any more — `company-onboarding` was removed in v0.2 and no upstream skill replaces it. Packs are a manual copy-and-fill from `_template`.
- `resource-hub` is gone, so there is no capability-routing layer. No shipped skill references it (verified 0). Skills that need an external API name it directly or rely on connected MCPs.
- `DESIGN-SPEC.md` is referenced in older docs but has never existed in this repo.
