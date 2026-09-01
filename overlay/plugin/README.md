# Big Slick — Marketing Distribution

133 marketing skills for Claude: pipeline models, board reporting, ABM, field
marketing, win-loss, case studies, PR/AR, and an AI-visibility (GEO) system —
plus a marketing leadership persona layer and swappable per-company context packs.

## Composition

| Layer | Skills | License |
|---|---|---|
| Core (proprietary) | 29 | MIT, except the Reserved Components listed below |
| coreyhaines31/marketingskills | 49 | upstream, preserved |
| OpenClaudia/openclaudia-skills | 52 | upstream, preserved |
| anthropics/knowledge-work-plugins | 3 | upstream, preserved |

Every skill's origin is recorded in `PROVENANCE.txt`.

## The core idea

**Skills are engines; companies are data.** No skill contains company specifics.
Each company gets a context pack, you activate one at a time, and every skill
reads that pack. Switching companies is one command.

## Try it

- `"Build the pipeline model for Hansel AI's year"` — sample company is pre-loaded
- `"Run this past the marketing council"` — debates it through named marketing frameworks
- `"Onboard <your company>"` — generates a real context pack

## Licensing

Fully open source. Every skill is vendored from an MIT- or Apache-2.0-licensed
upstream and is redistributable; per-skill source and licence are listed in
`INVENTORY.md`. Upstream licence texts ship in `licenses/`. See `LICENSING.md`.
