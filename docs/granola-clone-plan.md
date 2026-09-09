# Granola Clone — Desktop Application Build Plan

Status: planning document. No code written yet.
Date: 2026-09-09.

> **Repo note:** this document is scoped work for a *separate* product, not for Big Slick.
> Big Slick's architecture rules (vendored `upstream/`, curation-first, no new authoring)
> do not apply to it. If this project proceeds past planning, it wants its own repository.

---

## 1. What you are actually cloning

Granola is not "Whisper plus a summariser". It is six subsystems, and the difficulty is
concentrated in exactly one of them. Decomposed:

| # | Subsystem | Difficulty | Why |
|---|-----------|-----------|-----|
| 1 | **Capture** — record both sides of a call without joining as a bot | **Hard** | Native OS audio APIs, per-platform, permission-gated, signing-gated |
| 2 | **Transcription** — streaming ASR + speaker attribution | Medium | Solved problem; the choice is cost/privacy, not feasibility |
| 3 | **Enhancement** — merge sparse human notes + full transcript into a clean note | Easy | One well-designed LLM call. This is the *perceived* magic and the *cheapest* part |
| 4 | **Library** — local-first store, calendar binding, search, folders, sharing | Medium | Ordinary app engineering, but it is most of the code |
| 5 | **Distribution** — signed, notarised, auto-updating desktop binaries | Medium | No technical risk, but hard cost/time gates (see §9) |
| 6 | **Downstream** — push notes into Slack / CRM / email / docs | Easy | And this is where *you* already have an unfair advantage (see §8) |

The strategic read: **#1 is the moat, #3 is the demo.** Most Granola clones fail at #1 and
most clone *plans* over-invest in #3.

The "no bot in the meeting" property is the whole product thesis. It is why Granola feels
native and why bot-based competitors feel intrusive. Preserving it means capture must be
solved locally, on-device — you cannot outsource it to a meeting-platform API.

---

## 2. Reference architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Desktop shell (Electron or Tauri)                           │
│  ├── Notepad UI (TipTap/ProseMirror) — user types sparse notes│
│  ├── Meeting list / library / search                          │
│  └── Settings, permissions onboarding                         │
└───────────────┬──────────────────────────────────────────────┘
                │ IPC
┌───────────────▼──────────────────────────────────────────────┐
│  Native capture helper  (Swift on macOS / C++ on Windows)     │
│  ├── System audio  → Core Audio process tap (macOS 14.2+)     │
│  ├── Microphone    → AVAudioEngine / WASAPI                   │
│  └── Emits 2 separate PCM streams (them / me)                 │
└───────────────┬──────────────────────────────────────────────┘
                │ 16kHz mono PCM x2
┌───────────────▼──────────────────────────────────────────────┐
│  ASR worker  (local model, or cloud streaming socket)         │
│  └── Timestamped, channel-labelled transcript segments        │
└───────────────┬──────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│  Local store — SQLite (+ sqlite-vec for embeddings)           │
│  meetings, transcript_segments, notes, templates, entities    │
└───────────────┬──────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│  Enhancement + chat  → Claude API (claude-opus-5)             │
└───────────────┬──────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│  Sync + share backend (Postgres + object storage + auth)      │
│  Integrations: Slack, HubSpot, Gmail, Drive, Notion           │
└──────────────────────────────────────────────────────────────┘
```

**Shell choice:** Electron. Tauri produces a smaller binary, but you will be writing a
native sidecar for capture either way, and Electron's ecosystem (auto-update, crash
reporting, editor components) is materially deeper. The binary-size argument loses to the
schedule argument here. Granola itself is Electron.

**Sidecar boundary matters:** keep capture in a separate process, not in-process native
modules. Audio drivers crash. A crashed helper should lose one meeting's tail, not the
user's unsaved notes.

---

## 3. The hard part: audio capture

### macOS

Two viable APIs, and the right choice changed recently:

- **Core Audio process taps** (`AudioHardwareCreateProcessTap` + `CATapDescription`),
  macOS 14.2+. This is the correct path. It is audio-only, it can be scoped to *specific
  processes* (tap Zoom and Meet, leave Spotify alone), and it avoids the Screen Recording
  permission prompt and menu-bar recording indicator that make an audio product feel like
  spyware.
- **ScreenCaptureKit** (macOS 13+). Fallback for 13.x only. Audio capture is bolted onto
  screen-recording infrastructure, so it demands the Screen Recording TCC permission for a
  product that never touches the screen. Bad conversion at onboarding.
- **Virtual audio driver** (BlackHole-style). Avoid. DriverKit signing, install friction,
  and it hijacks the user's default output device.

Mic is separate (`AVAudioEngine`, `NSMicrophoneUsageDescription`).

**The two-stream trick:** capture system audio and microphone as *separate* streams rather
than a pre-mixed one. You get "me vs. them" attribution for free, with zero diarization
cost and perfect accuracy on the most important speaker boundary. Diarization within the
remote stream is then a nice-to-have, not a dependency. Do this from day one — retrofitting
it means re-plumbing the whole pipeline.

### Windows

WASAPI loopback (`IAudioClient` with `AUDCLNT_STREAMFLAGS_LOOPBACK`). For per-process
capture, `ActivateAudioInterfaceAsync` with `AUDIOCLIENT_ACTIVATION_PARAMS` (Windows 10
20H1+). Same two-stream design.

### Edge cases that will eat weeks

These are not exotic; they are every meeting. Budget for them explicitly:

- User switches headphones mid-call (device change → stream teardown/rebuild)
- User mutes — detecting mute state so the note does not claim silence was speech
- Bluetooth switches to HFP and samples drop to 8/16kHz mono, tanking accuracy
- Sleep/wake, screen lock, and battery-saver throttling mid-recording
- Multiple audio sessions (a call plus a YouTube tab)
- Permission revoked between sessions
- The 3-hour meeting that must not hold a 3-hour buffer in RAM

**Buy-vs-build flag:** [Recall.ai's Desktop Recording SDK](https://www.recall.ai/product/desktop-recording-sdk)
handles exactly this list — mac + Windows, system + mic audio, mute detection, device
switching — at $0.50/recording hour. That is expensive as permanent COGS but cheap as a
way to reach a working product before committing to native work. See §9.

---

## 4. Transcription

Three options, and the choice is a business decision, not a technical one:

| Path | Cost/meeting-hour | Latency | Privacy story | Accuracy |
|------|------------------|---------|---------------|----------|
| **Local** (whisper.cpp / WhisperKit / Parakeet TDT via MLX) | **$0** | Good on Apple Silicon | "Audio never leaves your Mac" — strongest possible | Near-cloud on clean audio; degrades on accents/crosstalk |
| **Deepgram Nova-3 streaming** | ~$0.46 + ~$0.12 diarization ≈ **$0.58** | Excellent | Weakest | Excellent |
| **AssemblyAI streaming** | ~$0.45 + ~$0.12 diarization ≈ **$0.57** | Excellent | Weakest | Excellent |

Recommendation: **local by default, cloud as an opt-in accuracy upgrade.** Three reasons.
It makes gross margin structural rather than a per-meeting tax (§10). It gives you the one
marketing claim incumbents cannot copy without re-architecting. And on Apple Silicon,
whisper.cpp on Metal runs large-v3 at roughly 2–3× realtime, which is comfortably enough
headroom for live transcription.

Caveat to design around: Whisper hallucinates during silence, which is a live-transcription
liability specifically. Gate on voice activity detection (VAD) before feeding segments to
the model, and never render a segment whose audio was below the VAD threshold. Parakeet TDT
is faster and purpose-built for low-latency English but ranks lower on general accuracy and
is English-only — reasonable as the "fast mode", not as the only engine.

Windows local inference is materially worse than Apple Silicon (no unified memory, variable
GPU). Plan for Windows to lean cloud even if macOS is local.

---

## 5. The enhancement pass

This is one Claude call, and it is the least risky part of the build. Shape it as:

```
system: <template — "sales call", "1:1", "standup", "user interview">
input:  - the user's sparse typed notes (high signal, low volume)
        - the full transcript with speaker labels and timestamps
        - meeting metadata (title, attendees, calendar description)
output: structured note — summary, decisions, action items w/ owners, open questions
```

Model: `claude-opus-5` ($5/$25 per MTok, 1M context). A one-hour meeting is roughly
9,000–10,000 words ≈ 12–13K input tokens, with ~1.5K tokens out. That is **~$0.10 per
meeting** — an order of magnitude below the transcription cost on the cloud path, and
therefore not worth optimising first. Use adaptive thinking (`thinking: {type: "adaptive"}`)
and stream the response.

Design notes that matter more than the prompt:

- **User notes are the anchor, not an addendum.** Granola's insight is that what the user
  bothered to type marks what mattered. The transcript is context for expanding those
  anchors, not the primary source. A summariser that ignores the typed notes is a
  commodity; one that treats them as an outline is the product.
- **Prompt caching:** cache the system prompt + template prefix; the transcript is volatile
  and goes after the last cache breakpoint. Verify with `usage.cache_read_input_tokens`.
- **Templates are the retention surface.** Per-meeting-type output structures are what make
  users configure the tool, and configured tools do not churn.
- **Enhancement must be re-runnable.** Users will change templates and expect old meetings
  to re-render. Store the raw transcript forever; treat the enhanced note as derived.

For chat-with-your-meetings (§7), the same store plus embeddings; `claude-opus-5` for the
answer, retrieval over `sqlite-vec` locally or `pgvector` server-side.

---

## 6. Data model and sync

Local-first, SQLite as source of truth on device:

```
meetings(id, calendar_event_id, title, started_at, ended_at, template_id, source)
attendees(meeting_id, name, email, role)
transcript_segments(meeting_id, channel[me|them|spk_n], t_start, t_end, text, confidence)
notes(meeting_id, raw_markdown, enhanced_markdown, enhanced_at, model, template_id)
action_items(meeting_id, text, owner, due, status, pushed_to)
embeddings(segment_id, vector)
```

Sync is a v2 problem, but the *decision* is v1: if two devices can edit the same note, you
need CRDTs (Automerge/Yjs) and you should adopt them at the editor layer immediately —
retrofitting collaborative editing onto plain-text notes is a rewrite. If notes are
single-writer, last-write-wins over a plain REST sync is fine and much cheaper. **Pick
single-writer for v1.** Multiplayer editing is not why anyone buys a notetaker.

Retention: raw audio is the largest and most sensitive asset. Default to discarding audio
once transcription completes, keeping only the transcript. It shrinks storage costs,
shrinks breach blast radius, and is a defensible privacy claim. Make retention explicit and
user-configurable.

---

## 7. Calendar binding and meeting detection

Two signals, combined:

1. **Calendar** — Google Calendar API and Microsoft Graph. Gives you the title, attendees,
   agenda, and conferencing link before the meeting starts. This is what makes notes
   auto-file themselves, which is most of the "it just works" feeling.
2. **Audio activity** — a call app holding an audio session, or a known process
   (zoom.us, Teams, a browser tab on meet.google.com) producing output.

Calendar alone over-triggers (declined meetings, holds). Audio alone under-attributes (no
title, no attendees). Together they are reliable: prompt to record when both fire, offer a
one-tap manual start when only audio fires.

Attendee list from calendar also gives you free speaker-name candidates to map onto
diarized channels — much better than "Speaker 2".

---

## 8. Where your existing toolset is an actual advantage

You already have live, authenticated integrations that Granola charges for or does not have:

- **Slack** — post the note to the deal channel
- **HubSpot** — write the meeting summary to the deal/contact record, create tasks from
  action items. This is the single highest-value B2B integration in the category
- **Gmail** — draft the follow-up email from the action items
- **Google Calendar / Drive** — binding and archival
- **LinkedIn (ConnectSafely)** — enrich unknown attendees before the call

And the strategic one: **Big Slick is 247 marketing skills that all need company context,
and meeting transcripts are the richest source of company context that exists.** A
notetaker that feeds `core/clients/<client>/` packs closes the loop that
`BUILD-BIGSLICK.md` currently asks the user to fill in by hand via `company-onboarding` —
a skill that, per `CLAUDE.md`, has never been executed end to end.

That is a genuinely differentiated wedge: not "another AI notetaker", but "the notetaker
that makes your marketing skills know your customers". Worth deciding early whether that is
the product or a later integration, because it changes the ICP.

---

## 9. Build vs. buy

| Component | Recommendation |
|-----------|---------------|
| Audio capture | **Buy first (Recall.ai Desktop SDK), build second.** Ship in weeks, replace when unit economics demand it. The $0.50/hr is a real tax; treat it as a deliberate loan against schedule, with a planned repayment |
| Transcription | **Build (local models).** This is where the margin lives, and whisper.cpp/WhisperKit make it a packaging problem, not an ML problem |
| Enhancement | **Build.** It is one API call; buying it makes no sense |
| Auth / billing | **Buy** (Clerk or WorkOS; Stripe) |
| Sync backend | **Buy managed** (Supabase or Neon + R2/S3) |
| Auto-update | **Buy** (electron-updater / Sparkle) |
| Crash + analytics | **Buy** (Sentry, PostHog) |

The general rule: buy everything that is not capture, local ASR, or the note itself.

---

## 10. Unit economics

Per meeting-hour, at the two extremes:

| Line item | Fully cloud | Local-first |
|-----------|------------|-------------|
| Recording (Recall.ai) | $0.50 | $0 (native capture) |
| Transcription | $0.15–0.58 | $0 |
| Enhancement (`claude-opus-5`, ~13K in / 1.5K out) | ~$0.10 | ~$0.10 |
| **Total** | **~$0.75–1.18** | **~$0.10** |

A heavy user does ~20 meeting-hours/month. That is **$15–24/user/month of COGS on the cloud
path** — against category pricing around $18–20/user/month. The cloud path has *negative*
gross margin on power users; the local path runs ~90%+.

This is the single most important number in the plan. It says: cloud capture and cloud ASR
are acceptable to *launch* on and unacceptable to *scale* on. Build the native capture and
local ASR migration into the roadmap as a funded milestone, not as a someday.

---

## 11. Phasing

**P0 — Prove the magic (4–6 weeks).** macOS only. Recall.ai SDK for capture, cloud ASR,
Claude enhancement, local SQLite, no accounts, no sync. One template. Goal: the moment
where sparse notes become a good document. If that moment does not land, nothing else
matters.

**P1 — Make it a daily tool (6–8 weeks).** Google Calendar binding + auto-detection.
Meeting library, search, folders. Multiple templates. Local ASR path behind a flag. Signed
+ notarised builds, auto-update. Onboarding for the permission prompts.

**P2 — Make it defensible (8–10 weeks).** Native capture replacing Recall.ai on macOS.
Local ASR as default. Accounts, sync, sharing links. Slack + HubSpot + Gmail push. Windows
capture.

**P3 — Make it sticky.** Chat over meeting history (RAG). Cross-meeting entity tracking
(people, accounts, commitments). Team/shared workspaces. An MCP server so Claude can query
the corpus. The Big Slick context-pack loop (§8).

Rough total to a defensible v1: **5–7 months** for a small team, assuming capture is bought
in P0.

---

## 12. Gap analysis — what is missing from your toolset

You have: Claude API access, GitHub, Google Calendar/Gmail/Drive, Slack, HubSpot, LinkedIn,
and Granola itself (as a *consumer* — useful for studying the data model, not for building).

You have **none** of the following, and each is a hard dependency:

### A. Must acquire — capture and ASR (the critical path)

1. **Native audio capture code.** Nothing in your toolset touches this. Swift
   (Core Audio process taps) + C++ (WASAPI). This is the one part that cannot be
   delegated to an API, an MCP server, or a skill. Either hire/learn it or buy Recall.ai.
2. **A speech-to-text provider or local model pipeline.** No ASR anywhere in your stack.
   Either a Deepgram/AssemblyAI account, or whisper.cpp/WhisperKit weights plus the
   packaging work to ship inference inside a desktop app.
3. **Speaker diarization**, if you go beyond the two-stream trick — pyannote (self-hosted,
   gated model downloads) or the cloud add-on.
4. **A corpus of real recorded meetings for evaluation.** You have no eval set — the same
   gap `CLAUDE.md` already flags for Big Slick's skills. Note quality is unmeasurable
   without ~50 recorded meetings with human-written reference notes. Start collecting from
   day one; this is the slowest-to-acquire asset on the list and cannot be bought.

### B. Must acquire — shipping a desktop app

5. **Apple Developer Program** — $99/yr, plus a Developer ID certificate and a notarisation
   pipeline. Without it macOS refuses to launch the app.
6. **Windows code-signing certificate** — OV/EV, roughly $200–500/yr. Without it,
   SmartScreen suppresses downloads.
7. **Auto-update infrastructure** — electron-updater or Sparkle plus a release feed host.
8. **Crash reporting and product analytics** — Sentry, PostHog. Desktop crashes are
   invisible without them.

### C. Must acquire — backend and accounts

9. **Your own OAuth app registrations.** Critical distinction: your Google Calendar/Gmail
   access here is *Frank's own account via MCP*. A shipped product needs its own Google
   Cloud project and Microsoft Entra app registration, with consent screens and
   verification. Calendar and `gmail.send` are **sensitive** scopes — Google verification
   required, no security assessment. `gmail.readonly`/`gmail.modify` are **restricted** —
   these add an annual CASA third-party security assessment (self-serve path roughly
   $540–1,000 as of 2026). **Design the product to need only sensitive scopes.** Reading
   mailboxes is not worth the compliance tail.
10. **An Anthropic API key with a billing account.** A Claude Code subscription is not a
    production inference budget. Separate key, separate spend limits, separate monitoring.
11. **Hosting, database, object storage** — none present. Supabase/Neon + Fly/Render + R2/S3.
12. **Auth and billing** — Clerk or WorkOS, and Stripe. None present.
13. **Vector storage / embeddings** for chat-over-meetings — `sqlite-vec` locally,
    `pgvector` server-side, plus an embedding provider.

### D. Must acquire — legal and trust

14. **Recording-consent handling.** Two-party consent jurisdictions make silent recording
    unlawful. You need in-product consent UX, not just a ToS clause. This is a product
    requirement, not a legal footnote.
15. **Privacy policy, DPA, sub-processor list, retention policy.** Enterprise buyers ask on
    the first call. GDPR posture required for any EU user.
16. **SOC 2** eventually, for any deal above SMB.

### What you notably do *not* need

Zoom/Meet/Teams meeting-platform APIs. The whole point of the desktop-capture approach is
that it works on any call, in any app, including in-person conversations — without
per-platform bot integrations. Skipping those APIs is a feature.

---

## 13. Top risks

1. **Capture engineering is underestimated.** It always is. The edge-case list in §3 is the
   real schedule, not the happy path. Mitigation: buy it in P0, build it with eyes open.
2. **Cloud unit economics quietly go negative** (§10) if local ASR slips. Mitigation: treat
   the local-ASR milestone as a funded deliverable with a date.
3. **The category is crowded and well-funded.** Granola, Otter, Fireflies, Fathom, plus
   first-party notetakers now shipping inside Zoom, Meet, and Teams for free. A generic
   clone has no wedge. Mitigation: the marketing-context loop in §8 is the differentiated
   angle available to *you specifically* — commit to it or find another.
4. **Trust is the buying criterion**, not accuracy. An always-listening app on a work
   laptop is a security review. Local-first processing is the strongest answer, which is a
   second reason it is an architectural decision rather than an optimisation.
5. **Note quality is unmeasurable without an eval set** (§12.A.4), so quality regressions
   ship silently. Same failure mode `CLAUDE.md` records for Big Slick's 247 skills.

---

## 14. First three decisions

Everything else follows from these:

1. **Buy or build capture for P0?** Determines whether you have a demo in 4 weeks or 4 months.
2. **Local-first or cloud-first ASR?** Determines gross margin, privacy positioning, and
   whether Windows is a first-class target.
3. **Generic notetaker, or the marketing-context notetaker (§8)?** Determines ICP, pricing,
   and whether Big Slick and this product are one company or two.
