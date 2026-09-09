# Personal Meeting Notetaker — Fork Plan

Fork [anarlog](https://github.com/fastrepl/anarlog) and add the one feature it's missing:
a calendar-driven alert that starts recording.

**Scope:** one user, one Mac, personal use.
**Status:** planning. No code written.
**Date:** 2026-09-09.

> Standalone project. This file is parked in this repo for convenience only — it has no
> dependency on anything here and should move to its own repository when work starts.

---

## 1. Why this is now a small project

Building from scratch was five to seven weekends, nearly all of the risk concentrated in
Core Audio process taps: three setup parameters that fail silently returning `noErr`, a
real-time thread you can't allocate on, and an Apple-unconfirmed bug where a healthy tap
starts delivering all-zero buffers indistinguishable from real silence.

**Forking deletes that entire problem.** anarlog already solved audio capture, and its
maintainers own those bugs. What's left is one feature, in a codebase that's already
running.

anarlog is a serious project, not a weekend demo: **9,300+ stars, 9,300+ commits, 754
forks**, actively maintained by fastrepl. MIT licensed for the community app.

---

## 2. What anarlog already gives you

Essentially the whole product:

| | |
|---|---|
| Local audio capture | No bot joins the call — the thing you actually wanted |
| On-device transcription | Apple Speech on Mac; or Deepgram / Soniox / AssemblyAI with your own key |
| AI summarisation | Bring your own key. Claude supported; OpenAI-compatible endpoints and local models too |
| Templates | Already built |
| Notes, folders, chat, exports | Already built |
| Local SQLite + markdown export | Your data on your disk |
| Local recordings and audio player | |
| Manual speaker labelling | |
| CLI + local MCP server | Read-only: list meetings, search, read transcripts. Claude Code can query your meeting history directly |
| macOS, Windows, Linux | Apple Silicon supported |

It also has typed notes during meetings. You said you don't need those — ignore the
notepad; nothing forces you to use it.

**Free tier is local-only and $0.** The paid tiers ($15/mo Pro) buy cloud transcription,
hosted AI, and encrypted sync across devices — none of which you want. Running the
open-source build with your own Claude key keeps everything local at API cost only.

---

## 3. What's missing — the gap you're building

**Calendar integration, pre-meeting notifications, and auto-join are all absent.** Neither
the repo nor the product site documents any of them. That is precisely the feature you
asked for, and it is the whole scope of this project.

**And it can't be bolted on from outside.** The CLI and MCP server are documented as
**read-only** — they list meetings, search by title, and read transcripts in bounded
chunks, but expose no way to *start* a recording. So an external trigger script isn't an
option, and the feature has to go inside the app.

> **Cheap check worth doing first:** confirm that read-only claim against the actual repo.
> Look for a start-recording Tauri command, a URL scheme, or an AppleScript hook. If any
> exists, you can trigger anarlog from a tiny external script and **skip forking entirely**
> — a few hours of work instead of a weekend or two. This is the single highest-value thing
> to check before writing code.

---

## 4. The stack you're inheriting

Not Swift. Plan accordingly:

- **Tauri v2** desktop shell
- **Rust** backend
- **React + TypeScript** frontend
- **SQLite** local storage
- Toolchain: Node.js 22+, pnpm 11.1.1, Rust 1.94.0

```
apps/desktop     → the Tauri app (where your work goes)
apps/web         → website and account portal
apps/api         → optional hosted services — ignore
apps/cli         → CLI and MCP server
plugins/         → Tauri capability plugins (the pattern to follow)
crates/          → Rust libraries
packages/        → TypeScript utilities
enterprise/      → commercial components — see §8
```

The existing `plugins/` directory matters: it means there's an established in-repo pattern
for adding OS-level capabilities, which is exactly what the calendar feature needs.

---

## 5. Day one — build, configure, and actually use it

Before building anything, spend a day using it. This is not a formality; it may end the
project happily.

1. **Build from source.** Node 22+, pnpm 11.1.1, Rust 1.94.0, Tauri v2 prerequisites, then
   `pnpm install --frozen-lockfile` and `pnpm exec turbo dev:desktop`. Budget half a day —
   monorepo toolchain wrangling always takes longer than the README suggests.
2. **Point it at Claude** with your own API key rather than the default managed OpenRouter
   route. Direct is cheaper and keeps the loop between you and Anthropic.
3. **Set transcription to on-device.** Apple Speech on Mac, no network, no cost.
4. **Write one template** for whichever meeting type you have most of.
5. **Use it for three real meetings.** Judge the actual output.

Then decide honestly: is the gap between this and what you want *actually* the calendar
alert, or is it something about the summaries? If it's the summaries, that's template work
(§7) and costs no engineering at all. Only build §6 if the missing trigger is what's really
bothering you.

---

## 6. The feature: calendar alert → record

Four pieces. The design work here carries over unchanged from the from-scratch plan; only
the implementation language changes.

### 6.1 Reading the calendar

**EventKit**, which reads whatever calendars are already configured in Calendar.app —
Google, Exchange, iCloud — behind one local permission prompt, with no OAuth in your app at
all. This is why the feature is small: no Google Cloud project, no consent screen, no
verification.

In Tauri this means a **plugin with a Swift or Objective-C bridge**, following the existing
`plugins/` pattern. The Rust side exposes a command; the native side talks to EventKit.
This is the most unfamiliar part of the build if you haven't bridged Rust to a macOS
framework before.

Known limitation: EventKit reflects Calendar.app's sync state, so an event created in
Google seconds ago can take minutes to appear. Irrelevant for scheduled meetings.

### 6.2 Deciding which meetings get an alert

This filtering is what makes the feature trustworthy rather than annoying. Fire an alert
twice for a birthday calendar and you'll dismiss every alert reflexively, at which point
the feature is worse than nothing. Skip:

- All-day events
- Events you declined (check your own participant status in the attendee list)
- Events with no other attendees — usually blocks and reminders, not meetings
- Calendars you didn't opt in, via a per-calendar allowlist
- Duplicates: the same meeting on both a personal and a work calendar, deduped on title +
  start time

### 6.3 The alert

Fire at **T-1 minute** (configurable). Tauri's notification plugin covers the basic case;
**notification action buttons may need native work** — check what Tauri v2 exposes before
designing around them. If actions turn out to be awkward, a click-to-focus notification
plus a prominent Record button in the app is a perfectly acceptable v1 and much less work.

| Action | Behaviour |
|---|---|
| **Record** | Start the recording |
| **Skip** | Dismiss, don't re-alert |

Re-scan and re-register whenever the calendar changes — meetings get moved and cancelled
constantly, and an alert for a meeting that no longer exists is exactly what trains you to
ignore alerts. Handle recurring events per occurrence, not per series.

### 6.4 Optional: auto-join

Only worth building if the click to open Zoom genuinely annoys you. It carries the longest
tail of anything here, because every invite formats its join link differently.

**No structured field exists for this.** `EKVirtualConferenceProvider` is for apps that
*offer* conference rooms to Calendar, not for reading a third-party Zoom link off someone
else's invite. So parse, in priority order: `event.url` (Google often puts the Meet link
here), then `location` (where Zoom invites often land), then `notes` (where everything else
ends up).

Launching: rewrite Zoom web URLs to the app deep link —
`https://<sub>.zoom.us/j/<id>?pwd=<pwd>` → `zoommtg://zoom.us/join?confno=<id>&pwd=<pwd>` —
so the client opens directly instead of bouncing through a browser page. The scheme does
nothing if Zoom isn't installed, so check first and fall back to the https URL. Meet, Teams
and Webex just take the https URL.

**Recommendation: skip this in v1.** It's the single largest source of grind in the whole
project, and it saves one click.

---

## 7. Templates — where the quality actually is

anarlog already has a template system, so this costs zero engineering. It is still where
the app becomes good or stays generic.

Since you're not typing notes, nothing tells the summariser what mattered to *you* — only
what was said. A generic "summarise this meeting" prompt produces the same bland output as
every other tool. What makes it yours is a template that knows a discovery call needs budget
signals, objections and next steps, while a 1:1 needs commitments and blockers.

Write one genuinely good template rather than four mediocre ones, and iterate it against
real meetings. This is the highest-value non-code work available, and it's available on day
one.

**Cost:** a one-hour meeting is ~13K input tokens and ~1.5K out. On `claude-opus-5` ($5/$25
per MTok) that's about **$0.10 per meeting**, roughly **$2/month** at 20 meeting-hours.

---

## 8. Fork hygiene

A 9,300-commit repo under active development will move underneath you.

- **Keep the diff tiny and isolated.** A new plugin plus minimal wiring rebases cleanly. Edits
  scattered across `apps/desktop` do not.
- **Rebase periodically** rather than diverging. You want their capture bug fixes — that's
  the entire reason you forked.
- **Consider upstreaming.** Calendar alerts are an obvious gap that other users will want. A
  merged PR means no fork to maintain at all, which is strictly better than the best
  possible fork. Worth opening an issue to gauge interest before building, in case a
  maintainer is already on it or wants a particular design.
- **Licensing:** the community app is MIT; `enterprise/` is commercial and source-visible
  under different terms. For personal use this is a non-issue — just don't build or
  redistribute enterprise components, and read `LICENSING.md` before publishing a fork.

---

## 9. Prerequisites

1. **Anthropic API key with billing.** A Claude subscription isn't an inference budget for a
   separate app. ~$2/month.
2. **Node 22+, pnpm 11.1.1, Rust 1.94.0, Tauri v2 prerequisites.**
3. **Rust and TypeScript**, plus a little Swift/Objective-C for the EventKit bridge. This is
   the real skill question — if you don't write Rust, the calendar plugin is a learning
   project rather than a weekend. It's a small, well-bounded piece of Rust, but it is Rust.
4. **No Apple Developer Program needed.** anarlog's build handles its own signing for local
   use, and you're not distributing.

**One non-technical prerequisite:** recording consent. Two-party-consent jurisdictions apply
to individuals recording their own calls. An alert that starts recording on one click makes
it easier than ever to record without thinking about it, which makes the habit of disclosing
more important, not less.

---

## 10. Build order and time

**Stage 0 — check for an existing trigger (an hour).** Search the repo for a start-recording
command, URL scheme, or AppleScript hook (§3). If one exists, the whole project becomes a
small external script and you skip everything below.

**Stage 1 — build, configure, use (one day).** §5. Half a day of toolchain, then real
meetings. **A legitimate stopping point** — many people would end here happily.

**Stage 2 — templates (ongoing, no code).** §7. Do this before writing any Rust; it may
close the gap on its own.

**Stage 3 — the calendar plugin (one weekend).** EventKit bridge, event scanning, filtering
logic. The unfamiliar part is bridging Rust to a macOS framework, not the calendar logic.

**Stage 4 — the alert and wiring (one weekend).** Notification, scheduling and
re-registration, wire the action to the existing record command.

**Stage 5 — auto-join (optional, don't).** §6.4.

| Path | Time |
|---|---|
| Configured and in daily use | **1 day** |
| Plus the calendar alert | **+1–2 weekends** |
| From scratch in Swift, for comparison | 3–7 weekends, with an unbounded capture tail |

---

## 11. Risks

1. **The toolchain fights you.** A Rust + pnpm + Tauri monorepo on a specific Rust version
   is the most likely place to lose a day. It's frustration, not risk — it always resolves.
2. **Rust is the real gate.** If you don't write it, stages 3–4 are a learning project. That
   changes the estimate more than anything technical here. Worth being honest with yourself
   before starting, because stage 1 delivers value without touching Rust at all.
3. **Upstream moves under you.** Mitigated by a small, isolated diff and periodic rebasing.
4. **Tauri notification actions may be limited.** Check before designing around buttons;
   have the click-to-focus fallback ready.
5. **Generic summaries.** The predictable failure mode of a no-notes design. The fix is
   template work, not code — and unlike everything else here, it's available on day one.
6. **You don't actually need the feature.** After a week of real use, the missing alert may
   turn out to matter less than you expect. Stage 1 before stage 3 exists precisely to find
   that out cheaply.

---

## 12. Open decisions

1. **Fork, or upstream a PR?** Upstreaming is strictly better if the maintainers want the
   feature. Ask first.
2. **How early should the alert fire?** T-1 keeps it actionable. T-5 drifts toward being
   another calendar reminder you ignore.
3. **Auto-join at all?** It's the longest tail in the project for one saved click.
4. **On-device or cloud transcription?** Apple Speech is free and local. A cloud provider
   with your own key is more accurate on poor audio. Start local; switch only if accuracy
   actually bothers you.
