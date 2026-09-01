# Licensing Map — Big Slick (fully open source as of v0.2)

Big Slick redistributes only skills whose upstream licence permits redistribution.

**MIT (root `LICENSE`)**: compose/installer/scripts, docs, and everything in `overlay/`.

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

**Removed in v0.2**: the Reserved Component License and the `core/skills/` layer it covered
(`company-onboarding`, `staff-meeting`, the `persona-*` charters, `resource-hub`, and the rest
of the 29 proprietary skills). Nothing in the distribution is source-available-only any more.

`core/clients/` holds per-company context packs. These are your own data, not part of the
distributed skill library, and are not covered by the licences above.

PRs welcome on all paths.
