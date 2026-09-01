# Big Slick — Marketing Distribution

Marketing skills for Claude, curated from open-source upstreams and shipped as a
lean core plus opt-in bundles.

Installing `bigslick` gives you **31 broadly-useful skills** — planning, ICP,
copywriting, landing pages, SEO audits, ads, CRO, pricing, attribution, reporting.
Add a specialty only when you need it:

```
claude plugin install bigslick-seo@bigslick
claude plugin install bigslick-paid@bigslick
```

Bundles: `seo`, `ai-search`, `paid`, `content`, `social`, `gtm`, `lifecycle`,
`strategy`, `research`, `ops` — 209 skills in total across all of them.

This split is deliberate. Every skill's description loads into every session, so
the full library costs ~28k tokens of context before you ask for anything. The
lean core costs ~5k. An uninstalled bundle costs nothing.

## Composition

| Layer | Skills | Licence |
|---|---|---|
| coreyhaines31/marketingskills | 49 | MIT |
| OpenClaudia/openclaudia-skills | 52 | MIT |
| anthropics/knowledge-work-plugins | 3 | Apache-2.0 |
| gooseworks-ai/goose-skills | 34 | MIT |
| kostja94/marketing-skills | 19 | MIT |
| rampstackco/claude-skills | 27 | MIT |
| wondelai/skills | 23 | MIT |
| first-party infrastructure | 2 | MIT |

Every skill's origin is recorded in `PROVENANCE.txt`; per-skill source, licence and
external dependencies are in `INVENTORY.md`.

## The core idea

**Skills are engines; companies are data.** No skill contains company specifics.
Each company gets a context pack, you activate one at a time, and every skill
reads that pack. Switching companies is one command.

## Try it

- `"Build a marketing plan for Hansel AI"` — sample company is pre-loaded
- `"Run this past the marketing council"` — debates it through named marketing frameworks
- `"Onboard my company"` — interviews you and generates a real context pack

## Licensing

Fully open source, with nothing source-available or proprietary. 207 skills are
vendored from MIT- or Apache-2.0-licensed upstreams; the 2 first-party
infrastructure skills (`company-onboarding`, `resource-hub`) are MIT under the
repository's root LICENSE. Upstream licence texts ship in `licenses/`. See
`LICENSING.md`.
