---
name: client-onboarding
description: "Run Big Slick across a book of clients rather than one business. Use when the user is a consultant, agency, fractional CMO or freelancer serving several companies, or says \"onboard a new client\", \"add a client\", \"switch to <client>\", \"which client am I on\", \"list my clients\", or \"archive this engagement\". Covers the roster, per-client isolation, safe switching, and the engagement lifecycle. For setting up one business you work in full time, use company-onboarding instead."
---

# Client onboarding

For people who run marketing for **more than one company**. The interview itself is
not repeated here — `company-onboarding` owns that, and you will run it once per
client. What this skill owns is everything that only becomes a problem at two
clients or more: keeping them apart, knowing which one is live, and not leaking
one client's numbers into another's plan.

If the user works in-house at a single company, stop and use `company-onboarding`.

## The one failure that matters

Cross-client contamination. Presenting Client A's positioning, competitor set, or
funnel baseline in Client B's work is the mistake that ends engagements, and it
happens silently because a stale active pack looks exactly like a correct one.

Two rules prevent nearly all of it:

1. **Name the client before doing the work.** Every substantive answer in a session
   opens with `Working from <client>'s context pack.` If you cannot say which
   client you are on, you are not ready to answer.
2. **Never carry a number between packs.** Benchmarks, win rates, CAC, pricing —
   if it came from another client's pack, it does not enter this one. Anonymised
   *method* travels; data does not.

## 1. Build the roster

One folder per client under `core/clients/`, plus `_template` and the `hansel-ai`
sample. Use a short, lowercase, stable slug — it appears in paths, in the generated
skill name, and in every switch command.

```bash
ls core/clients                       # who exists
readlink core/clients/_active         # who is live right now
```

Answer "list my clients" from that directory, never from memory. A pack that exists
on disk is a client; one you merely remember is not.

## 2. Onboard each client

Run `company-onboarding` per client. Everything there applies unchanged: pick a
depth, write the ten-file pack to `core/clients/<client>/`, run Phases B–D.

Depth is a per-client decision, not a house style. A retainer client earns Standard
or Full; a two-week project does not. Say what each costs and let the user choose
per engagement.

Record the commercial frame in the client's `product-marketing.md` — scope, day
rate or retainer, cadence, term. It is not marketing data, but it decides what work
is in bounds, and no other file holds it.

## 3. Switch clients safely

```bash
bash scripts/activate_client.sh <client>
```

**Read the output.** It reports a line that matters more here than anywhere else:

> `home-global: ~/.claude/product-marketing.md  (replaced <previous>'s)`

Switching **overwrites** the home-global copy with the new client's context. That
file is what 18 skills read when Claude runs from the home directory, so the
previous client's context is now gone from that path — and nothing warns you later.
Say out loud which client was displaced.

Because of that clobber, the shared file is the wrong mechanism for a book of
clients. The right one is per-client skills.

## 4. Give every client their own context skill

```bash
python3 scripts/make_context_plugin.py <client>
```

This is the only route that works in the desktop app and from any folder, and —
critically here — each client gets a **separate installable**. Enable one, disable
the others. That is real isolation: no shared file to clobber, no ambiguity about
who is loaded.

Regenerate after any edit to a pack. Nothing watches for changes, so an edited pack
and a stale installed skill will disagree, and the skill wins.

## 5. Verify before every engagement session

Ask something only this client's pack can answer — "who do we lose deals to?" A
correct answer means you are on the right client. A generic answer, or a request to
describe the business, means the wrong pack is loaded or none is.

Do this at the **start** of a working session, not after producing a deliverable.
The cost of checking is one question; the cost of not checking is work built on the
wrong company.

## 6. Close an engagement

When an engagement ends, the pack does not evaporate — it becomes a liability if it
stays live and a reference if it is archived deliberately.

- Switch the active client away first, so nothing is pointed at a closed account.
- Uninstall or disable that client's context skill.
- Keep the pack folder. It is the user's own record of the engagement, and a
  returning client is far cheaper to re-onboard from it than from scratch.
- Client packs are gitignored except `_template` and `hansel-ai`. Never commit one,
  and never let one into a release — `package_release.sh` aborts if it finds one,
  and that guard exists because this data is a client's confidential positioning
  and funnel numbers.

## What may be reused across clients

| Reuse | Never reuse |
|---|---|
| Method, frameworks, question sets | Any number from another client's pack |
| Your own templates and checklists | Named competitors, customers or logos |
| Anonymised pattern ("B2B trials often…") | Positioning, messaging, ICP wording |
| Vendor and tooling knowledge | Anything under another client's NDA |

When a genuinely useful pattern emerges across clients, write it as a general
observation with no client identifiable in it. If you cannot strip the identity, it
does not travel.
