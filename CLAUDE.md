# CLAUDE.md — Big Slick (read me first, every session)

## What this is
Big Slick: an open-core marketing skills distribution for Claude ("Red Hat for Claude marketing skills"). Public repo = the OPEN edition. Reserved Components live in the private `bigslick-pro` repo. Owner: Frank Days. Full design: DESIGN-SPEC.md. Executable build: BUILD-BIGSLICK.md. Licensing map: LICENSING.md.

## Architecture (5 rules — never violate)
1. `upstream/` is READ-ONLY vendored open source, pinned in `upstream/VERSIONS`. Modify upstream skills only via `overlay/patches/<skill>/`.
2. `overlay/manifest.yaml` is the merge (include/exclude per upstream). `core/` wins every name collision at compose.
3. Client specifics live ONLY in `core/clients/<client>/` packs. Never put a company name in a skill file.
4. No skill names a model or API provider. Capabilities route via the `resource-hub` skill; providers in its `config/registry.yaml`; keys only in env vars.
5. v0.1 is curation-first: no new marketing-skill authoring. Growth = admit open-source skills that pass §4.13 of DESIGN-SPEC (license gate: MIT/Apache/BSD/CC0; reject GPL/AGPL/no-license). Infrastructure skills (e.g. bigslick-setup) are allowed.

## Build & release
- `pip3 install pyyaml && python3 scripts/compose.py` → `dist/skills/` + provenance + plugin manifest. Expect **125** skills in the public repo (104 upstream + 21 core).
- `bash scripts/test.sh` — release gate (structural + client-lifecycle tests). Must print ALL TESTS PASS.
- `bash scripts/package.sh` → `bigslick.plugin` (open edition; asserts 0 reserved skills). Pro plugin builds from `../bigslick-pro`.
- Client activation: `bash scripts/activate_client.sh <client>` (relative symlinks). Claude runs this; users never do.
- Quarterly: `bash scripts/update_upstreams.sh` → review add/removes → edit manifest → recompose → test → bump `overlay/plugin/plugin.json` version.

## Working conventions
- Every core skill: trigger-rich frontmatter description; reads `.agents/product-marketing.md` first; ends with the resource-hub routing line; produces a named deliverable.
- Execution finds what review misses: run any new/changed skill once against the Hansel AI sample client (`core/clients/hansel-ai`) before committing.
- Commit messages: imperative, one line, what + why. Never commit `dist/`, `.agents/`, or real client packs (gitignored; only `_template` and `hansel-ai` are public).
- Don't reformat or "improve" upstream or existing core skill content unasked.

## Git
- Public: github.com/frankdays/bigslick (this repo). Private: github.com/frankdays/bigslick-pro (Reserved Components).
- Push directly when asked; tag releases `v0.x`. Force-push only for the one-time history purge in split-pro.sh.
