# Personal Meeting Notetaker — Build Plan

A single-user macOS app that records meetings, transcribes them on-device, and writes the
summary. No note-taking, no interaction during the call.

**Scope:** one user, one Mac, no distribution, no accounts, no backend, no sync.
**Status:** planning. No code written.
**Date:** 2026-09-09.

> Standalone project. This file is parked in this repo for convenience only — it has no
> dependency on anything here and should move to its own repository when work starts.

---

## 1. Before you write code

One honest check first: **[anarlog](https://github.com/fastrepl/anarlog)** (MIT, formerly
Hyprnote) already does most of this — local recording, on-device transcription, markdown
output on disk, bring-your-own-LLM with Anthropic supported. An evening running it against
three real meetings tells you whether to execute this plan or just configure that.

Build if you want the control, the exercise, or output shaped exactly your way. The rest of
this document assumes you decided to build.

---

## 2. What it does

**The app is invisible until the meeting is over.**

1. **A meeting starts.** It notices — a calendar event is live, or a call app started
   producing audio — and begins recording. A global hotkey does the same manually. The only
   visible sign is a menu-bar indicator.
2. **It records and transcribes in the background.** System audio (them) and microphone
   (you) as separate streams, transcribed on-device. You do nothing.
3. **The meeting ends.** The transcript goes to Claude with the meeting's template, and a
   structured summary comes back.
4. **It files itself.** Bound to the calendar event, with title, time and attendees. Lands
   in a searchable library on disk as markdown.

There is no editor, no during-meeting UI, and nothing to remember to do. You go to a
meeting; afterwards the note exists.

### Feature set, prioritised

**Must have — this is the app**

| Feature | Notes |
|---|---|
| No bot joins the call | Nothing appears in the meeting. Works on Zoom, Meet, Teams, a phone on speaker, or in person. This is the whole thesis |
| Background dual-stream capture | System audio + mic, separately (see §4) |
| On-device transcription | Free, private, no network (see §5) |
| AI summary from the transcript | The output the app exists to produce (see §7) |
| Templates per meeting type | Sales call, 1:1, interview, advisory. **The only steering signal you have** — see the design note below |
| Calendar binding | Title, attendees, time, description pulled automatically (see §6) |
| Library + full-text search | Every meeting, findable |
| Raw transcript retained and viewable | For when you need to check what was actually said |
| Re-run summarisation | Change a template, regenerate old summaries. Cheap, and you will want it constantly |

**Worth having — add once it's a habit**

| Feature | Notes |
|---|---|
| Moment marker hotkey | One keystroke during a call drops a timestamp — no typing. Gives the summariser a priority signal without any note-taking. Cheap to build, and the best available substitute for typed notes |
| Ask questions across meeting history | "What did we agree with Acme in March?" — retrieval over the transcript corpus |
| Action items extracted with owners | Falls out of the summarisation pass; worth its own view |
| Export / copy as markdown | One keystroke to get it wherever it's going next |
| Manual speaker naming | Map "them" to a real name once per recurring meeting |
| Folders or tags | Only once the library is big enough to need them |

**Explicitly not building**

A notepad or editor of any kind. Sharing links, team workspaces, collaborative editing,
sync, mobile, Windows, accounts, billing.

### Design principles

- **Zero interaction is the feature.** If something requires you to act during a meeting,
  it doesn't belong. The app's whole value is that you forget it exists.
- **Templates carry all the steering.** Without typed notes, nothing tells the summariser
  what mattered to *you* — it only knows what was said. Template quality is therefore the
  entire quality lever, not a nicety. Expect to iterate on them, and build for that (§7).
- **Never lose a meeting.** Write audio and partial transcript to disk continuously. A
  crash at minute 50 should cost seconds, not the meeting.

---

## 3. Architecture

One Swift app. One process. macOS 14.4+, Apple Silicon.

```
┌──────────────────────────────────────────────────────────┐
│  SwiftUI menu-bar app                                     │
│                                                           │
│  ┌──────────────────┐   ┌────────────────────────────┐   │
│  │ Library + search │   │ Settings / templates       │   │
│  └──────────────────┘   └────────────────────────────┘   │
│         (no during-meeting UI beyond a status icon)       │
│                                                           │
│  Capture    Core Audio process tap   → system audio       │
│             AVAudioEngine            → microphone         │
│  ASR        WhisperKit (CoreML, streaming, VAD)           │
│  Calendar   EventKit                                      │
│  Store      markdown + JSONL on disk                      │
│  Summarise  Anthropic API via URLSession                  │
└──────────────────────────────────────────────────────────┘
```

No Electron, no sidecar, no IPC, no server, no database daemon, no auth. Every dependency
is an OS framework or a single Swift package — one Xcode project.

Dropping the editor removes the only part of the UI that needed to be good. What remains is
a menu-bar item, a list, and a settings pane.

---

## 4. Capture

The one subsystem with real difficulty — and where to start, because if it doesn't work
nothing else matters.

**Use Core Audio process taps** — `AudioHardwareCreateProcessTap` with a `CATapDescription`,
macOS 14.2+/14.4+. Not ScreenCaptureKit: taps are audio-only, can be scoped to specific
processes (tap Zoom, ignore your music), and avoid demanding the Screen Recording permission
and menu-bar recording indicator for an app that never touches the screen.

**Start from working sample code.** [insidegui/AudioCap](https://github.com/insidegui/AudioCap)
is Guilherme Rambo's reference implementation of exactly this — tap creation, the
aggregate-device setup, permission handling.
[AudioTee](https://stronglytyped.uk/articles/audiotee-capture-system-audio-output-macos)
is a second implementation as a CLI. Apple documents the API in
[Capturing system audio with Core Audio taps](https://developer.apple.com/documentation/coreaudio/capturing-system-audio-with-core-audio-taps).
This makes the hard part a reading exercise rather than a research project.

**Capture mic and system audio as two separate streams.** The most important structural
decision in the app. You get "me vs. them" attribution for free — perfect accuracy on the
speaker boundary that matters most, with zero diarization, no ML, no cost. Diarizing
multiple remote speakers becomes an optional refinement rather than a dependency.
Retrofitting this is a re-plumb of the whole pipeline, so do it on day one.

**Write to disk continuously.** Rolling audio chunks plus append-only partial transcript.
Never hold a whole meeting in memory.

**Edge cases you can ignore at personal scope:** headphone switching mid-call, Bluetooth
dropping to 8/16 kHz HFP, mute-state detection, simultaneous audio sessions, multi-hour
recordings. Handle each only when it actually bites you. Skipping them is most of why this
is weekends rather than months.

---

## 5. Transcription

**[WhisperKit](https://github.com/argmaxinc/argmax-oss-swift)** — MIT, a Swift Package,
CoreML models on the Neural Engine, with **real-time streaming and voice activity detection
built in** and pre-converted model variants ready to pull. As of v1.0.0 the repo is
`argmaxinc/argmax-oss-swift`.

This turns "ship an ML pipeline inside a desktop app" into an `import`. Cost is zero, audio
never leaves the machine, and on Apple Silicon it runs comfortably faster than realtime.

whisper.cpp is the alternative if you'd rather work in Metal/GGML directly. Either is fine;
WhisperKit is less assembly.

**Gate on VAD.** Whisper hallucinates during silence — fluent, confident, entirely invented
sentences from nothing. This is the most common way local transcription looks broken and it
will not announce itself. WhisperKit ships VAD, so this is configuration rather than code,
but it is not the default-safe path. Test against a meeting with long quiet stretches early.

**This matters more now.** With no typed notes to cross-check against, the transcript is the
*only* input to the summary. A hallucinated passage goes straight into the note with nothing
to contradict it. Getting VAD right is not optional polish here.

Run ASR on both channels independently and merge by timestamp into one labelled transcript.

---

## 6. Calendar

**EventKit.** It reads whatever calendars are already configured in Calendar.app —
including Google, Exchange and iCloud accounts — behind a single local permission prompt,
with no in-app authentication at all.

This deletes an entire subsystem. The alternative (Google Calendar API) means a Google
Cloud project, an OAuth consent screen, scope review, and app verification — weeks of
process for data already sitting on your Mac.

You get event title, time, attendees and description: enough to auto-file the summary, fill
the note header, select a template by meeting type, and offer real names for the "them"
channel.

**Known limitation:** EventKit reflects Calendar.app's sync state, so an event created in
Google seconds ago may take minutes to appear. Irrelevant for scheduled meetings,
occasionally annoying for ad-hoc ones — the manual hotkey covers it.

**Meeting detection matters more without a notepad.** In the previous design, opening the
notepad *was* the start signal. Now detection is the only thing standing between you and a
missed meeting. Combine two signals: a calendar event is currently active, *and* a known
process (`zoom.us`, Teams, a browser on a Meet/Webex URL) is producing audio. Ship the
manual hotkey first — it's ten lines and makes auto-detection a refinement rather than a
blocker.

---

## 7. The summarisation pass

One Claude call. Cheapest component, and now the entire perceived value of the app.

**Model:** `claude-opus-5` ($5 / $25 per MTok, 1M context). Adaptive thinking
(`thinking: {type: "adaptive"}`), streamed.

**Inputs:**

```
system:  the selected template — output structure, tone, what to extract,
         what to ignore

user:    ## Meeting
         title, attendees, scheduled time, calendar description

         ## Transcript
         [00:04:12] them: ...
         [00:04:31] me:   ...

         ## Marked moments        (if the marker hotkey is built)
         [00:22:07], [00:41:55]
```

**Output:** structured markdown — summary, decisions made, action items with owners, open
questions, and whatever else the template specifies.

**Cost:** a one-hour meeting is ~9,000–10,000 spoken words ≈ 13K input tokens, ~1.5K out.
About **$0.10 per meeting**, or roughly **$2/month** at 20 meeting-hours. Cheap enough that
regenerating your entire history after a template change costs less than lunch.

**Prompt caching:** template and standing instructions first with a cache breakpoint after
them; the transcript is volatile and goes last. Verify via `usage.cache_read_input_tokens`
rather than assuming.

**Templates are the product.** This is the consequence of dropping typed notes. A generic
"summarise this meeting" prompt produces the same bland output as every other tool. What
makes the summary yours is a template that knows a discovery call needs budget signals,
objections and next steps, while a 1:1 needs commitments and blockers. Budget real time
here — it is where the quality is, and it is the only lever you have left.

**Treat the summary as derived.** Raw transcript is the source of truth and kept forever;
the summary can always be regenerated. This is what makes template iteration safe, and
template iteration is how the app gets good.

---

## 8. Storage

**Markdown files on disk. Not a database.**

For one user this is strictly better: greppable, diffable, Git-versionable, readable by
every other tool you own, and directly readable by Claude Code. If the app dies, your
summaries don't.

```
~/Meetings/
  2026-09-09-acme-discovery/
    summary.md         ← generated note (regenerable)
    transcript.jsonl   ← [{t_start, t_end, channel, text, confidence}]
    meeting.json       ← title, attendees, times, template, markers, event id
    audio/             ← optional, deleted after transcription by default
```

Default to **discarding audio once transcription completes.** It's the largest and most
sensitive artifact, the transcript is what you actually use, and keeping it is an
always-on liability for no benefit. Make it a setting; default it off.

Add a SQLite index only when search gets slow — at personal volume, ripgrep over the
directory is genuinely fine for years. When you do, index for search and keep the files as
truth. For "ask questions across history", embeddings in `sqlite-vec` alongside that index.

---

## 9. Prerequisites

1. **Anthropic API key with billing.** A Claude subscription is not an inference budget for
   a separate app — this needs its own key with its own spend limit. ~$2/month.
2. **Xcode and an Apple ID.** Free, and enough to build and run locally.
3. **Apple Developer Program, $99/yr — optional.** The real tradeoff: macOS TCC identifies
   ad-hoc-signed apps by their code hash, which **changes on every build**, and it does not
   honour self-signed team IDs. With free signing you re-approve microphone and
   audio-capture permission after every rebuild. Fine while developing, corrosive to a
   daily habit — and worse here, because an app you never interact with is one whose
   silently-revoked permission you won't notice until a meeting is already lost. Defer it,
   then buy it without hesitating.
4. **Swift and Core Audio familiarity**, or willingness to acquire it. The only real skill
   gap, and the only thing that can genuinely stall the project.

**One non-technical prerequisite:** recording consent. Two-party-consent jurisdictions
apply to individuals recording their own calls — personal use is not an exemption. This
design makes it easier to forget you're recording at all, which makes the habit of
disclosing more important, not less.

---

## 10. Build order

Sequenced so the riskiest thing is answered first and every stage is independently useful.

**Stage 1 — capture spike.** Build AudioCap. Get two separate PCM streams (system + mic)
from a real Zoom call written to disk. No UI. This is the project's entire technical risk,
deliberately front-loaded. Give it one weekend; if it fails, revisit §1.

**Stage 2 — transcript pipeline.** WhisperKit over both channels, merged by timestamp into
one labelled `transcript.jsonl`. Menu-bar start/stop only. At the end of this stage you
have a working local transcriber, useful on its own.

**Stage 3 — the summary.** The Claude call, one template, markdown written to disk. This is
where it becomes the thing you wanted, and where you start using it daily.

**Stage 4 — make it disappear.** EventKit binding and auto-detection, global hotkey,
library view and search. Turns a tool you have to remember into one that just runs — which
in this design is the entire point.

**Stage 5 — templates, driven by use.** More templates, refined from real output. Marker
hotkey, transcript viewer, speaker naming, export.

Roughly **three weekends** to daily-driver quality — one fewer than the notepad design,
since stage 3 is now an API call and a file write rather than an editor.

---

## 11. Pitfalls worth knowing in advance

1. **Core Audio taps stall the project.** The most likely failure mode. Mitigated by
   starting there and by AudioCap existing. Hold yourself to the one-weekend box.
2. **Whisper hallucination during silence.** Fluent, plausible, invented text — and with no
   typed notes to contradict it, it lands in the summary unchallenged. Test a low-talk
   meeting early.
3. **Generic summaries.** The predictable failure mode of this design: without your notes
   as a signal, a weak template produces the same output as every other AI notetaker, and
   you stop reading them. The fix is template work, not model work.
4. **Silent misses.** An app with no UI fails silently — a missed detection, a revoked
   permission, a crashed capture. Add a cheap daily check: if a calendar meeting had no
   recording, say so.
5. **TCC reapproval kills the habit.** Either buy the $99 certificate or stop rebuilding
   once it works.

---

## 12. Open decisions

1. **Summarise automatically on meeting end, or on demand?** Automatic fits this design —
   the app is meant to be invisible — and costs $0.10 a time. Probably automatic, with a
   setting.
2. **Marker hotkey: build it or not?** It's the only way to give the summariser a priority
   signal without typing. Cheap, and it recovers some of what dropping notes gave up.
   Worth trying once templates are stable enough to judge the difference.
3. **How many templates to start?** One, used properly, beats four half-written. Start with
   whichever meeting type you have most of this month.
