# Licensing Map — Big Slick (fully open source as of v0.2)

Big Slick redistributes only skills whose upstream licence permits redistribution.

**MIT (root `LICENSE`)**: compose/installer/scripts, docs, everything in `overlay/`, and the
four first-party infrastructure skills in `core/skills/` (`company-onboarding`, `client-onboarding`, `resource-hub`, `client-context`).

**Vendored upstreams** — original licences preserved in each `upstream/<name>/LICENSE` and
in `licenses/`:

| Upstream | Repo | Licence |
|---|---|---|
| marketingskills | coreyhaines31/marketingskills | MIT |
| openclaudia | OpenClaudia/openclaudia-skills | MIT |
| anthropic-marketing | anthropics/knowledge-work-plugins | Apache-2.0 |
| goose-skills | gooseworks-ai/goose-skills | MIT |
| kostja-marketing | kostja94/marketing-skills | MIT |
| rampstack | rampstackco/claude-skills | MIT |
| wondel | wondelai/skills | MIT |
| claude-seo | AgriciDaniel/claude-seo | MIT |
| geo-seo | zubair-trabzada/geo-seo-claude | MIT |

Per-skill source, licence, and external dependencies: **`INVENTORY.md`**. The same source and
licence are appended to every shipped skill's description at build time (`Source: <owner/repo>
(<licence>).`), so the credit travels with the skill; `scripts/test.sh` T8 fails if one is missing.

**Every installable plugin carries its own notices.** A marketplace install fetches only one
plugin directory, never the repo's `licenses/`, so the build writes into `plugin/` and each
`bundles/<name>/`:

- `LICENSES/` — the full licence text, with copyright notice, of every source that plugin
  redistributes;
- `NOTICE.md` — which skills come from which source, and a statement of Big Slick's
  modifications (the appended Source line, and any local patch, marked †), as Apache-2.0 §4(b)
  requires for modified files.

`scripts/test.sh` T9 fails if any plugin root is missing either.

**Removed in v0.2**: the Reserved Component License and the 29 source-available skills it
covered (`staff-meeting`, the `persona-*` charters, `pipeline-math`, `board-reporting` and the
rest). Nothing in the distribution is source-available-only any more, and `scripts/test.sh` T4
fails the build if a per-skill `LICENSE.md` reappears under `core/skills/`.

`company-onboarding` and `resource-hub` were later restored to `core/skills/` **relicensed MIT**
by the copyright holder, because no vendored upstream covers writing a client context pack or
holding provider configuration. `client-onboarding` (the multi-client layer) and `client-context`
(loads the active pack, or says there is none) were added later on the same MIT terms. All four
are open source on the same terms as the rest of the repo.

`core/clients/` holds per-company context packs. Your own packs are your data — writing one
does not put it under any licence here. The only pack that ships in the distribution,
`_template`, is MIT under the root `LICENSE` like everything else.

A `core/clients/LICENSE.md` carrying the old Reserved Component terms survived the v0.2
cleanup as an untracked local file. It never reached GitHub or any release asset (it was
gitignored), but it nominally covered the sample packs that shipped at the time, so it has been
removed. `scripts/test.sh` T4 now fails on any file named LICENSE/LICENCE/COPYING anywhere
outside `upstream/` and `licenses/` that grants source-available terms — the earlier check
only looked at `core/skills/`, which is why this one went unnoticed.

PRs welcome on all paths.
