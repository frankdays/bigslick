# HANDOFF.md — state as of 2026-09-01

## Where things stand
- Public repo `frankdays/bigslick`, v0.2 merged and pushed: **209 skills** — 207 vendored from
  7 MIT/Apache-2.0 upstreams, plus 2 first-party MIT infrastructure skills in `core/skills/`
  (`company-onboarding`, `resource-hub`), restored after the merge and relicensed MIT. The proprietary `core/skills/` layer (29 skills — personas,
  `staff-meeting`, `company-onboarding`, `resource-hub`, `pipeline-math` and the rest) was
  removed. Big Slick is no longer open-core; it is fully open source.
- The removed 29 are recoverable at commit **4373503**. `bigslick-pro` was never created and
  the split was deliberately abandoned, not deferred.
- Release gate passes (`bash scripts/test.sh` → ALL TESTS PASS). `bigslick-0.2.0.zip` builds
  from `scripts/package_release.sh` (209 skills, 3.3M), which now aborts if any client pack
  other than `_template`/`hansel-ai` is staged.
- Docs reconciled to the v0.2 reality: CLAUDE.md, MAINTAINERS.md, INSTALL.md, install.sh.

## Open items
1. **Tag and publish v0.2.** `plugin.json` says `0.2.0`, but the latest GitHub release is v0.1
   with a stale 133-skill asset. Needs: tag `v0.2` at the merge commit, publish
   `bigslick-0.2.0.zip`, and run `scripts/package_dmg.sh` for the `.dmg`. `v0.1` stays where
   it is — don't move a published tag.
2. **`resource-hub` covers first-party skills only.** The 207 vendored skills name their own
   providers; `INVENTORY.md` records each one's env vars. Fine as-is, but it means "configure
   your keys in one place" is not literally true across the whole library.
3. Pilot client not yet chosen — still the highest-value open business item.
4. Trigger-eval set for ambiguous skill pairs never built. At 207 skills, trigger collisions
   are more likely than they were at 133.
5. Landing page + directory submissions, once v0.2 is published.

## Things that don't exist (referenced in older notes — stop looking for them)
`DESIGN-SPEC.md`, `REQUIREMENTS.md`, `bigslick-skill-requirements.csv`, `scripts/package.sh`,
`split-pro.sh`, `core/skills/bigslick-setup/`. None were ever committed to this repo on any
branch, and none are on disk. `scripts/package_release.sh` is the working packager;
`BUILD-BIGSLICK.md` and `INVENTORY.md` carry the design and inventory content.

## Gotchas
- System Python is PEP 668 externally-managed: `pip3 install pyyaml` fails. Use a venv.
- `dist/` is gitignored and absent from GitHub, so `claude plugin marketplace add <github url>`
  cannot install this repo. The public path is the release asset + `install.sh` (see INSTALL.md).
- Regenerate `INVENTORY.md` (`scripts/gen_inventory.py`) after any manifest change or `test.sh`
  T5 fails.
