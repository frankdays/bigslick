# Granola Clone — Personal macOS Desktop App

Status: planning document. No code written yet.
Scope: **personal use, single user, macOS (Apple Silicon), no distribution.**
Date: 2026-09-09.

> **Repo note:** this is a separate personal project, not Big Slick. None of Big Slick's
> architecture rules apply. If it proceeds, it wants its own repository.

---

## 0. The scope change, and why it matters

A commercial Granola clone is a 5–7 month project whose difficulty lives in distribution,
compliance, sync, and unit economics. A **personal** one deletes all four. What is left is
small enough to build in a few weekends, entirely in Swift, with no backend, no accounts,
no OAuth, and no per-meeting cost beyond about **$2/month** of Claude tokens.

Everything below is scoped to that. The single most important consequence: **you do not
need any of the commercial infrastructure** — no Recall.ai, no cloud ASR, no Google Cloud
project, no CASA assessment, no Stripe, no Sentry, no SOC 2. See §6 for the full list of
what got deleted.

---

## 1. First decision: fork, don't build

Before writing anything, evaluate **[anarlog](https://github.com/fastrepl/anarlog)** (MIT;
the project previously known as Hyprnote). It is already, almost exactly, the thing:

- Local-first, records and transcribes **on-device**, audio never leaves the machine
- Saves every meeting as **markdown on disk**
- **Bring-your-own LLM** — Anthropic is a supported provider, so it points at Claude directly
- macOS Apple Silicon, MIT licensed, forkable

For personal use this is very likely the correct answer. A weekend spent forking it,
pointing it at `claude-opus-5`, and writing your own enhancement templates gets you
further than a month of building capture from scratch — and you skip the single hardest
subsystem entirely (§3).

**Build from scratch only if** one of these is true: you want the build itself as the
exercise; anarlog's note model fights the way you actually take notes; or you want the
Big Slick context loop (§7) wired in deeply enough that grafting it on is worse than
owning the codebase.

The rest of this plan assumes you decided to build. Read §1 again first.

---

## 2. Architecture — one Swift app, one process

The commercial plan called for Electron plus a native capture sidecar plus a backend. At
personal scope, collapse all of it:

```
┌───────────────────────────────────────────────────────────┐
│  SwiftUI menu-bar app (macOS 14.4+, Apple Silicon)        │
│                                                            │
│  Capture   → Core Audio process tap  (system audio)        │
│              AVAudioEngine           (microphone)          │
│  ASR       → WhisperKit  (on-device, streaming, VAD)       │
│  Calendar  → EventKit    (no OAuth — see §5)               │
│  Store     → markdown files on disk + SQLite index         │
│  Enhance   → Anthropic API via URLSession (claude-opus-5)  │
└───────────────────────────────────────────────────────────┘
```

No Electron. No IPC. No sidecar. No server. No database server. No auth. Every dependency
is a Swift package or an OS framework, and the whole thing is one Xcode project.

**Storage: markdown files on disk, not a database.** For one user this is strictly better —
greppable, diffable, Git-versionable, readable by every other tool you own, and readable by
Claude Code directly. Add a SQLite index later only if search gets slow, which at personal
volume it will not for years.

---

## 3. Capture — still the hard part, but it is sample code now

This remains the one subsystem with real difficulty, but at personal scope you get to crib
rather than engineer.

**Use Core Audio process taps** (`AudioHardwareCreateProcessTap` + `CATapDescription`,
macOS 14.2+/14.4+). Not ScreenCaptureKit — taps are audio-only, can be scoped to specific
processes (tap Zoom, ignore Spotify), and avoid the Screen Recording permission and
menu-bar recording indicator.

**Start from [insidegui/AudioCap](https://github.com/insidegui/AudioCap)** — Guilherme
Rambo's sample code for exactly this, recording system audio on macOS 14.4+. It covers tap
creation, the aggregate-device dance, and the permission handling.
[AudioTee](https://stronglytyped.uk/articles/audiotee-capture-system-audio-output-macos)
is a second reference implementation as a CLI tool. Apple also documents the API directly.

**Capture mic and system audio as two separate streams.** This is the one design decision
to get right on day one. You get "me vs. them" attribution for free — perfect accuracy on
the most important speaker boundary, zero diarization cost, no ML involved. Retrofitting it
is a re-plumb.

**Edge cases you can safely ignore at personal scope** (and must not, commercially):
headphone switching mid-call, Bluetooth HFP sample-rate collapse, mute-state detection,
multiple simultaneous audio sessions, 3-hour meetings. Handle them if they bite you.
Personally, they mostly will not, and each one you skip is a week saved.

---

## 4. Transcription — local, free, and now a Swift package

**Use [WhisperKit](https://github.com/argmaxinc/argmax-oss-swift)** (MIT; as of v1.0.0 the
repo is `argmaxinc/argmax-oss-swift`, shipping WhisperKit + SpeakerKit + TTSKit). It is a
Swift Package with CoreML-compiled models running on the Neural Engine, with **real-time
streaming and voice activity detection built in**, and 27+ pre-converted model variants.

This is a near-perfect fit: it is the one dependency that turns "ship an ML pipeline inside
a desktop app" into `import WhisperKit`.

Cost: **$0**. Privacy: audio never leaves the Mac. Both matter more at personal scope than
commercially, because there is no accuracy-vs-margin tradeoff left to make — cloud ASR buys
you a few WER points for ~$0.58/hour, and you do not need them.

whisper.cpp is the alternative if you want Metal/GGML directly rather than CoreML. Either
works; WhisperKit is less assembly.

**One thing to get right:** Whisper hallucinates during silence — it will confidently
transcribe nothing into plausible sentences. Gate segments on VAD before they reach the
model. WhisperKit ships VAD, so this is configuration rather than code, but it is not the
default-safe path and it is the single most common way local transcription looks broken.

---

## 5. Calendar — EventKit, and no OAuth at all

This is the biggest deletion in the plan. The commercial version needed a Google Cloud
project, a verified consent screen, sensitive-scope review, and a Microsoft Entra app
registration.

**Personally, you need none of it.** [EventKit](https://developer.apple.com/documentation/eventkit)
reads whatever calendars are already configured in Calendar.app — including Google,
Exchange, and iCloud accounts — with a single local permission prompt and no in-app
authentication whatsoever. Your Google Calendar is already synced there.

You get event titles, times, attendees, and descriptions, which is everything needed to
auto-file notes and pre-seed speaker names.

Known limitation: EventKit reflects Calendar.app's sync state, so a just-created Google
event can take a few minutes to appear. Irrelevant for meetings scheduled in advance;
occasionally annoying for ad-hoc ones. Offer a manual "start recording" button and it stops
mattering.

**Meeting detection:** combine calendar (an event is happening now) with audio activity (a
known process — zoom.us, Teams, a browser on meet.google.com — is producing output). Either
signal alone over- or under-triggers; together they are reliable enough. At personal scope
a menu-bar button plus a notification is a perfectly good fallback, and much less code.

---

## 6. What got deleted from the commercial plan

Everything in this list was a hard requirement for a product and is **not needed** here:

| Dropped | Why it is gone |
|---|---|
| Recall.ai Desktop SDK ($0.50/hr) | Capture is sample code you can crib (§3) |
| Cloud ASR (Deepgram/AssemblyAI, ~$0.58/hr) | WhisperKit is free and local (§4) |
| Google Cloud project, OAuth consent screen, verification | EventKit needs none of it (§5) |
| CASA security assessment (~$540–1,000/yr) | Only applies to restricted Gmail scopes |
| Microsoft Entra registration | macOS-only, EventKit covers Exchange too |
| Windows build (WASAPI, per-process loopback) | Not a target |
| Hosting, Postgres, object storage | Markdown on local disk |
| Clerk / WorkOS / Stripe | One user, no accounts, no billing |
| Sync, CRDTs, multiplayer editing | One device, or iCloud Drive if two |
| Sentry / PostHog | You are the crash reporter |
| Notarisation pipeline, auto-update, Windows cert | Not distributing |
| SOC 2, DPA, sub-processor list, privacy policy | No customers |
| 50-meeting eval corpus | You can eyeball whether notes are good |
| Electron, sidecar IPC, process supervision | One Swift process |

That is roughly 80% of the commercial plan's cost and schedule, removed by the scope change
alone.

---

## 7. The one thing worth over-building

The Big Slick angle survives the scope change and gets *better*, because personally you do
not need it to be a product — you just need it to work once.

`CLAUDE.md` records that `company-onboarding` has never been executed end to end, and that
company context is the distribution's known gap: 247 skills that all want a client pack,
and packs that have to be written by hand. **Meeting transcripts are the richest source of
that context that exists.**

So: after enhancement, add a second pass that appends to `core/clients/<client>/` — new
facts about the account, objections heard, competitor mentions, language the customer
actually used. Then `scripts/make_context_plugin.py <client>` carries it into the desktop
app and the CLI.

That closes a loop nothing else in your stack closes, it is maybe 100 lines of Swift plus a
prompt, and it is the reason to build rather than just install Granola.

---

## 8. Enhancement pass

One Claude call. `claude-opus-5` ($5/$25 per MTok, 1M context), adaptive thinking, streamed.

```
system: <template — "sales call", "1:1", "user interview", "advisory call">
input:  - your sparse typed notes      (high signal, low volume)
        - full transcript, channel-labelled (me / them), timestamped
        - meeting metadata from EventKit (title, attendees, description)
output: summary, decisions, action items with owners, open questions
```

Two design notes that matter more than prompt wording:

- **Your typed notes are the anchor, not an addendum.** What you bothered to type marks what
  mattered; the transcript is context for expanding those anchors. A summariser that ignores
  the typed notes is a commodity — that inversion is the whole Granola insight.
- **Enhancement must be re-runnable.** You will change templates and want old meetings
  re-rendered. Keep the raw transcript forever; treat the enhanced note as derived. Cheap
  insurance, and at $0.10 a re-run you can regenerate your whole history on a whim.

---

## 9. What you still need

The list is now four items long.

1. **An Anthropic API key with billing.** Your Claude Code subscription is not an inference
   budget for a separate app. At ~20 meeting-hours/month this costs about **$2/month**
   (~13K input / 1.5K output tokens per meeting-hour at Opus 5 rates ≈ $0.10 each).
2. **Xcode + an Apple ID.** Free. Enough to build and run locally.
3. **Apple Developer Program, $99/yr — optional, quality-of-life.** Here is the real
   tradeoff: macOS TCC identifies ad-hoc-signed apps by their code hash, which **changes on
   every build**, and it does not honour self-signed team IDs. So with free signing you
   re-grant microphone and audio-capture permission after every rebuild. Tolerable while
   developing, irritating forever. A Developer ID certificate gives a stable team
   identifier and the grants persist. Skip it until the rebuild-reapprove loop annoys you.
4. **Swift + Core Audio familiarity**, or the willingness to acquire it. This is the only
   genuine skill gap. AudioCap makes it a reading exercise rather than a research one, but
   it is still the part of the project that can actually stall. It is also the strongest
   argument for §1.

Nothing else. No accounts to create, no vendors to sign up with, no compliance.

**One non-technical item:** recording consent. Two-party-consent jurisdictions apply to
individuals recording their own calls, not just to companies. Personal use is not an
exemption. Decide how you will disclose, and build the habit rather than the feature.

---

## 10. Realistic phasing

**Weekend 1 — settle the fork question.** Install anarlog, run it against three real
meetings, point it at Claude. If it is good enough, you are done and §11 is moot. This is
the highest-expected-value weekend in the plan.

**Weekend 2 — capture spike.** Build AudioCap, get two separate PCM streams (system + mic)
writing to disk from a real Zoom call. This is the whole technical risk of the project,
front-loaded. If this weekend fails, go back to §1.

**Weekend 3 — pipeline.** WhisperKit over both streams → channel-labelled transcript →
markdown on disk. No UI beyond a menu-bar toggle.

**Weekend 4 — the note.** Notepad UI, the enhancement call, one template. This is the
weekend where it becomes the thing you actually wanted.

**Weekend 5 — glue.** EventKit auto-detection and auto-filing, a second template, and the
Big Slick context pass (§7).

Roughly **a month of weekends** to something you use daily — against 5–7 months for the
commercial version, and possibly one weekend if §1 resolves in anarlog's favour.

---

## 11. Risks, honestly

1. **Core Audio taps stall you.** The mitigation is §1 — fork instead. Give the capture
   spike one weekend and hold yourself to it.
2. **Whisper hallucination makes notes untrustworthy.** VAD gating fixes this, but you have
   to know to look for it, and it will not announce itself — it produces fluent, plausible,
   entirely invented sentences during silence. Check a low-talk meeting early.
3. **You build a worse Granola.** The honest personal-use question is whether this beats
   paying for the real thing. It does if — and probably only if — you want local-only
   audio, your own templates, or the Big Slick loop (§7). If none of those is the actual
   motivation, that is worth knowing before weekend 2.
4. **TCC re-prompting kills the habit.** A tool you have to re-authorise constantly is one
   you stop opening. Either buy the $99 cert or stop rebuilding once it works.

---

## 12. The one decision that matters

**Fork anarlog, or build in Swift?**

Everything else follows. Spend the first weekend answering it empirically rather than
deciding it now — the whole point of §10 is that the answer is cheap to obtain and
expensive to guess wrong.
