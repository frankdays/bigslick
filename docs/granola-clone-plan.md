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

## 4. Capture — risks and mitigations

The one subsystem with real difficulty, and where to start. This section is longer than the
others because nearly every failure mode here is **silent**: the API returns `noErr`,
callbacks fire at a normal cadence, buffer pointers are valid, and every sample is zero.
Plan for diagnosis, not just implementation.

**Use Core Audio process taps** — `AudioHardwareCreateProcessTap` with a `CATapDescription`.
Not ScreenCaptureKit: taps are audio-only, scopeable to specific processes, and avoid
demanding the Screen Recording permission for an app that never touches the screen.

Start from [insidegui/AudioCap](https://github.com/insidegui/AudioCap) (the reference
implementation), with [AudioTee](https://github.com/makeusabrew/audiotee) as a second
reading and [Apple's docs](https://developer.apple.com/documentation/coreaudio/capturing-system-audio-with-core-audio-taps)
as the third. Documentation is sparse; **the SDK headers are the only authoritative source**
and web summaries are actively misleading on at least one parameter (§4.1).

### 4.1 Three setup foot-guns that all return `noErr`

Every one of these produces a working-looking tap that delivers pure silence.

**The `exclusive` flag is directional, not a lock.** This is the expensive one.
`exclusive = true` means *tap everything except the listed PIDs*; `exclusive = false` means
*tap only the listed PIDs*. Constructing with `init(stereoGlobalTapButExcludeProcesses:)`
and then setting `isExclusive = false` silently inverts the meaning — the tap fires, the
format reads correctly, callbacks arrive steadily, and every sample is zero. Read the
header.

**The aggregate device shape.** Attaching the tap as the main sub-device with an empty
sub-device list produces zero samples, silently. The correct shape is: a *real output
device* as `kAudioAggregateDeviceMainSubDeviceKey`, the tap attached via
`kAudioAggregateDeviceTapListKey`, and `kAudioAggregateDeviceTapAutoStartKey: true` — which
is mandatory, not optional.

**`AVAudioEngine` cannot be retargeted to a tap-backed aggregate device.** Setting
`kAudioOutputUnitProperty_CurrentDevice` returns `noErr` and the engine quietly goes on
reading the default input instead. Use `AudioDeviceCreateIOProcIDWithBlock` directly on the
aggregate. Its dispatch-queue parameter must be non-nil — passing nil silently fails to
register the callback.

**Teardown order matters** and reversing it leaves resources inconsistent:

```
AudioDeviceStop → AudioDeviceDestroyIOProcID
                → AudioHardwareDestroyAggregateDevice
                → AudioHardwareDestroyProcessTap
```

### 4.2 The all-zero buffer bug — the unsolved risk

**This is the most serious risk in the project, and it has no clean fix.**

There is an [open Apple Developer Forums report](https://developer.apple.com/forums/thread/825780),
unanswered by Apple, of taps that run correctly for minutes and then begin delivering
all-zero buffers while system audio remains plainly audible. The IOProc keeps firing at
normal cadence, frame counts and timestamps look right, buffer pointers are valid, and
every PCM sample is exactly `0.0`. It sometimes self-recovers and sometimes doesn't.

Suspected triggers, none confirmed: sample-rate renegotiation (44.1 ↔ 48 kHz) when another
app changes the output device; Bluetooth state changes where the device UID stays the same
(AirPods sleeping and waking); long session uptime. Reported more often on MacBook Air than
Pro.

**Why this is worse for a meeting recorder than for most apps:** all-zero buffers are
indistinguishable from legitimate silence, and a meeting is *full* of legitimate silence.
There is no HAL property that reports whether a tapped process is actually producing
non-zero audio — that was one of the five questions Apple didn't answer. So you cannot
directly detect the failure.

**Mitigations, in order of value:**

1. **Use the microphone channel as a liveness oracle.** This is the strongest available
   signal and it falls out of the two-stream design for free. If the mic has speech energy
   while the system tap has been exactly zero for N seconds during an active call, the tap
   is almost certainly broken — a real conversation does not have one party silent for a
   minute while you talk. Rebuild on that signal, not on zeros alone.
2. **Watch the triggers, not the symptom.** Subscribe to HAL property listeners for default
   output device changes, sample-rate changes, and device list changes, and proactively
   rebuild the tap when one fires. Cheaper and safer than reacting after the fact.
3. **Make rebuild cheap and safe.** Full teardown and rebuild (§4.1 order, then recreate) is
   the only known recovery. Because each channel is written to disk independently (§4.7), a
   mid-meeting rebuild costs a short gap in one channel, not a corrupted recording.
4. **Never rebuild blindly on silence alone.** Tearing down a healthy tap because a meeting
   went quiet trades a rare bug for a common one.
5. **Log every rebuild.** If this fires often on your hardware, you'll want to know before
   you trust the app with something important.

Budget real time for this. It is the difference between a demo and something you rely on.

### 4.3 Real-time thread discipline

The `AudioDeviceCreateIOProcIDWithBlock` callback runs on a real-time thread. Inside it you
must not allocate, take a lock, do file or network I/O, or make Objective-C/ARC calls that
might do any of those. **The Swift runtime itself is not real-time safe** — retain/release
traffic can allocate, so the callback body needs to be written with that in mind rather than
as ordinary Swift.

The standard structure: the IOProc copies samples into a **lock-free ring buffer** using
atomic read/write indices, and a normal-priority consumer thread drains it, resamples,
writes to disk, and feeds the ASR. Nothing else happens on the audio thread.

This is the part that works in a demo and glitches in a real meeting — and glitches are how
you discover you got it wrong, which is a bad way to find out. Get the ring buffer right
before building anything on top of it.

**Also:** zero the ring buffer on stop, or stale samples from the previous session leak into
the next one.

### 4.4 Format, channels, and clock drift

**Don't assume the buffer layout.** Taps deliver whatever the device is using — often 48 kHz
float, sometimes 44.1, and channel layout varies. Walk the `AudioBufferList` and handle
interleaved (channels ≥ 2 in `abl[0]`), separate-channel, and mono cases from what's
actually there rather than from what you expect.

**Resample to 16 kHz mono** for WhisperKit, streaming, via `AVAudioConverter`. Handle the
sample rate changing mid-session — see §4.2, since that's also a suspected trigger for the
zero-buffer bug.

**Clock drift is real but mostly harmless here.** The tap and the microphone run on
independent hardware clocks that are nominally identical and never exactly equal, so
timestamps slowly diverge over a long meeting. For A/V sync that's fatal; **for transcript
merging it is not.** You need the two channels aligned well enough to interleave utterances
in the right order — a tolerance measured in hundreds of milliseconds, not samples. Stamp
each buffer on arrival, merge by timestamp, and don't build drift compensation until you
observe an actual ordering problem. This is a genuine "the commercial version needs it, you
don't" saving.

### 4.5 Signing and permissions — a development-time gate

**Process taps require a stable signing identity to work at all.** Unsigned `xcodebuild`
output compiles fine but the TCC prompt never fires and capture silently fails. Run via
Xcode with a real Apple ID team selected, or `codesign` against a stable identifier. This
will cost you an afternoon if you hit it without knowing.

**`NSAudioCaptureUsageDescription` is its own TCC category**, separate from microphone
access. The key isn't in Xcode's Info.plist dropdown — type it manually.

**There is no public API to check or request audio-capture permission.** AudioCap does it
through private TCC framework calls, behind a build flag; without that, permission is
requested implicitly on the first capture attempt. For a personal app the private-API route
is fine — you're not shipping to the App Store.

**Testing the permission flow:** `tccutil reset SystemAudioCaptureRequests <bundle-id>`
clears granted/denied state so you can iterate on the prompt copy and the denial path.

### 4.6 Set the floor at macOS 14.4, and know the 26.x history

Taps arrived in 14.2, but deployment targets below **14.4** land in a different permission
category with different prompt copy. Pin 14.4 as the minimum for consistency.

Recent regressions worth knowing, since they show this API still moves:

- **macOS 26.0** broke capture from FaceTime and the Phone app, and broke capture whenever a
  secondary output device had a different sample rate from the default output. **Both fixed
  in 26.1.**
- Tahoe has a separate reported issue where system audio quality degrades over hours or days
  of uptime.

If you're on 26.x, be on 26.1 or later before concluding your code is at fault.

### 4.7 Defensive architecture

Design so that failures are survivable rather than trying to eliminate them:

- **Two independent streams, written independently.** The microphone path (`AVAudioEngine`)
  is ordinary, well-trodden, and reliable; the tap is the fragile one. Keep them fully
  separate all the way to disk so a tap failure or rebuild costs you their side of one
  meeting, never yours and never the file.
- **Write continuously.** Rolling audio chunks and append-only partial transcript. A crash
  at minute 50 costs seconds.
- **Instrument every boundary** — tap created, aggregate instantiated, IOProc registered,
  `AudioDeviceStart` returned, first callback arrived, frame count and channel layout,
  periodic peak level, ring buffer receiving non-zero peaks. When a layer says `noErr` and
  the output is silent, the bug is a parameter semantics misunderstanding, and boundary
  instrumentation is what tells you *which* layer. Build this before you need it.
- **Surface failure to yourself.** A silent recorder that stops recording is worse than no
  recorder. If a meeting produced a suspiciously empty channel, say so afterwards.

### 4.8 Browser-based meetings need a global tap

Google Meet in a browser doesn't play audio from the main browser process — it comes from a
renderer or helper process, and *which* one varies by browser and by meeting platform.
Per-process tapping is therefore unreliable for anything running in a tab.

Simplest robust answer: tap globally (`exclusive = true` with an empty exclusion list) and
accept that music and notifications land in the recording too. Refine to per-process only
for native apps like Zoom, where the process is stable and identifiable — and even then,
only if stray audio actually becomes a problem in the transcript.

### 4.9 Edge cases you can skip at personal scope

Headphone switching mid-call, Bluetooth dropping to 8/16 kHz HFP, mute-state detection,
simultaneous audio sessions, echo cancellation, multi-hour recordings. Each is real, each
would be mandatory commercially, and each can wait until it actually bites you. Skipping
them is most of why this project is weekends rather than months — but note that a few of
them (device changes, sample-rate changes) overlap with the §4.2 triggers, so the HAL
listeners you add there earn their keep twice.

### 4.10 What the spike must prove

Stage 1 is done when, from a real Zoom call:

1. Both streams write to disk as separate files
2. Peak levels are non-zero on both, verified over several minutes
3. The tap survives a deliberate output-device change (plug in headphones mid-call)
4. The tap survives a sample-rate change
5. A forced teardown/rebuild mid-recording produces a gap, not a corruption
6. Boundary instrumentation prints something useful at every stage

Items 3–5 are the ones that separate "it worked once" from "I can build on this."

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

**Stage 0 — the half-day reproduction test.** Before building anything, try to trigger the
all-zero buffer bug (§4.2) on *your* Mac. Run AudioCap unmodified and deliberately provoke
the suspected causes: change the output device mid-capture, switch sample rate, connect and
disconnect AirPods, then leave it running for an hour. Watch for the buffer going silent
while audio is still audible.

This is the highest-leverage half-day in the plan, because **that one unknown dominates the
whole estimate's variance.** Can't reproduce it in a deliberate hour of trying → the long
tail mostly evaporates and capture is ordinary engineering. Reproduce it in ten minutes →
you know to budget the rebuild machinery up front, and the case for forking anarlog (§1)
gets considerably stronger, since its authors have presumably already paid this cost.

**Stage 1 — capture engine.** Two separate PCM streams from a real Zoom call, written to
disk, meeting the §4.10 exit criteria. This is the project's entire technical risk,
deliberately front-loaded. It splits into three milestones with very different confidence:

| Milestone | Focused time | Confidence |
|---|---|---|
| First recording — tap creates, callbacks fire, non-zero samples on both channels | 1–2 days | **High.** The three silent foot-guns (§4.1) are now documented; blind, each could have eaten a weekend on its own |
| Robust capture — lock-free ring buffer, streaming resample to 16 kHz mono, HAL listeners, teardown/rebuild, boundary instrumentation | 1–2 weekends | Medium. Real engineering, but no unknowns |
| Trusted daily — survives whatever your hardware actually does over weeks | Unbounded tail | **Low, and not fully in your control.** §4.2 is an unfixed Apple bug |

If the first milestone isn't reached in a weekend, that's the signal to revisit §1 rather
than to push harder.

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

Roughly **five to seven weekends** to daily-driver quality — revised up from the earlier
estimate, entirely because of what §4 turned up. The research did not add work so much as
relocate it: it shortened the "get it recording" phase by naming the silent foot-guns in
advance, and lengthened the "trust it" phase by revealing a bug that has no clean fix.

Worth being clear about the shape of that number: stages 2–5 are predictable, and if
anything the estimates there are slightly conservative. Essentially all the variance sits
in stage 1, and stage 0 is how you resolve most of it for half a day's work.

---

## 12. Where the effort actually goes

Effort and risk are not the same thing here, and conflating them leads to planning the
wrong stage first. Three different kinds of hard show up in this project:

| Feature | Effort | Kind of hard | Can it kill the project? |
|---|---|---|---|
| Core Audio capture | **High** — 2–3 weekends, plus an open-ended tail | Unfamiliar API, real-time constraints, and one unfixed OS bug | **Yes** |
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

## 13. Cutting the build down

The full plan is five to seven weekends. Roughly half of that can come out — and a
surprising amount of it costs nothing at all, because the no-notes, no-during-meeting-UI
decision already removed the reasons those parts were complicated.

### Free — no functionality lost

**Batch-transcribe after the meeting instead of streaming during it.** The largest free win.
Nothing in this app shows a live transcript, so there is no reason to produce one. Dump raw
audio to disk during the call and run WhisperKit over the file afterwards — a one-hour
recording takes a few minutes on Apple Silicon, and the summary isn't wanted until the
meeting is over anyway.

This deletes an entire class of difficulty: the lock-free ring buffer, low-latency
constraints, streaming resampling, and live channel merging all go away. The audio callback
still can't block, but a generous buffer and a plain file write is a far lower bar than
real-time streaming — and it removes the "works in a demo, glitches in a real meeting"
failure mode described in §4.3. **Saves roughly a weekend and the hardest debugging in the
project.**

**Hardcode one prompt instead of building a template system.** No selection logic, no
per-meeting-type routing, no UI. Put the prompt in a text file and edit it. Template
infrastructure is worth building only once you know what your templates should say, which
you won't for a month. **Saves several days.**

**Skip the library UI and search.** The notes are markdown in a folder. Finder opens it,
`rg` searches it, your editor reads it, Spotlight indexes it. A list view is a nicety, not a
feature. **Saves several days.**

### Real tradeoffs — you give something up

**Alert, but no auto-join.** Keep the pre-meeting notification with Record / Skip, and drop
the Join button. This removes meeting-link extraction — the endless one from §12 — along
with Zoom deep-linking and the whole per-platform parsing tail. You still get the thing that
actually matters (never forgetting to record), and you join the call the way you already do.
**Saves a weekend plus an open-ended tail, for one click you were making anyway.** Probably
the best value on this list.

**No alert at all — just a global hotkey.** Drops EventKit scheduling, the alert state
machine, notification permissions, and the login item on top of the above. Cost: you have to
remember. **Saves two weekends**, but "remember to start it" is exactly the habit that
software is supposed to replace, so this one genuinely degrades the product.

**Microphone only, no system audio.** The nuclear option: `AVAudioEngine` alone is ordinary,
well-documented, low-risk code, and it deletes §4 entirely — the taps, the foot-guns, the
all-zero bug, the whole highest-risk subsystem. **Saves 3–5 days plus the unbounded tail and
the project's only real failure mode.**

The cost is severe though: with headphones on you capture only your own voice, which is
useless. It works only with speakers on, at worse quality, with echo, and no "me vs. them"
channel separation. Genuinely good for in-person meetings; poor for the call recording this
app is mostly for. Worth knowing as the floor, not as a recommendation.

**Buy the capture.** [Recall.ai's Desktop Recording SDK](https://www.recall.ai/product/desktop-recording-sdk)
handles all of §4 — both streams, device changes, mute detection — at $0.50/recording hour,
about $10/month at 20 hours. Deletes the project's hardest part outright.

Be honest about where that lands, though: paying $10/month for capture, on top of the API
cost, to avoid building the one part that makes this yours, invites the obvious question of
why not pay $18 for Granola and skip the whole thing. Reasonable as a temporary bridge to
get running; poor as a destination.

### What is *not* a shortcut

**Switching to ScreenCaptureKit.** Tempting — it's older and more widely used — but the
consensus for audio-only capture still favours Core Audio taps, and ScreenCaptureKit adds
the broader Screen & System Audio Recording permission while not clearly reducing the
implementation difficulty. It trades a known set of problems for a different one, at no
saving.

### The recommended fast path

Take every free simplification, plus alert-without-auto-join:

| | Full plan | Fast path |
|---|---|---|
| Capture | Streaming, real-time-safe | Batch to disk |
| Transcription | Live, merged | After the meeting |
| Summary | Template system | One hardcoded prompt |
| Alert | Alert + auto-join Zoom | Alert + Record |
| Library | List view, search | A folder |
| **Total** | **5–7 weekends** | **~3 weekends** |

You lose one click before each meeting and a list view. Everything that made the app worth
building survives — and stage 0 (§11) still comes first either way, because the capture
risk is the one thing none of these cuts removes.

### And the largest lever remains §1

Forking [anarlog](https://github.com/fastrepl/anarlog) takes the whole thing to an evening.
Three weekends is the price of owning the code; if that ownership isn't worth three
weekends to you, that is a completely legitimate answer, and stage 0 is a cheap way to find
out before committing.

---

## 14. Pitfalls worth knowing in advance

1. **Core Audio taps stall the project.** The most likely failure mode, and §4 is the
   detailed register. The headline risks: three setup parameters that fail silently with
   `noErr`, and an Apple-unconfirmed bug where a healthy tap starts returning all-zero
   buffers indistinguishable from real silence. Mitigated by the mic-as-liveness-oracle
   check (§4.2) and by AudioCap existing. Hold yourself to the one-weekend spike box.
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

## 15. Open decisions

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
