# Personal Meeting Notetaker — Build Plan

A single-user macOS desktop app with Granola's core functionality.

**Scope:** one user, one Mac, no distribution, no accounts, no backend, no sync.
**Status:** planning. No code written.
**Date:** 2026-09-09.

> Standalone project. This file is parked in this repo for convenience only — it has no
> dependency on anything here and should move to its own repository when work starts.

---

## 1. Before you write code

One honest check first: **[anarlog](https://github.com/fastrepl/anarlog)** (MIT, formerly
Hyprnote) already does most of this — local recording, on-device transcription, markdown
notes on disk, bring-your-own-LLM with Anthropic supported. An evening spent running it
against three real meetings tells you whether this plan is worth executing or whether you
just install that and configure it.

Build if you want the control, the exercise, or a note model that matches how you actually
work. The rest of this document assumes you decided to build.

---

## 2. What it does — the functionality that matters

Granola's insight is not transcription. It is that **you keep taking notes the way you
already do, and the machine fills in everything you didn't have time to write.** The
transcript is scaffolding, not the product. Everything below serves that.

### The core loop

1. **A meeting starts.** The app notices — a calendar event is live, or a call app started
   producing audio — and offers to open a notepad. A global hotkey does the same thing
   manually, and a menu-bar icon shows recording state.
2. **You type sparse notes.** This is the primary UI during the call: a clean, fast text
   editor. Not a transcript view, not a waveform, not a dashboard. Whatever you'd have
   typed anyway — half-sentences, names, a number someone said, a question to come back to.
3. **It records and transcribes in the background.** System audio (them) and microphone
   (you) as separate streams, transcribed on-device, invisible while you work.
4. **The meeting ends.** One action — or automatically — and the enhanced note appears:
   your fragments expanded into a structured document using the full transcript as source.
5. **It files itself.** Bound to the calendar event, with title, time and attendees. Lands
   in a searchable library on disk.

That is the whole product. Everything else is convenience.

### Feature set, prioritised

**Must have — this is the app**

| Feature | Notes |
|---|---|
| No bot joins the call | Nothing appears in the meeting. Works on Zoom, Meet, Teams, a phone on speaker, or an in-person conversation. This is the entire thesis |
| Live notepad during the meeting | Fast, plain, keyboard-first. Markdown. Never blocks on transcription |
| Background dual-stream capture | System audio + mic, separately (see §4) |
| On-device transcription | Free, private, no network (see §5) |
| AI enhancement of your notes | The moment the product exists for (see §7) |
| Templates per meeting type | Sales call, 1:1, interview, advisory. Determines output structure. This is what makes the notes yours rather than generic |
| Calendar binding | Title, attendees, time, description pulled automatically (see §6) |
| Library + full-text search | Every meeting, findable |
| Raw transcript retained and viewable | Secondary UI. Available when you need to check what was actually said |
| Re-run enhancement | Change a template, regenerate old notes. Cheap and you will want it constantly |

**Worth having — add once the core loop is a habit**

| Feature | Notes |
|---|---|
| Ask questions across meeting history | "What did we agree with Acme in March?" — retrieval over the transcript corpus |
| Action items extracted with owners | Falls out of the enhancement pass; worth surfacing as its own view |
| Export / copy note as markdown | One keystroke to get it into wherever it's going next |
| Manual speaker naming | Map "them" to a real name once per recurring meeting |
| Folders or tags | Only once the library is big enough to need them |

**Explicitly not building**

Sharing links, team workspaces, collaborative editing, sync across devices, mobile, Windows,
accounts, billing. Every one of these is most of a product on its own and none of them
serve a single user on one Mac.

### Design principles

Three rules that decide most of the small questions later:

- **The notepad is the interface.** If a feature makes the during-meeting view busier, it
  belongs somewhere else. You are in a conversation; the app gets one small corner of your
  attention.
- **Your typed notes are the anchor, not an addendum.** What you bothered to type marks
  what mattered. The transcript expands those anchors — it does not outrank them. A tool
  that ignores your notes and summarises the transcript is a commodity; this inversion is
  the whole idea.
- **Never lose a meeting.** Write audio and partial transcript to disk continuously. A
  crash at minute 50 should cost seconds, not the meeting.

---

## 3. Architecture

One Swift app. One process. macOS 14.4+, Apple Silicon.

```
┌──────────────────────────────────────────────────────────┐
│  SwiftUI menu-bar app                                     │
│                                                           │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐ │
│  │ Notepad     │   │ Library +    │   │ Settings /     │ │
│  │ (live)      │   │ search       │   │ templates      │ │
│  └─────────────┘   └──────────────┘   └────────────────┘ │
│                                                           │
│  Capture    Core Audio process tap   → system audio       │
│             AVAudioEngine            → microphone         │
│  ASR        WhisperKit (CoreML, streaming, VAD)           │
│  Calendar   EventKit                                      │
│  Store      markdown + JSON on disk                       │
│  Enhance    Anthropic API via URLSession                  │
└──────────────────────────────────────────────────────────┘
```

No Electron, no sidecar, no IPC, no server, no database daemon, no auth. Every dependency
is either an OS framework or a single Swift package. It is one Xcode project.

**Why all-Swift rather than Electron:** you need native audio capture regardless, so
Electron buys you a web UI at the cost of a second runtime and a process boundary around
the riskiest component. At single-user scale the web-ecosystem advantages don't pay for
that. SwiftUI is more than adequate for a notepad and a list.

---

## 4. Capture

The one subsystem with real difficulty — and the one place to start, because if it doesn't
work nothing else matters.

**Use Core Audio process taps** — `AudioHardwareCreateProcessTap` with a `CATapDescription`,
macOS 14.2+/14.4+. Not ScreenCaptureKit: taps are audio-only, can be scoped to specific
processes (tap Zoom, ignore your music), and avoid demanding the Screen Recording permission
and the menu-bar recording indicator for an app that never touches the screen.

**Start from working sample code.** [insidegui/AudioCap](https://github.com/insidegui/AudioCap)
is Guilherme Rambo's reference implementation of exactly this — tap creation, the
aggregate-device setup, and permission handling.
[AudioTee](https://stronglytyped.uk/articles/audiotee-capture-system-audio-output-macos)
is a second implementation as a CLI. Apple documents the API directly in
[Capturing system audio with Core Audio taps](https://developer.apple.com/documentation/coreaudio/capturing-system-audio-with-core-audio-taps).
This turns the hard part into a reading exercise rather than a research project.

**Capture mic and system audio as two separate streams.** The single most important
structural decision in the app. You get "me vs. them" attribution for free — perfect
accuracy on the speaker boundary that matters most, with zero diarization, no ML, and no
cost. Diarizing multiple remote speakers becomes an optional later refinement rather than a
dependency. Retrofitting this is a re-plumb of the entire pipeline, so do it on day one.

**Write to disk continuously.** Rolling audio chunks plus append-only partial transcript.
Never hold a whole meeting in memory.

**Edge cases you can ignore at personal scope** — and would have to solve commercially:
headphone switching mid-call, Bluetooth dropping to 8/16 kHz HFP, mute-state detection,
simultaneous audio sessions, multi-hour recordings. Handle each only when it actually bites
you. Skipping them is most of why this is a month of weekends rather than half a year.

---

## 5. Transcription

**[WhisperKit](https://github.com/argmaxinc/argmax-oss-swift)** — MIT, a Swift Package,
CoreML models running on the Neural Engine, with **real-time streaming and voice activity
detection built in** and pre-converted model variants ready to pull. As of v1.0.0 the repo
is `argmaxinc/argmax-oss-swift`.

This is the dependency that turns "ship an ML pipeline inside a desktop app" into an
`import`. Cost is zero, audio never leaves the machine, and on Apple Silicon it runs
comfortably faster than realtime.

whisper.cpp is the alternative if you'd rather work in Metal/GGML directly. Either is fine;
WhisperKit is less assembly.

**Gate on VAD.** Whisper hallucinates during silence — it produces fluent, confident,
entirely invented sentences from nothing. This is the single most common way local
transcription looks broken, and it will not announce itself. WhisperKit ships VAD, so this
is configuration rather than code, but it is not the default-safe path. Test against a
meeting with long quiet stretches early.

Run ASR on both channels independently and merge by timestamp into a single labelled
transcript.

---

## 6. Calendar

**EventKit.** It reads whatever calendars are already configured in Calendar.app —
including Google, Exchange and iCloud accounts — behind a single local permission prompt,
with no in-app authentication at all.

This deletes an entire subsystem. The alternative (Google Calendar API) means a Google
Cloud project, an OAuth consent screen, scope review, and app verification — weeks of
process for data already sitting on your Mac.

You get event title, time, attendees and description: enough to auto-file notes, pre-seed
the note header, and offer real names for the "them" channel.

**Known limitation:** EventKit reflects Calendar.app's sync state, so an event created in
Google seconds ago may take a few minutes to appear. Irrelevant for scheduled meetings,
occasionally annoying for ad-hoc ones — the manual hotkey covers it.

**Meeting detection:** combine two signals. A calendar event is currently active, *and* a
known process (`zoom.us`, Teams, a browser on a Meet/Webex URL) is producing audio. Either
alone misfires; together they're reliable. Ship the manual hotkey first — it's ten lines
and it makes auto-detection a refinement rather than a blocker.

---

## 7. The enhancement pass

One Claude call. This is the cheapest component and the entire perceived value.

**Model:** `claude-opus-5` ($5 / $25 per MTok, 1M context). Adaptive thinking
(`thinking: {type: "adaptive"}`), streamed so the note appears progressively.

**Inputs:**

```
system:  the selected template — output structure, tone, what to extract
         + the standing instruction that the user's notes are the outline

user:    ## My notes
         <your sparse typed notes>

         ## Transcript
         [00:04:12] them: ...
         [00:04:31] me:   ...

         ## Meeting
         title, attendees, scheduled time, calendar description
```

**Output:** structured markdown — summary, decisions made, action items with owners, open
questions, and whatever else the template asks for.

**Cost:** a one-hour meeting is ~9,000–10,000 spoken words ≈ 13K input tokens, with ~1.5K
out. That is **about $0.10 per meeting**, or roughly **$2/month** at 20 meeting-hours.
Cheap enough that re-running enhancement across your whole history after a template change
costs less than lunch.

**Prompt caching:** put the template and standing instructions first with a cache
breakpoint after them; the transcript is volatile and goes last. Verify it's working via
`usage.cache_read_input_tokens` rather than assuming.

**Treat the enhanced note as derived.** Raw transcript and raw notes are the source of
truth and are kept forever; the enhanced note can always be regenerated. This is what makes
template iteration safe, and template iteration is how the app gets good.

---

## 8. Storage

**Markdown files on disk. Not a database.**

For one user this is strictly better: greppable, diffable, Git-versionable, readable by
every other tool you own, and directly readable by Claude Code. If the app dies, your notes
don't.

```
~/Meetings/
  2026-09-09-acme-discovery/
    note.md            ← enhanced note (regenerable)
    raw-notes.md       ← what you typed (source of truth)
    transcript.jsonl   ← [{t_start, t_end, channel, text, confidence}]
    meeting.json       ← title, attendees, times, template, calendar event id
    audio/             ← optional, deleted after transcription by default
```

Default to **discarding audio once transcription completes.** It's the largest and most
sensitive artifact, the transcript is what you actually use, and keeping it is an
always-on liability for no benefit. Make it a setting; default it off.

Add a SQLite index only when search gets slow — at personal volume, ripgrep over the
directory is genuinely fine for years. When you do add it, index for search; keep the
files as truth.

For the "ask questions across history" feature, embeddings in `sqlite-vec` alongside that
index.

---

## 9. Prerequisites

1. **Anthropic API key with billing.** A Claude subscription is not an inference budget for
   a separate app — this needs its own key with its own spend limit. ~$2/month at normal use.
2. **Xcode and an Apple ID.** Free, and enough to build and run locally.
3. **Apple Developer Program, $99/yr — optional.** The real tradeoff: macOS TCC identifies
   ad-hoc-signed apps by their code hash, which **changes on every build**, and it does not
   honour self-signed team IDs. With free signing you re-approve microphone and
   audio-capture permission after every rebuild. Fine while developing, corrosive to a daily
   habit. A Developer ID certificate gives a stable team identifier and the grants persist.
   Defer it until the reapproval loop annoys you, then buy it without hesitating.
4. **Swift and Core Audio familiarity**, or willingness to acquire it. The only real skill
   gap, and the only thing that can genuinely stall the project.

**One non-technical prerequisite:** recording consent. Two-party-consent jurisdictions
apply to individuals recording their own calls — personal use is not an exemption. Decide
how you disclose, and make it a habit rather than a feature.

---

## 10. Build order

Sequenced so the riskiest thing is answered first and every stage is independently useful.

**Stage 1 — capture spike.** Build AudioCap. Get two separate PCM streams (system + mic)
from a real Zoom call written to disk. No UI. This is the project's entire technical risk,
deliberately front-loaded. Give it one weekend; if it fails, revisit §1.

**Stage 2 — transcript pipeline.** WhisperKit over both channels, merged by timestamp into
one labelled `transcript.jsonl`. Still no UI beyond a menu-bar start/stop. At the end of
this stage you have a working local transcriber, which is already useful on its own.

**Stage 3 — the note.** The notepad UI, the enhancement call, one template, markdown
written to disk. This is the stage where it becomes the thing you actually wanted — and the
first point at which you should start using it daily.

**Stage 4 — make it a habit.** EventKit binding and auto-detection, global hotkey, the
library view and search. Turns a tool you have to remember into one that just runs.

**Stage 5 — refinement, driven by use.** More templates, re-run enhancement, transcript
viewer, speaker naming, export. Only build what a month of real use actually demands.

Roughly **a month of weekends** to daily-driver quality, with something useful in hand from
stage 2 onward.

---

## 11. Pitfalls worth knowing in advance

1. **Core Audio taps stall the project.** The most likely failure mode. Mitigated by
   starting there (stage 1) and by AudioCap existing. Hold yourself to the one-weekend box.
2. **Whisper hallucination during silence.** Fluent, plausible, invented text. VAD gating
   fixes it, but you have to know to look. Test a low-talk meeting early — this destroys
   trust in the notes faster than anything else.
3. **TCC reapproval kills the habit.** A tool you must re-authorise constantly is a tool you
   stop opening. Either buy the $99 certificate or stop rebuilding once it works.
4. **Enhancement quality is invisible without comparison.** You will not notice a prompt
   regression. Keep three real meetings as a fixed check set and re-run them after every
   template change — informal, but enough to catch the obvious.
5. **Scope creep toward the commercial product.** Sharing, sync, and multi-device are each
   most of a product. The value here comes from the core loop being excellent for one
   person.

---

## 12. Open decisions

1. **Enhance automatically on meeting end, or on demand?** Automatic is more magical and
   costs $0.10 a time; on-demand is more controlled. Probably automatic with a setting.
2. **Notepad as a floating always-on-top window, or a normal one?** Depends on whether you
   run calls full-screen. Affects the during-meeting experience more than it sounds.
3. **How many templates to start?** One, used properly, beats four half-written. Start with
   whichever meeting type you have most of this month.
