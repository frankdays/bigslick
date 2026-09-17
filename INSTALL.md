# Installing Big Slick

You don't need to be technical to do this. It takes about five minutes, and most of that is installing Claude.

---

## Which Claude do you have?

**The desktop app** (a window you chat in) and **Claude Code** (you type `claude` at a command
prompt) are different products, and Big Slick installs differently in each.

**Desktop app — no download needed.**

1. Open the Claude desktop app
2. Click the **Customize** button in the left sidebar
3. Open **Plugins**
4. Click **Add**
5. Choose **Add marketplace**
6. Choose **Add from a repository**
7. Paste in `https://github.com/frankdays/bigslick` and confirm
8. Click **Sync** — this pulls the marketplace down; nothing appears until you do
9. The skill groupings appear on their own once the sync finishes — eleven entries: **bigslick** (the core) plus ten optional bundles. See a different number, or none? The sync didn't finish; click **Sync** again.
10. Go to **Personal**
11. Add **bigslick** — the 32-skill core. Add bundles later, when you reach for something it doesn't have.
12. Check the plugin is *enabled*, not just installed — anything switched off contributes no skills
13. Start a chat and say **Onboard my company** (or **Onboard a new client** if you run marketing for several) to tailor everything to your business

To confirm the skills are there, type `/` and look for the `bigslick:` prefix — it's
`/bigslick:company-onboarding`, not `/company-onboarding`. Searching the bare name finds
nothing and looks exactly like a failed install. You rarely need the slash though: skills
match on what you describe, so plain words are the normal way in.

**Claude Code — carry on below.** The downloadable installers drive the Claude Code CLI and
cannot add skills to the desktop app.

---

## Step 1 — Get Claude Code

Big Slick is a set of skills *for* Claude, so Claude has to be there first.

Download it from **[claude.com/claude-code](https://claude.com/claude-code)** and install it like any other app.

You'll need a Claude account. A paid plan is required for real work — the skills do a lot of thinking.

---

## Step 2 — Download Big Slick

From the [Releases page](https://github.com/frankdays/bigslick/releases), download the latest **`bigslick-<version>.dmg`** (currently `bigslick-0.2.7.dmg`).

Double-click it. A window opens showing a folder called `bigslick` and a short note. **Drag the `bigslick` folder into Documents** — don't run it from the disk image, which is read-only and disappears when you eject it.

*(There's a `.zip` on the same page if you prefer it. Same contents.)*

---

## Step 3 — Run the installer

Inside that folder is a file called **`INSTALL.command`**.

**Double-click it.** macOS will block it — that's expected, and the next step is how you get past it.

> **Getting past the warning.** macOS blocks anything not signed with a paid Apple developer account. Close the dialog, then open
> **System Settings → Privacy & Security**, scroll down to the **Security** section, and click **Open Anyway** next to the message
> naming the blocked file. Confirm with Touch ID or your password. You only do this once.
>
> *If you've read older instructions saying to right-click and choose Open — that stopped working in macOS 15 (Sequoia). Use System Settings instead.*

A black window opens and prints what it's doing — registering the marketplace, then installing the plugin. When it finishes you'll see:

```
Ready. 32 core skills installed and enabled.
217 more sit in optional bundles and are NOT installed yet — that is
deliberate, so they cost you no context until you ask for them.
Confirm any time with:  claude plugin list
```

**32 is the right number, not a partial install.** Big Slick ships lean: the core plugin
is what loads every session, and the other 217 skills wait in bundles you add when you
need them. Adding them all up front would cost you around 28,000 tokens of context in
every single conversation.

If it says something else, see **Troubleshooting** below. You can close the black window.

---

## Step 4 — Start using it

Open the `bigslick` folder in Terminal and type `claude`. If that sentence meant nothing to you, here's the shortest path:

1. Open the **Terminal** app (press `Cmd+Space`, type "Terminal", press Enter)
2. Type `cd ` — with a space after it — then **drag the `bigslick` folder onto the Terminal window** and press Enter
3. Type `claude` and press Enter

### First, confirm it's actually loaded

Paste this:

```
What do you know about my business?
```

A working install tells you it has no context pack yet and points you at the skill
that fixes it. If you instead get generic marketing advice with no mention of a
context pack, the plugin isn't loaded — see **Troubleshooting**.

You can also check from the command line at any time:

```
claude plugin list
```

That should show `bigslick@bigslick` with `Status: ✔ enabled`. Installed but *disabled*
contributes no skills and is easy to miss.

### Then set up your company

No sample company ships with Big Slick, so the skills have nothing to work from until
you tell them about your business. That takes one instruction. Paste this:

```
Onboard my company
```

It interviews you about your business — positioning, ICP, competitors, funnel
numbers, tooling — and writes it all down. Every other skill reads what it
wrote, so you never edit files by hand.

Once that's done, these are worth trying:

```
Build me a marketing plan
Define our ICP
Run this plan past the marketing council
```

The last one convenes a simulated board of advisors — Seth Godin, David Ogilvy,
April Dunford and others — and gives you their arguments about your plan.

If you would rather fill the files in yourself, copy the template instead:

```
cp -r core/clients/_template core/clients/mycompany
bash scripts/activate_client.sh mycompany
```

---

## Working with more than one company

Big Slick keeps each company's facts in its own folder, and the skills read whichever one is active. To switch:

```
./scripts/activate_client.sh acme
```

Or just ask Claude to switch to Acme; it knows how.

Nothing is loaded until you onboard. Say **"onboard my company"** (or **"onboard a new client"** if you run marketing for several) and Claude builds your context pack. Until then every skill says plainly that it is giving general advice rather than advice about you.

---

## Troubleshooting

**"Claude Code isn't installed yet"** — Step 1 didn't finish. Install Claude Code, then run `INSTALL.command` again.

**"cannot be opened because it is from an unidentified developer"** — expected. Close the dialog, open **System Settings → Privacy & Security**, scroll to Security, click **Open Anyway**, and confirm. Right-click → Open does *not* work on macOS 15 or later.

**"Installed with problems — the plugin did not register"** — the installer checked its own work and something didn't take. Open Terminal in the folder and run `claude plugin install bigslick@bigslick` to see the actual error.

**A skill doesn't seem to fire** — name it directly, with its plugin prefix: *"Use `bigslick:pipeline-review` to look at next year."* Skills are chosen from what you ask, so naming one removes the guesswork. The prefix matters: the bare name matches nothing.

**Starting over** — `claude plugin uninstall bigslick@bigslick`, then run the installer again. Nothing you've written about your own company is touched; it lives in `core/clients/`.

---

## Removing it

```
claude plugin uninstall bigslick@bigslick
```

Then delete the folder. Your company packs are inside it, so copy `core/clients/` somewhere first if you want to keep them.
