# Big Slick in five minutes

The shortest path from nothing to your first piece of real marketing work.
Stuck anywhere, or on Windows or Linux? The [full install guide](INSTALL.md) has the
long version, including the macOS security prompt that trips most people up.

---

## 1. Install

**Desktop app** (a window you chat in) — nothing to download:

**Customize** in the left sidebar → **Plugins** → **Add** → **Add marketplace** →
**Add from a repository** → paste `https://github.com/frankdays/bigslick` → confirm →
click **Sync**. Then go to **Personal** and add **bigslick**.

Sync is the step people skip; nothing appears until you click it. You should end up with
eleven entries — **bigslick** plus ten optional bundles. A different number means the sync
didn't finish, so click **Sync** again.

**Claude Code** (you type `claude` at a command prompt):

```bash
claude plugin marketplace add https://github.com/frankdays/bigslick
claude plugin install bigslick@bigslick
```

Add only **bigslick** for now. That's 32 skills, and it's the right number — the other 217
wait in bundles you add when you reach for something the core doesn't have. Installing all
249 up front would cost you about 28,000 tokens of context in every conversation.

---

## 2. Check it loaded

Start a chat and ask:

```
What do you know about my business?
```

A working install tells you it has no context pack yet and points you at the skill that
fixes it. Generic marketing advice with no mention of a context pack means the plugin
isn't loaded — check it's *enabled*, not just installed, and see
[Troubleshooting](INSTALL.md#troubleshooting).

---

## 3. Tell it about your company

No sample company ships with Big Slick, so the skills have nothing to work from until you
do this. One instruction:

```
Onboard my company
```

The express path reads your site, drafts the whole pack — positioning, ICP, competitors,
voice, tooling, funnel numbers — and asks you to correct it. About ten minutes. Every
other skill reads what it wrote, so you configure once and never edit files by hand.

Running marketing for several companies? Say **"Onboard a new client"** instead: same
interview, but it sets up a roster you can switch between.

---

## 4. Do something real

```
Build me a marketing plan
Define our ICP
Run this plan past the marketing council
```

The last one convenes a simulated board — Seth Godin, David Ogilvy, April Dunford and
others — and gives you their arguments about your plan, including where they disagree.

You rarely need slash commands: skills are chosen from what you describe, so plain words
are the normal way in. When you do want one specific skill, name it with its prefix —
`bigslick:pipeline-review`, not `pipeline-review`. The bare name matches nothing and looks
exactly like a failed install.

---

**Next:** [INSTALL.md](INSTALL.md) for the download route, switching between companies, and
troubleshooting · [INVENTORY.md](INVENTORY.md) for all 249 skills ·
[MAINTAINERS.md](MAINTAINERS.md) for how the library is assembled.
