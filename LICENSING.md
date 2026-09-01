# Licensing Map — Big Slick (fully open source as of v0.2)

Big Slick redistributes only skills whose upstream licence permits redistribution.

**MIT (root `LICENSE`)**: compose/installer/scripts, docs, everything in `overlay/`, and the
two first-party infrastructure skills in `core/skills/` (`company-onboarding`, `resource-hub`).

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

Per-skill source, licence, and external dependencies: **`INVENTORY.md`**.

**Removed in v0.2**: the Reserved Component License and the 29 source-available skills it
covered (`staff-meeting`, the `persona-*` charters, `pipeline-math`, `board-reporting` and the
rest). Nothing in the distribution is source-available-only any more, and `scripts/test.sh` T4
fails the build if a per-skill `LICENSE.md` reappears under `core/skills/`.

`company-onboarding` and `resource-hub` were later restored to `core/skills/` **relicensed MIT**
by the copyright holder, because no vendored upstream covers writing a client context pack or
holding provider configuration. They are open source on the same terms as the rest of the repo.

`core/clients/` holds per-company context packs. These are your own data, not part of the
distributed skill library, and are not covered by the licences above.

PRs welcome on all paths.
