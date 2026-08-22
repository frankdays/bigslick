---
name: linkedin-connectsafely-search
description: >
  Use this skill whenever Frank asks to search LinkedIn, look up people or companies on LinkedIn,
  find prospects, research contacts, build ABM lists, do competitive intelligence, or take any
  action through the ConnectSafely MCP. Trigger on phrases like "search LinkedIn", "find people
  who", "look up [company/person] on LinkedIn", "who is", "build a list of", "find prospects",
  "research [company]", "check [person]'s profile", or any request that implies interacting with
  LinkedIn data. Always use this skill before making any ConnectSafely tool call — do not call
  ConnectSafely tools without first loading this skill.
---

# LinkedIn Search via ConnectSafely MCP

This skill governs how to use the ConnectSafely MCP to search and research on LinkedIn in a way
that is safe, human-paced, and tuned to Frank's four use cases: fractional/consulting prospecting,
ABM research, competitive intelligence, and market research.

---

## Core Principles

### 1. Never Run Parallel Searches
Always execute ConnectSafely tool calls sequentially, one at a time. Never fan out multiple
simultaneous calls. LinkedIn's detection systems flag inhuman request patterns — parallel calls
are the clearest signal of automation.

### 2. Pace Every Call
Pause between every ConnectSafely tool call. The target delay is 5 to 10 seconds. Do this even
when chaining "read-only" lookups like profile fetches. Use the Sleep pattern:
- After each tool call, note the delay before the next call
- Vary the delays slightly (don't always use exactly 7s — vary between 5 and 12s)
- Longer pauses (10-15s) before any action that touches connection/message functionality

### 3. Stop Before Writing or Sending
Apply judgment at each step:
- Safe to continue automatically: fetching profiles, paginating search results, pulling company data,
  checking relationship status, reading posts or comments
- Must stop and confirm: sending a connection request, sending a message, posting content, reacting
  to posts, endorsing skills, or any action that creates a visible LinkedIn event
Present results and ask Frank before any write action.

### 4. Use Targeted Queries
LinkedIn's algorithm and ConnectSafely's search both return better results with specific, narrow
queries. Prefer precise criteria over broad sweeps. See the Query Construction section below.

---

## Warm Path vs. Cold Path Logic

Before searching for anyone, check connection degree first. It changes the entire approach.

### 1st-Degree Connections (Warm Path)
Do not search for these people — you already have access to them. Instead:
1. Call `get-latest-posts` to see what they have been posting about recently
2. Call `fetch-profile` to check for role changes, new projects, or signals of need
3. Stop and assess: is there a genuine reason to reach out based on what you found?
4. If yes, draft a message that references something specific from their recent activity

Never cold-message a 1st-degree connection. The goal is to re-engage with context, not to pitch.

### 2nd-Degree Connections (Warm-ish Path)
These are reachable through mutual connections. Before any outreach:
1. Note the shared connection — it may be worth asking for an introduction instead
2. Check their recent posts for a natural conversation opener
3. Consider commenting on a post before sending a connection request (see Pre-Outreach Warming below)

### 3rd-Degree and Beyond (Cold Path)
Standard prospecting rules apply. Use the playbooks in the Use Case Playbooks section.
Warming through content engagement is especially important here before any connection attempt.

### Implementation
Always call `check-relationship` immediately after finding a person in search results, before
fetching their profile. Route to the appropriate path based on the result. Do not fetch profiles
for 1st-degree contacts from search — go directly to `get-latest-posts` instead.

---

## Session Start: Check Profile Visitors First

At the start of any prospecting session, before running any search, call `get-profile-visitors`.

Someone who viewed Frank's profile in the last 7 days is a higher-intent signal than anyone
surfaced by a keyword search. They already know who Frank is.

Workflow:
1. `get-profile-visitors` — pull recent visitors
2. Pause 7 to 10 seconds
3. For any visitor who matches the target profile (B2B SaaS, data infra, open source, relevant title):
   - `check-relationship` to know degree
   - `fetch-profile` to understand why they might have visited
   - Pause between each
4. Present the shortlist to Frank with context before any action

Only after working through profile visitors should you move on to active searching.

---

## Session Budgeting

LinkedIn's detection looks at daily and weekly totals, not just call-to-call intervals. Even
perfectly paced calls can trigger flags if the session volume is too high.

Hard limits per session:
- Profile fetches: no more than 30 to 40 in a single session
- Search queries: no more than 10 to 15 distinct searches per session
- Total tool calls: aim to stay under 60 per session across all types

If a session is going to require more than this (e.g., building a large ABM list), split it
across multiple sessions on different days. Flag this to Frank and plan accordingly.

Track a running count during the session and surface it when approaching limits:
"We've done 25 profile fetches this session — suggest we pause here and continue tomorrow."

Weekly awareness: connection requests are capped at 100 per week across all activity. If Frank
is also using ConnectSafely's engagement automation, that counts toward the same account limits.

---

## Tracking What Has Already Been Searched

To avoid re-fetching profiles across sessions and burning session budget on work already done,
maintain a simple log of research activity.

At the end of any significant session (5 or more profiles fetched), offer to:
1. Summarize who was researched, what was found, and what the recommended next step is
2. Save that summary to Google Drive (Frank has Drive connected) as a dated session log

Suggested filename format: `LinkedIn Research Log - YYYY-MM-DD.md`

Before starting research on a new batch of targets, ask Frank if there is an existing log to
check against — or search Drive for recent LinkedIn research logs to avoid duplicating work.

For ongoing ABM campaigns specifically, suggest maintaining a running tracker document in Drive
with columns for: Company, Contact Name, Date Researched, Connection Degree, Recent Signal,
Status, and Next Step.

---

## Pre-Outreach Warming

Do not send a connection request as the first touchpoint with a 3rd-degree prospect. LinkedIn's
2026 algorithm actively rewards engagement-based approaches and penalizes cold volume outreach.

Warming sequence before connecting:
1. `get-latest-posts` for the prospect — find a post worth engaging with
2. Pause 8 to 10 seconds
3. Stop and show Frank the post — ask if he wants to comment on it
4. If yes: draft a substantive comment (not generic — reference something specific in the post)
5. Frank reviews and approves the comment before it is posted
6. Wait at least 2 to 3 days after commenting before sending a connection request
7. When connecting, reference the comment or the shared topic in the request note

This sequence produces meaningfully higher acceptance rates and is the kind of activity LinkedIn
actively promotes. It also builds Frank's visibility with the prospect's followers.

Do not skip this for high-value targets. For lower-priority cold prospects, it is optional but
still recommended.

---

## Geographic and Timezone Awareness

LinkedIn's detection flags activity patterns that don't match normal business hours for the
account's home region. Frank is based in Arlington, MA (Eastern Time).

Timing guidelines:
- Run searches and fetch profiles between 8am and 7pm Eastern on weekdays
- Avoid heavy sessions on weekends — occasional weekend activity is fine but don't run full
  research sessions
- If targeting prospects in other timezones, still keep session timing within Frank's normal
  business hours — the account signal is what matters, not the prospect's timezone
- Do not schedule or trigger any write actions (connection requests, messages) outside of
  9am to 6pm Eastern

If Frank asks to run a session outside these windows, note the timing risk and suggest scheduling
it for the next business day instead.

---

## Pacing Implementation

When writing code or describing steps that call ConnectSafely tools, always include explicit
sleep/delay between calls:

```javascript
// Example pattern — adapt to the execution context
await connectSafelyTool('search-people', { query: '...' });
await sleep(7000);  // 7 second pause — vary this
await connectSafelyTool('fetch-profile', { profileId: '...' });
await sleep(9000);  // different delay each time
```

If executing tool calls directly (not in code), narrate the pause: "Pausing before the next
lookup..." and wait before proceeding.

---

## Use Case Playbooks

Read the relevant section below based on what Frank is trying to do.
For multi-use-case requests, chain the playbooks in this order: Prospect List → Profile Enrichment → Research.

### A. Prospecting for Fractional / Consulting Clients

Target profile: CMOs, VPs Marketing, Heads of Growth at B2B SaaS, data infrastructure, or
open source software companies, typically Series B through growth stage or post-acquisition.

Recommended search sequence:
1. `search-people` with title + industry filters
2. For each result: `check-relationship` to know 1st/2nd/3rd degree
3. `fetch-profile` for the most relevant 5 to 10 results (not all at once — pause between each)
4. Stop and present enriched list to Frank before any outreach action

Boolean search tips for ConnectSafely:
- Title: "CMO" OR "VP Marketing" OR "Head of Marketing" OR "Chief Marketing Officer"
- Exclude: NOT "VP of Product" NOT "intern" NOT "student"
- Combine with company size or funding stage when possible

### B. ABM Campaign Research

Target: Specific named accounts. Goal is to identify the right contacts and understand the
account's current priorities, messaging, and org structure.

Recommended sequence:
1. `get-company-details` for the target account
2. `search-people` filtered by company name + relevant seniority
3. `get-latest-posts` from key contacts to understand what they care about
4. `search-posts` with company name or relevant keywords to find recent content signals
5. Stop and summarize findings before Frank decides on outreach

Account signals to look for:
- Recent hires in marketing/growth roles (indicates scaling)
- Posts about specific pain points (data infrastructure, go-to-market challenges)
- Job postings at the company (signals investment areas)

### C. Competitive Intelligence

Target: Specific companies or categories of companies. Goal is to understand their positioning,
team, recent activity, and messaging.

Recommended sequence:
1. `get-company-details` for each competitor (one at a time with delays)
2. `search-posts` with company name to see recent content
3. `get-company-followers` or `get-connection-count` for size signals
4. `search-people` filtered to the target company to understand team structure

Things to capture:
- How they describe themselves (company description field)
- What topics they post about
- Key executive names and titles
- Employee count and recent growth indicators

### D. Market Research

Goal: Understand who is active around a topic, what conversations are happening, what pain
points practitioners are discussing.

Recommended sequence:
1. `search-posts` with topic keywords (e.g., "vector database" "real-time data" "PostgreSQL")
2. `get-all-post-comments` on high-engagement posts to surface active practitioners
3. `fetch-profile` on the most interesting commenters
4. `search-people` with relevant title + keyword combinations

---

## Query Construction

### People Search
- Keep keyword queries short: 2 to 4 distinctive terms
- Use Boolean: AND to require, OR to broaden, NOT to exclude
- Quotes for exact phrases: "database as a service" not database as a service
- Separate title from keywords when possible — don't put title in the keyword field if there is
  a dedicated title filter

### Company Search
- Search by name for known targets
- Search by industry + size for category research
- Use `get-company-details` after finding a company ID — it returns richer data than search alone

### Post Search
- Use industry jargon, not generic terms: "real-time database" beats "fast database"
- Try both the product category AND the pain point: "observability" AND "distributed systems"
- Recent posts (last 30 days) are most useful for ABM signal

---

## Output and Reporting

After each search or profile fetch, present results clearly:
- For people: name, title, company, connection degree, and one notable signal from their profile or posts
- For companies: name, size, industry, HQ, and one notable recent signal
- For posts: author, engagement level, key theme, and why it's relevant

Always tell Frank:
- How many results were returned vs. how many were reviewed
- What the next logical step would be
- Whether any action requires his confirmation before proceeding

---

## Safety Guardrails

These limits are based on LinkedIn's 2026 enforcement patterns and ConnectSafely's guidance:

- Connection requests: stay well under 100 per week total across all automation
- Messages: no bulk sends; each message should be individually reviewed
- Profile views: viewing many profiles rapidly is detectable; space them out
- Do not run the same search query repeatedly in a short window
- If a search returns an error or empty result, pause longer (15-20s) before retrying with a
  different query — do not retry the identical query immediately

If Frank's account shows any restriction signals (search results drying up, actions failing),
stop all activity and flag it immediately.

---

## Available ConnectSafely Tools (Key Subset)

Reference this list to pick the right tool for each step. For full tool documentation, consult
the ConnectSafely MCP tool descriptions directly.

| Tool | Use for |
|------|---------|
| `search-people` | Finding people by title, company, location, keyword |
| `search-people-v2` | Same but with auto-pagination (use for larger lists) |
| `fetch-profile` / `get-profile` | Enriching a specific person's profile |
| `check-relationship` | Knowing connection degree before outreach |
| `get-latest-posts` | What a specific person has been posting about |
| `search-posts` | Finding content by topic keyword |
| `get-all-post-comments` | Surface active practitioners from high-engagement posts |
| `get-company-details` | Full firmographic data on a company |
| `search-companies` | Finding companies by keyword or category |
| `get-profile-visitors` | Check who visited Frank's profile — run this first in any prospecting session |
| `get-account-status` | Checking account health before a heavy session |
| `get-connections` | Browsing existing network |
| `comment-on-post` | STOP — draft for Frank to review before posting |
| `send-connection-request` | STOP — confirm with Frank first |
| `conversations-send-message` | STOP — confirm with Frank first |
| `create-post` | STOP — confirm with Frank first |

---

## Before Starting Any Session

Run this checklist in order before any significant research session:

1. **Check the time** — confirm it is between 8am and 7pm Eastern on a weekday. If not, flag it.
2. **Check account health** — call `get-account-status`. Stop if any restriction signals appear.
3. **Check for existing research** — ask Frank if there is a Drive log to review, or search Drive
   for recent LinkedIn research logs, to avoid duplicating work already done.
4. **Check profile visitors** — call `get-profile-visitors` before running any searches. Work
   through high-intent visitors before moving to cold prospecting.
5. **Confirm the goal** — clarify the use case (prospecting, ABM, competitive intel, market
   research), expected depth, and whether any write actions are anticipated this session.

Only after completing this checklist should you begin searching or fetching profiles.
