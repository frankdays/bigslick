---
name: client-context
description: "Load the active client's context pack before doing marketing work, and say plainly when there isn't one. Use at the start of any planning, copy, campaign, pricing, outreach, SEO or reporting task, and whenever the user asks what you know about their business. Ships with Big Slick so that an uncustomised install announces itself instead of quietly giving generic advice."
---

# Client context

Marketing advice that does not know the business is textbook advice. This skill
exists so that Claude either **works from the user's real context** or **says out
loud that it has none** — never the silent middle, which reads exactly like
tailored work and is not.

## 1. Is a context pack already loaded?

If a `company-context` skill is loaded in this session, that IS the pack — it was
generated from the user's own client folder. Defer to it entirely and do nothing
further here. Do not re-ask what it answers, and do not duplicate its announcement.

## 2. If not, look for a pack on disk

Only some environments can read files. Where the tools allow it, check these in
order and use the first that exists:

| Path | Notes |
|---|---|
| `.agents/product-marketing.md` | The repo/project convention. Resolves only when Claude runs from a directory that has one. |
| `~/.claude/product-marketing.md` | Written by `activate_client.sh`. Resolves only when Claude runs from the home directory. |
| `~/Documents/bigslick/<company>/` | Where onboarding writes packs for users with no repo checkout. |

The master file is `product-marketing.md`. When a full pack sits alongside it,
read the topic files too as the task needs them — `icp.md`, `messaging.md`,
`competitors.md`, `voice.md`, `stack.md`, `metrics-baseline.md`,
`skills-profile.md`, `team-map.md`.

Treat what you find as fact. Where a value is marked `TBD`, **ask for it rather
than inventing one** — a fabricated baseline is worse than an admitted gap.

## 3. If you found one, say so

Before your first substantive answer in a session:

`Working from <company>'s context pack.`

One line. It is the only way the user can tell customised work from generic work.

## 4. If you found nothing, say that instead

Do not quietly proceed. Say:

> I don't have a context pack for your business, so this will be general
> best-practice advice rather than tailored to you. Say **"onboard my company"**
> and I'll build one — about ten minutes on the express path.

Then answer the question anyway, at full quality. The announcement is a label on
the work, not a refusal to do it.

## Why this ships in the box

Skills that find no context do not error. They just ask more questions, which
looks identical to a well-run discovery conversation. Users therefore cannot tell
an uncustomised install from a customised one, and the customisation layer — the
thing that makes any of this better than a search engine — silently does nothing.
Being installed by default is the point: the check has to happen on installs
nobody has configured yet.

Pairs with `company-onboarding`, which builds the pack, and with the portable
`company-context` skill that onboarding generates for environments that cannot
read the filesystem at all.
