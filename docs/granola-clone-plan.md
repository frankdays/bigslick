# Personal Meeting Notetaker — Build Plan

A single-user macOS app that alerts you before a meeting, joins the call, records it,
transcribes on-device, and writes the summary.

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

1. **A minute before your meeting, a notification appears.** Meeting name, time,
   attendees, and three buttons: **Join & Record**, **Record only**, **Skip**.
2. **You click Join & Record.** Zoom launches straight into the call, and recording arms
   at the same moment. One click, from a notification, before the meeting.
3. **It records and transcribes in the background.** System audio (them) and microphone
   (you) as separate streams, transcribed on-device. Nothing to do during the call.
4. **The meeting ends.** The transcript goes to Claude with the meeting's template, and a
   structured summary comes back.
5. **It files itself.** Bound to the calendar event, with title, time and attendees. Lands
   in a searchable library on disk as markdown.

No editor, no during-meeting UI. The only interaction in the whole flow is one click on a
notification you were about to act on anyway.

### Feature set, prioritised

**Must have — this is the app**

| Feature | Notes |
|---|---|
| Pre-meeting alert with Join & Record | The entry point to everything else (see §7) |
| Launches the call app directly | Zoom deep link, or the meeting URL for Meet/Teams (see §7) |
| No bot joins the call | Nothing appears in the meeting. Works on Zoom, Meet, Teams, a phone on speaker, or in person |
| Background dual-stream capture | System audio + mic, separately (see §4) |
| On-device transcription | Free, private, no network (see §5) |
| AI summary from the transcript | The output the app exists to produce (see §8) |
| Templates per meeting type | Sales call, 1:1, interview, advisory. **The only steering signal you have** |
| Calendar binding | Title, attendees, time, description, meeting link (see §6) |
| Library + full-text search | Every meeting, findable |
| Raw transcript retained and viewable | For when you need to check what was actually said |
| Re-run summarisation | Change a template, regenerate old summaries. Cheap, and you will want it |

**Worth having — add once it's a habit**

| Feature | Notes |
|---|---|
| Moment marker hotkey | One keystroke during a call drops a timestamp — no typing. Gives the summariser a priority signal. The best available substitute for typed notes |
| Ask questions across meeting history | Retrieval over the transcript corpus |
| Action items extracted with owners | Falls out of the summarisation pass; worth its own view |
| Export / copy as markdown | One keystroke to get it wherever it's going next |
| Manual speaker naming | Map "them" to a real name once per recurring meeting |
| Folders or tags | Only once the library needs them |

**Explicitly not building**

A notepad or editor of any kind. Sharing links, team workspaces, collaborative editing,
sync, mobile, Windows, accounts, billing.

### Design principles

- **One click, before the meeting. Zero during it.** The alert is the single point of
  interaction. Once you're in the call the app is invisible.
- **The alert must be trustworthy.** It fires for the right meetings and not the wrong
  ones. An alert that cries wolf on declined invites and holiday calendars gets dismissed
  reflexively, and then it silently stops working. Filtering (§7) is not a detail.
- **Templates carry all the steering.** Without typed notes, nothing tells the summariser
  what mattered to *you* — only what was said. Template quality is the entire quality
  lever. Expect to iterate, and build for that (§8).
- **Never lose a meeting.** Write audio and partial transcript to disk continuously. A
  crash at minute 50 should cost seconds, not the meeting.

---

## 3. Architecture

One Swift app. One process. macOS 14.4+, Apple Silicon. Runs as a menu-bar agent at login.

```
┌──────────────────────────────────────────────────────────┐
│  SwiftUI menu-bar agent (LSUIElement, launch at login)    │
│                                                           │
│  ┌──────────────────┐   ┌────────────────────────────┐   │
│  │ Library + search │   │ Settings / templates       │   │
│  └──────────────────┘   └────────────────────────────┘   │
│                                                           │
│  Alerts     EventKit → UserNotifications → NSWorkspace    │
│  Capture    Core Audio process tap   → system audio       │
│             AVAudioEngine            → microphone         │
│  ASR        WhisperKit (CoreML, streaming, VAD)           │
│  Store      markdown + JSONL on disk                      │
│  Summarise  Anthropic API via URLSession                  │
└──────────────────────────────────────────────────────────┘
```

No Electron, no sidecar, no IPC, no server, no database daemon, no auth. Every dependency
is an OS framework or a single Swift package — one Xcode project.

**The alert makes always-running a hard requirement.** Mark the app `LSUIElement` (menu bar
only, no Dock icon) and register it as a login item with
`SMAppService.mainApp.register()`. An app you have to remember to launch cannot alert you
about a meeting you forgot.

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
speaker boundary that matters most, with zero diarization, no ML, no cost. Retrofitting it
is a re-plumb of the whole pipeline, so do it on day one.

**Arming vs. starting.** "Join & Record" arms the tap; it should start capturing when the
call app actually produces audio, not the instant you click. Clicking the alert, waiting
through the Zoom splash screen, and picking an audio device can take twenty seconds — and
a recording that starts on click captures that silence, which is exactly the input Whisper
hallucinates against (§5).

**Write to disk continuously.** Rolling audio chunks plus append-only partial transcript.
Never hold a whole meeting in memory.

**Edge cases you can ignore at personal scope:** headphone switching mid-call, Bluetooth
dropping to 8/16 kHz HFP, mute-state detection, simultaneous audio sessions, multi-hour
recordings. Handle each only when it bites you.

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

**This matters more without notes.** The transcript is the *only* input to the summary. A
hallucinated passage goes straight into the note with nothing to contradict it.

Run ASR on both channels independently and merge by timestamp into one labelled transcript.

---

## 6. Calendar

**EventKit.** It reads whatever calendars are already configured in Calendar.app —
including Google, Exchange and iCloud accounts — behind a single local permission prompt,
with no in-app authentication at all.

This deletes an entire subsystem. The alternative (Google Calendar API) means a Google
Cloud project, an OAuth consent screen, scope review, and app verification — weeks of
process for data already sitting on your Mac.

You get event title, time, attendees, description and URL: enough to fire the alert, launch
the call, file the summary, select a template, and offer real names for the "them" channel.

**Known limitation:** EventKit reflects Calendar.app's sync state, so an event created in
Google seconds ago may take minutes to appear. Irrelevant for scheduled meetings — which is
what the alert is for — and the manual hotkey covers the rest.

---

## 7. Pre-meeting alert and auto-join

The entry point to the whole app. Four pieces: schedule, alert, extract, launch.

### 7.1 Scheduling the alert

Watch EventKit for changes (`NSNotification.Name.EKEventStoreChanged`) and re-scan on a
timer as well — EventKit's sync lag means change notifications alone will miss things.
Query events in the next few hours and register a `UNNotificationRequest` per meeting with
a `UNCalendarNotificationTrigger` at **T-1 minute** (configurable; T-2 if you like a moment
to breathe).

Cancel and re-register pending requests whenever the store changes — meetings get moved and
cancelled constantly, and a notification for a meeting that no longer exists is exactly the
kind of thing that trains you to ignore alerts.

### 7.2 Which meetings get an alert

This filtering is what makes the feature trustworthy rather than annoying. Skip:

- All-day events
- Events you declined (check your own participant status in `event.attendees`)
- Events with no other attendees (usually blocks and reminders, not meetings)
- Calendars you didn't opt in — a per-calendar allowlist in settings. Holiday and birthday
  calendars must never fire an alert
- Duplicates: the same meeting present on both a personal and a work calendar, deduped on
  title + start time

Optionally skip events under a few minutes, and events already in progress when the app
launches.

### 7.3 The notification

`UNUserNotificationCenter` with a `UNNotificationCategory` carrying three
`UNNotificationAction`s, handled in `userNotificationCenter(_:didReceive:)`:

| Action | Behaviour |
|---|---|
| **Join & Record** | Open the meeting link (§7.4) *and* arm recording |
| **Record only** | Arm recording without launching anything — for dial-ins, in-person meetings, or when you'll join yourself |
| **Skip** | Dismiss; no recording for this event, and don't re-alert |

Requires notification permission — `UNUserNotificationCenter.current().requestAuthorization([.alert, .sound])`
— which is one more prompt to handle in onboarding.

**If you don't click anything,** fall back to the audio-activity detection from §7.5 rather
than doing nothing. The alert is the fast path, not the only path.

### 7.4 Extracting and launching the meeting link

**There is no reliable structured field for this.** `EKVirtualConferenceProvider` and
`EKVirtualConferenceDescriptor` exist for apps that *offer* conference rooms to Calendar —
they are not a way to read a third-party Zoom or Meet link off someone else's invite. So
you parse, in priority order:

1. `event.url` — Google Calendar often populates this with the Meet link
2. `event.location` — where Zoom invites frequently put the join URL
3. `event.notes` — the invite body, where everything else ends up

Match per platform, first hit wins, and store what you found on the meeting record so you
can see why a launch failed.

**Launching:**

- **Zoom** — rewrite the web URL to the app's deep link so it opens the client directly
  instead of bouncing through a browser launch page:
  `https://<sub>.zoom.us/j/<id>?pwd=<pwd>` → `zoommtg://zoom.us/join?confno=<id>&pwd=<pwd>`,
  opened with `NSWorkspace.shared.open`. The `zoommtg://` scheme does nothing if the Zoom
  client isn't installed, so check with `NSWorkspace.shared.urlForApplication(toOpen:)`
  first and fall back to the original https URL.
- **Google Meet, Teams, Webex** — just open the https URL; the browser or the native
  handler takes it from there. Teams also registers `msteams://` if you want the app
  specifically.
- **No link found** — degrade to Record only, and say so in the notification rather than
  silently doing nothing.

### 7.5 Fallback detection

Keep the audio-activity path from the earlier design as a safety net: if a calendar event
is currently active *and* a known process (`zoom.us`, Teams, a browser on a Meet/Webex URL)
is producing audio, offer to record even though the alert wasn't clicked. This catches the
meeting you joined from your phone, the one that started early, and the one whose alert you
missed because the Mac was asleep.

### 7.6 Edge cases

- **Mac asleep at meeting time.** The notification fires on wake, possibly well after the
  meeting started. Check the event's end time before offering to join.
- **Recurring meetings.** Schedule per occurrence, not per series.
- **Already recording.** Never double-start; the alert should reflect that a recording is
  already running.
- **Back-to-back meetings.** Close out the previous recording before arming the next.
- **Zoom passcode as text in the notes** rather than in the URL — common with copy-pasted
  invites. Parse it if it's adjacent; otherwise let Zoom prompt.

---

## 8. The summarisation pass

One Claude call. Cheapest component, and the entire perceived value of the app.

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

**Templates are the product.** A generic "summarise this meeting" prompt produces the same
bland output as every other tool. What makes the summary yours is a template that knows a
discovery call needs budget signals, objections and next steps, while a 1:1 needs
commitments and blockers. The calendar event can select the template automatically — by
title pattern, attendee domain, or which calendar it's on.

**Treat the summary as derived.** Raw transcript is the source of truth and kept forever;
the summary can always be regenerated. This is what makes template iteration safe, and
template iteration is how the app gets good.

---

## 9. Storage

**Markdown files on disk. Not a database.**

For one user this is strictly better: greppable, diffable, Git-versionable, readable by
every other tool you own, and directly readable by Claude Code. If the app dies, your
summaries don't.

```
~/Meetings/
  2026-09-09-acme-discovery/
    summary.md         ← generated note (regenerable)
    transcript.jsonl   ← [{t_start, t_end, channel, text, confidence}]
    meeting.json       ← title, attendees, times, template, markers,
                          event id, join link, how it was started
    audio/             ← optional, deleted after transcription by default
```

Default to **discarding audio once transcription completes.** It's the largest and most
sensitive artifact, the transcript is what you actually use, and keeping it is an
always-on liability for no benefit. Make it a setting; default it off.

Add a SQLite index only when search gets slow — at personal volume, ripgrep over the
directory is fine for years. For "ask questions across history", embeddings in
`sqlite-vec` alongside that index.

---

## 10. Prerequisites

1. **Anthropic API key with billing.** A Claude subscription is not an inference budget for
   a separate app — this needs its own key with its own spend limit. ~$2/month.
2. **Xcode and an Apple ID.** Free, and enough to build and run locally.
3. **Apple Developer Program, $99/yr — optional, but more compelling now.** macOS TCC
   identifies ad-hoc-signed apps by their code hash, which **changes on every build**, and
   it does not honour self-signed team IDs. With free signing you re-approve microphone and
   audio-capture permission after every rebuild — and notification permission and login-item
   registration are in the same boat. An app that alerts you is one whose silently-revoked
   permissions you won't notice until a meeting is already missed. Defer it, then buy it
   without hesitating.
4. **Swift and Core Audio familiarity**, or willingness to acquire it. The only real skill
   gap, and the only thing that can genuinely stall the project.

**Permissions to handle in onboarding:** microphone, audio capture, calendar (EventKit),
notifications, and login-item registration. Five prompts. Worth a real first-run screen
that explains each one, because a half-granted set fails in confusing ways.

**One non-technical prerequisite:** recording consent. Two-party-consent jurisdictions
apply to individuals recording their own calls — personal use is not an exemption. A
one-click join-and-record makes it easier than ever to record without thinking about it,
which makes the habit of disclosing more important, not less.

---

## 11. Build order

Sequenced so the riskiest thing is answered first and every stage is independently useful.

**Stage 1 — capture spike.** Build AudioCap. Get two separate PCM streams (system + mic)
from a real Zoom call written to disk. No UI. This is the project's entire technical risk,
deliberately front-loaded. Give it one weekend; if it fails, revisit §1.

**Stage 2 — transcript pipeline.** WhisperKit over both channels, merged by timestamp into
one labelled `transcript.jsonl`. Menu-bar start/stop only. You now have a working local
transcriber, useful on its own.

**Stage 3 — the summary.** The Claude call, one template, markdown written to disk. This is
where it becomes the thing you wanted, and where you start using it daily.

**Stage 4 — the alert loop.** EventKit scanning and filtering, scheduled notifications with
actions, link extraction, Zoom deep-linking, login item. This is the stage that turns it
from a tool you run into one that runs itself — and it's the largest of the four. Budget
two weekends: one for scheduling and filtering, one for extraction and launching, which is
where the real-world mess lives.

**Stage 5 — refinement, driven by use.** More templates, automatic template selection,
audio-activity fallback, marker hotkey, transcript viewer, speaker naming, export.

Roughly **four to five weekends** to daily-driver quality.

---

## 12. Where the effort actually goes

Effort and risk are not the same thing here, and conflating them leads to planning the
wrong stage first. Three different kinds of hard show up in this project:

| Feature | Effort | Kind of hard | Can it kill the project? |
|---|---|---|---|
| Core Audio capture | **High** — 2–3 weekends cumulative | Unfamiliar API + real-time constraints | **Yes** |
| Meeting-link extraction | **High** — a day, then a long tail | Endless real-world variety | No |
| Alert state machine | Medium — a weekend, then corrections | Deceptively many edges | No |
| Templates / summary quality | **Unbounded** — never finished | Slow, subjective feedback loop | It decides whether you use the app |
| Transcription integration | Low — a weekend | Plumbing, one sharp edge | No |
| Everything else | Low — hours each | Ordinary | No |

### 1. Core Audio capture — the only thing that can stop you

Highest risk, and higher effort than the AudioCap starting point suggests. AudioCap shows
you the API dance; it is a demo, not a capture engine. What it doesn't hand you:

- **Real-time thread discipline.** The `AudioDeviceCreateIOProcIDWithBlock` callback is a
  real-time thread: no allocation, no locks, no ARC traffic. Getting samples out to the
  rest of the app needs a lock-free ring buffer. This is the part that works in a demo and
  glitches in a real meeting, which is also the worst way to find out.
- **Format conversion.** Taps deliver the device's native format — often 48 kHz float,
  multichannel. WhisperKit wants 16 kHz mono. Streaming resampling via `AVAudioConverter`,
  done correctly, is real work.
- **Two clocks.** The system tap and the microphone run on different hardware clocks and
  will drift apart over a long meeting. Timestamp alignment for merging the two channels is
  not free.
- **Core Audio's failure style.** Opaque `OSStatus` codes, no exceptions, and failures that
  manifest as silence rather than errors. Debugging is slow.

The one-weekend spike gets you recording. Trusting it daily is more like two to three
weekends of cumulative work spread across the project.

### 2. Meeting-link extraction — the grind

Not intellectually hard; just endless. Zoom links show up in `location`, in `notes`, as
bare URLs, wrapped in Outlook safelinks, with the passcode inline or on its own line. Meet
is in `event.url` sometimes and buried in the body other times. Teams links are enormous
and URL-encoded. An invite forwarded through three people accumulates cruft from all three.

This is the classic "90% in a day, the last 10% forever" feature. No amount of design
avoids it — only real invites do. Collect a dozen off your own calendar before writing the
parser, and expect to keep patching it for months.

### 3. The alert state machine — the one that gets underestimated

The notification API is easy. The state around it is not: events move and get cancelled
(cancel and re-register), recurring events need per-occurrence handling, the same meeting
appears on two calendars, the Mac was asleep, a recording is already running, meetings run
back-to-back, timezones change, you declined after the alert was scheduled.

Each edge is small. Together they're a real state machine, and the bugs are the kind you
discover a week later when a meeting quietly wasn't recorded.

### 4. Templates and summary quality — the one with no finish line

This is not engineering effort, it's iteration against a slow, subjective feedback loop.
You can only evaluate a template on real meetings, one meeting at a time, and "is this
summary good?" has no test suite. There is no done state.

It is also, since dropping typed notes, carrying the app's entire quality burden. This is
where the project either becomes something you use daily or becomes another notetaker whose
output you stop opening — and it's the one part no library shortcuts.

Front-load one genuinely good template rather than four mediocre ones.

### What's deceptively easy, and deceptively hard

**Looks hard, isn't:** transcription (WhisperKit is an `import`), notifications
(`UserNotifications` is straightforward), calendar access (EventKit removes an entire OAuth
subsystem), storage (files on disk), the Claude call (one HTTP request).

**Looks easy, isn't:** the real-time audio callback, and the alert state machine. Both look
like a day's work and aren't.

**The summary:** one feature can stall the project (capture), one will consume more hours
than any other (link extraction), one will be underestimated (the alert loop), and one
never ends (templates). Everything else is genuinely small — which is the reason a project
like this is feasible for one person at all.

---

## 13. Pitfalls worth knowing in advance

1. **Core Audio taps stall the project.** The most likely failure mode. Mitigated by
   starting there and by AudioCap existing. Hold yourself to the one-weekend box.
2. **Link extraction is messier than it looks.** Every calendar invite formats its join
   link differently, and the same platform varies by who sent it. This is regex-and-real-
   invites work, not design work — collect a dozen actual invites from your own calendar
   before writing the parser, and expect to keep patching it.
3. **A noisy alert gets trained away.** Fire on declined invites or a holiday calendar a
   few times and you'll dismiss every alert reflexively, at which point the feature is
   worse than nothing. Filtering (§7.2) deserves more care than it seems to.
4. **Whisper hallucination during silence.** Fluent, plausible, invented text — and with no
   typed notes to contradict it, it lands in the summary unchallenged. Test a low-talk
   meeting early. Arming rather than starting on click (§4) avoids the worst case.
5. **Generic summaries.** The predictable failure mode of a no-notes design: a weak
   template produces the same output as every other AI notetaker, and you stop reading
   them. The fix is template work, not model work.
6. **Silent misses.** An app that runs itself fails silently — a missed detection, a
   revoked permission, a crashed capture. Add a cheap daily check: if a calendar meeting
   had no recording, say so.

---

## 14. Open decisions

1. **How early should the alert fire?** T-1 is Granola-like and keeps it actionable. T-2 or
   T-5 gives room to prepare but drifts toward being another calendar reminder you ignore.
2. **Auto-join without a click, for meetings you always attend?** Tempting for recurring
   1:1s. Also the fastest way to launch Zoom into a room you didn't mean to enter. If
   built, restrict it to an explicit per-meeting opt-in.
3. **Summarise automatically on meeting end, or on demand?** Automatic fits the design and
   costs $0.10 a time. Probably automatic, with a setting.
4. **Marker hotkey: build it or not?** The only way to give the summariser a priority
   signal without typing. Worth trying once templates are stable enough to judge.
5. **How many templates to start?** One, used properly, beats four half-written.
