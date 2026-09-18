# HANDOFF.md — state as of 2026-09-17

## Where things stand
- Public repo `frankdays/bigslick`, **v0.2.9** (`overlay/plugin/plugin.json` is the source;
  `compose.py` propagates it to `plugin/` and all 10 bundles). Tags `v0.1` through
  `v0.2.7` are published.
- **249 skills** — 245 vendored from 7 MIT/Apache-2.0 upstreams, plus 4 first-party MIT
  infrastructure skills in `core/skills/`: `company-onboarding` (one business),
  `client-onboarding` (a book of clients), `resource-hub` (provider config), and
  `client-context` (loads the active pack, or says out loud that there is none).
  Big Slick is fully open source; there is no proprietary layer and no private repo.
- **Lean core + bundles.** The core plugin (`plugin/`) ships 32 skills (~5k always-on tokens); the other
  217 live in 10 opt-in bundles — `seo` 43, `strategy` 34, `ai-search` 24, `gtm` 20,
  `ops` 19, `research` 19, `lifecycle` 18, `content` 17, `social` 14, `paid` 9. Shipping all
  249 cost ~28k tokens every session; skill descriptions are trigger logic and cannot be
  trimmed, so the only lever is shipping fewer by default.
- **Every plugin has its own directory.** `plugin/` (the core) and `bundles/<name>/` are
  committed, each a `.claude-plugin/plugin.json` + `skills/` pair, and `marketplace.json`
  points at `./plugin` and `./bundles/<name>`, so
  `claude plugin marketplace add https://github.com/frankdays/bigslick` works.
  **Changed in 0.2.9.** The core used to be published at the repo root (`"source": "."`),
  which made it the one entry that packaged the entire repository — `upstream/`, `bundles/`
  and all, ~25MB and 2,243 files — instead of its own 32 skills. It was also the only entry
  that never showed up in the desktop app's plugin browser, while all ten bundles listed
  fine. T7 now fails if a root `skills/` or root `.claude-plugin/plugin.json` reappears.
- The 29 removed proprietary core skills are recoverable at commit **4373503**.
  `bigslick-pro` was never created; the split was abandoned, not deferred.
- Release gate passes (`bash scripts/test.sh` → ALL TESTS PASS: T1–T7 plus F1).
  `scripts/package_release.sh` builds the download and aborts if any client pack other
  than `_template` is staged.
- **No sample client ships.** `hansel-ai` was removed 2026-09-15 (`e132b6a`); the last
  references to it in docs and installer copy went with `5d4aa1b`. `core/clients/_template`
  is the structure, not a runnable pack. Skills have nothing to work from until the user
  onboards.

## Open items
1. **Publish v0.2.8.** Tag it, run `scripts/package_release.sh` and `scripts/package_dmg.sh`,
   and attach the artifacts. The newest GitHub release asset is still well behind the repo.
   `v0.1` stays where it is — don't move a published tag.
2. **Pilot client not yet chosen** — still the highest-value open business item. Two real
   packs exist locally (`qmenta`, `unleash`), both gitignored.
3. **Trigger-eval set never built.** At 249 skills, collisions are unmeasured. `onboarding`
   (post-signup), `company-onboarding` (one business) and `client-onboarding` (several) are
   three semantically adjacent names with nothing but their descriptions separating them.
4. **`resource-hub` covers first-party skills only.** The 245 vendored skills name their own
   providers; `INVENTORY.md` records each one's env vars. So "configure your keys in one
   place" is not literally true across the whole library.
5. Landing page + directory submissions, once v0.2.8 is published.

## Things that don't exist (referenced in older notes — stop looking for them)
`DESIGN-SPEC.md`, `REQUIREMENTS.md`, `bigslick-skill-requirements.csv`, `scripts/package.sh`,
`split-pro.sh`, `core/skills/bigslick-setup/`, `core/clients/hansel-ai/`. None are on disk or
on any branch. `scripts/package_release.sh` is the working packager; `BUILD-BIGSLICK.md` and
`INVENTORY.md` carry the design and inventory content.

## Gotchas
- System Python is PEP 668 externally-managed: `pip3 install pyyaml` fails. Use the venv —
  `python3 -m venv .venv && .venv/bin/pip install pyyaml`, then put `.venv/bin` on PATH.
  `scripts/test.sh` aborts with "pip install pyyaml first" if you forget.
- **Recompose and commit `plugin/` + `bundles/` after any skill or version change**, or T7
  fails. The version lives in `overlay/plugin/plugin.json`; editing the generated
  `.claude-plugin/plugin.json` by hand gets overwritten.
- Regenerate `INVENTORY.md` (`scripts/gen_inventory.py`) after any manifest change or T5 fails.
- **Company context is working-directory dependent.** 25 skills read
  `.agents/product-marketing.md` and 17 read `.claude/product-marketing.md`, both relative to
  cwd — which resolves nowhere in the desktop app. `scripts/make_context_plugin.py <client>`
  packages a pack as a `company-context` skill and is the only route that reaches everywhere.
  Keep it in the onboarding flow.
- **Check what is actually active before client work.** As of 2026-09-17,
  `~/.claude/product-marketing.md` was the empty `_template` — i.e. no client active. The 245
  upstream skills fail silently in that state, handing back generic advice with no signal it
  is untailored. `client-context` in the core plugin exists to say so out loud; the upstream
  skills cannot be patched to do the same without 245 merge costs.
- **A locally-installed plugin does not follow your commits.** The marketplace source is the
  directory `/Users/frank/bigslick`, but the installed copy is a pinned snapshot under
  `~/.claude/plugins/cache/`. Run `claude plugin marketplace update bigslick && claude plugin
  update bigslick@bigslick` after a release, or you are testing an old build of your own work.
- Real client packs under `core/clients/` are gitignored and must never be committed; only
  `_template` is public. Beware the `.gitignore` inline-comment trap — a trailing `# comment`
  becomes part of the pattern and silently breaks a re-include.
