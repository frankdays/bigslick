---
name: exec-linkedin-ghostwriting
description: Ghostwrite LinkedIn presence for executives — voice capture, post production, and the operating cadence. Use when the user mentions "ghostwrite", "CEO's LinkedIn", "founder brand", "executive content", "exec social", "write posts as/for [exec]", or building leadership visibility. Layers per-exec voice on top of the upstream linkedin-content skill (formats) and works with the linkedin-connectsafely-search skill (research/engagement).
---
# Executive LinkedIn Ghostwriting
Read the active client pack. Each exec gets a voice file: `clients/<company>/exec-voices/<name>.md` — no exec content ships without one.

## 1. Voice capture (one hour, once, then maintained)
Source material: 3–5 of their real posts/emails they like, a recorded 20-minute interview ("tell me about a strong opinion you hold about the industry that peers disagree with"), and 2–3 talks/podcasts if they exist. Extract into the voice file: sentence rhythm (short/long), vocabulary (words they use / would never use), stance profile (what they'll take heat for, what's off-limits), story inventory (their repeatable personal anecdotes), format preferences (lists? long-form? contrarian hooks?), and hard NOs. Test: draft 2 posts, have them mark every phrase "I'd never say this" — that markup is the real voice file.

## 2. Content engine
- **POV pillars:** 3 recurring themes per exec at the intersection of (what they genuinely believe) × (what the ICP cares about) × (what the company needs the market to think — from positioning). Product mentions ≤ 1 in 5 posts.
- **Sourcing:** mine their week — deal stories (anonymized), customer conversations, internal debates, hot takes on category news (`brand-monitor` feeds), conference reactions. The ghostwriter's job is extraction, not invention: a 10-minute weekly voice memo from the exec is the highest-yield input.
- **Formats:** per upstream `linkedin-content`/`thread-writer`; native text beats links; specificity beats platitudes ("we lost a $400k deal because…" outperforms "leadership lessons").
- **Comments are half the program:** 15 min/day engaging on target accounts' and peers' posts (surface candidates via `linkedin-connectsafely-search`, respecting its rules) — often outperforms posting for actual pipeline influence.

## 3. Operating cadence & guardrails
Program viability test, stated upfront: the exec commits ~30 min/week (voice memo + approval pass). If they can't or won't after a month, don't fake it — downgrade to a comments-and-reshares program or stop; invented thought leadership is detectable and worse than absence.
2–3 posts/exec/week sustained beats daily-for-a-month. Approval loop: batch weekly, exec approves/edits in one pass, 24h SLA or the slot rolls. Hard guardrails in every engagement: the exec has final word and knows everything published under their name; no material non-public information (revenue specifics, unannounced deals/products — route anything gray to legal); no manufactured personal stories — embellished authenticity reads as fake and eventually gets caught; competitor commentary punches at ideas, never at people.

## 4. Measurement
Not follower count. Track: comments/DMs from ICP-matched people (the actual output), inbound meetings citing the content (ask SDRs to log), engagement from named target accounts (`abm-builder` list overlap), and qualitative: does sales hear "I've seen your CEO's posts"? Quarterly, prune pillars that draw engagement only from peers/vendors rather than buyers.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
