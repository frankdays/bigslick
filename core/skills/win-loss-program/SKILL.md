---
name: win-loss-program
description: Design and run a win-loss analysis program — the systematic study of why deals are won and lost, from buyer interviews and CRM forensics. Use when the user mentions "win-loss", "why are we losing", "loss reasons", "deal autopsy", "competitive losses", "win rate dropped", or wants buyer-sourced truth feeding positioning, battlecards, and product. Produces the highest-signal input a marketing org has.
---
# Win-Loss Program
Read the active client pack. This program feeds `product-marketing` (positioning), `competitors`/`competitor-profiling` (battlecards), `pricing`, and the PMM persona — design the routing before the first interview.

## 1. Program design
- **Sample:** every closed deal is logged (CRM taxonomy below); target 8–12 buyer *interviews* per quarter, balanced won/lost, weighted toward competitive and ICP-fit deals. Below ~6/quarter you have anecdotes; say so rather than overclaiming.
- **Who interviews:** never the AE (buyers won't be honest) and ideally not anyone the buyer met during the sale. PMM or a third party. State the independence in the ask.
- **The ask:** within 2–4 weeks of decision, 25 minutes, explicitly "we're improving how we sell, not re-selling you"; a modest gift card is standard and acceptable. Expect 20–40% acceptance; losses accept more often than wins expect.

## 2. CRM loss-reason forensics (the always-on layer)
Fix the taxonomy first — "lost to competitor / price / no decision" tells nothing. Minimum viable taxonomy: lost-to-whom (named), lost-at-stage, primary reason (product gap [which], price/packaging, champion left, no urgency, trust/references, timing), + AE free-text. Enforce via required CRM fields (`crm-conventions`). Analyze quarterly: reason mix by segment, by competitor, by stage — stage patterns reveal whether marketing, product, or sales owns the fix.

## 3. Interview guide (30 min, recorded)
- Process: "Walk me through how this decision actually happened — who was involved, what did they care about?"
- Alternatives: "Who else did you look at seriously? What did they do better/worse?"
- The moment: "Was there a moment the decision tipped? What caused it?"
- Us, honestly: "What almost made you choose differently? What did our team get wrong/right?"
- Price: "Was price a real factor or the polite reason?" (ask directly — buyers respect it)
- Wrap: "What would you tell our CEO?"
Probe stories, not ratings. The verbatim quotes are the product.

## 4. Synthesis & routing (quarterly)
Deliverable: win-loss readout — reason mix with trend, competitor-by-competitor scorecard (why we win/lose vs. each, in buyer quotes), 3 systemic findings, and routed actions: messaging changes → `product-marketing`; battlecard updates → `competitor-profiling`; product gaps → product team with deal-$ attached; pricing signals → `pricing`. Protect candor: quotes circulate anonymized (role + segment, never name/company unless approved) — one buyer burned by an attributed quote ends the program's access. Present to sales leadership BEFORE publishing wide — they must recognize the deals in it, or they'll dismiss it.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
