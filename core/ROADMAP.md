# Core Layer Roadmap
Updated: 2026-07-25. Planning doc only — no skills built from this list yet.

## In core today (4)
resource-hub | reddit-b2b-tech-strategy | wikipedia-b2b-citation-strategy | linkedin-connectsafely-search

## Build list — BUILT as MVP 2026-07-25, revised after CMO review (details in skill files)
1. company-onboarding — keystone; tailors the whole system to a specific business. Four phases: (a) context intake → generates client pack (extend upstream `product-marketing` scaffold); (b) resource wiring → configures resource-hub routing + env/connection checklist from stack.md; (c) skill relevance mapping → writes skills-profile.md to client pack (library stays global; relevance is per-client data, never per-client recompose); (d) persona calibration → maps persona roster to client's real team. v1 = phases a–b; phases c–d land after function skills + personas exist. Naming note: 'company-onboarding' chosen to avoid colliding with upstream `onboarding` (user/product onboarding, Corey).
2. pipeline-math — revenue target → pipeline coverage → MQL/SQL volumes by channel → CAC/payback-constrained budget model
3. board-reporting — CEO/board translation layer: pipeline vs plan, efficiency trends, narrative, budget defense
4. field-marketing-events — trade shows, sponsored conferences, field events, owned events; ABSORBS webinars (do not build a separate webinar skill)
5. case-study-builder — interview banks, story structure, approvals, repurposing
6. review-site-strategy — G2/Capterra/TrustRadius: review generation, profile/grid positioning, AI-citation flow (completes citation triad with reddit + wikipedia)
7. ai-answer-monitoring — queries AI engines on client category, tracks share of voice vs competitors, attributes citations to sources; produces recurring AI Visibility Report (orchestrates skills 6 + reddit + wikipedia + upstream geo-* tools via resource-hub)

Sequence rationale: 1 → 2 → 3 chain (context pack feeds pipeline model feeds board narrative); 4–5 are calendar/proof deliverables; 6–7 complete the GEO product.

## Personas layer (decided 2026-07-25 — not built)
Design rule: personas are CHARTERS, not curricula — ~80 lines: lane, altitude, decision rights, quality bar, owned deliverables, and which function skills they orchestrate. NO domain knowledge inside (that lives in function skills). Build AFTER the function skills they reference exist (~position 5–6 in sequence).

Roster — BUILT as MVP 2026-07-25 (6 charters + 1 antagonist + 1 orchestrator):
- cmo — integrator; owns tradeoffs, budget allocation, board narrative
- product-marketing-director — positioning, messaging, launches, win-loss, competitive, enablement
- vp-growth — demand gen, pipeline, paid; primary owner of pipeline-math outputs
- field-marketing-director — events calendar + budget lane; orchestrates field-marketing-events
- comms-manager — brand risk, PR/AR (absorbs PR/analyst specialist lane)
- content-seo-director — organic engine incl. GEO differentiator; argues organic vs paid
- vp-sales (antagonist) — adversarial reviewer only; attacks plans from revenue side (operationalizes sales-alignment gap)
- staff-meeting (orchestrator) — convenes personas against a doc/plan; role-specific, client-pack-aware upgrade of upstream marketing-council

## Extend-when-touched — BUILT as core skills 2026-07-25 (revised after CMO review)
abm-builder | pr-analyst-relations | exec-linkedin-ghostwriting | hubspot-conventions (→ client pack) | attribution-diagnostics | win-loss-program | sales-marketing-alignment

## Backlog — BUILT 2026-07-25 (martech-stack-auditor, hiring-interview-kit)
martech-stack-auditor (client pack stack.md covers most value; build on first client request)
hiring-interview-kit (build if/when full-time CMO scenario is live)

## Cut (decided 2026-07-25)
- webinar-playbook — merged into field-marketing-events
- campaign-retro/meeting-facilitator — low leverage; no skill needed
- budget-vendor-management — removed from list earlier
- 1:1/performance-review kit — removed from list earlier

## Operating notes
- All new skills: read active client pack (.agents/product-marketing.md convention); route external calls via resource-hub; never reference providers directly.
- Watch trigger overlap: reddit-marketing & linkedin-content (openclaudia) vs core skills — patch descriptions in overlay/patches/ if they misfire.

## Identified gap (from Hansel AI sample test, 2026-07-25)
- oss-devrel-gtm — open-source GTM is a distinct motion (community->cloud->enterprise, DevRel program, stars/installs as funnel, monetization packaging) not covered by any of the 128 skills; community-marketing (upstream) is adjacent but not OSS-specific. Build when an OSS client is real.
