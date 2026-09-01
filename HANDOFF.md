# HANDOFF.md — state as of 2026-09-01, for the first Claude Code session

## Where things stand
- Public repo `frankdays/bigslick`: 13 commits, upstreams pinned (Corey @3df87f9, OpenClaudia @2856765, Anthropic @5267cf7), Option A licensing committed, Hansel AI sample client present, 29 core skills (incl. `oss-devrel-gtm`, built locally — note: exceeds the v0.1 no-authoring rule; keep, but log it in DESIGN-SPEC §4.3).
- Reserved Components (9 skills: company-onboarding, staff-meeting, persona-* ×7) are STILL in the public repo → must move to private `bigslick-pro`.
- Built and tested artifacts (from the chat session, in the owner's downloads): `bigslick.plugin` (open, 125 skills), `bigslick-pro.plugin` (9), `scripts/package.sh`, `bigslick-setup` skill, `split-pro.sh`, `REQUIREMENTS.md`, `bigslick-skill-requirements.csv`, `DESIGN-SPEC.md` v0.1, `CLAUDE.md`.

## Do these, in order
1. Add to repo root: `CLAUDE.md`, `HANDOFF.md`, `REQUIREMENTS.md`, `bigslick-skill-requirements.csv`, updated `DESIGN-SPEC.md`. Add `scripts/package.sh`. Add `core/skills/bigslick-setup/` (from bigslick-setup-skill.zip). Commit: "Add repo context, requirements inventory, setup skill, packaging".
2. Run `PURGE_HISTORY=1 bash split-pro.sh frankdays` (from repo root; script in the owner's downloads). Confirms: private repo created/pushed, 9 reserved skills removed from public repo + history, LICENSING.md updated. Verify `python3 scripts/compose.py` reports 125.
3. Run `bash scripts/test.sh` → ALL TESTS PASS. Run `bash scripts/package.sh` → bigslick.plugin. Commit + tag `v0.1`.
4. Verify the public install path from a clean shell: `claude plugin marketplace add https://github.com/frankdays/bigslick && claude plugin install bigslick@bigslick`.
5. Update DESIGN-SPEC.md: inventory to 125 open + 9 pro (private), note oss-devrel-gtm, mark punch-list item 9 done.

## Known gaps / decisions pending (owner)
- Pilot client not yet chosen (Phase 1 item 3) — highest-value open item.
- Curation round (Phase 2): vet candidate repos per DESIGN-SPEC §4.13 to fill market-sizing and partner-channel gaps.
- Trigger-eval set for the 8 watch-flag pairs not yet built (§4.15).
- Attorney review of the Reserved Component License before launch.
- Landing page + directory submissions after step 4 passes.
