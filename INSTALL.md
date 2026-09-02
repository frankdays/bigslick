# Installing Big Slick

You don't need to be technical to do this. It takes about five minutes, and most of that is installing Claude.

---

## Step 1 — Get Claude Code

Big Slick is a set of skills *for* Claude, so Claude has to be there first.

Download it from **[claude.com/claude-code](https://claude.com/claude-code)** and install it like any other app.

You'll need a Claude account. A paid plan is required for real work — the skills do a lot of thinking.

---

## Step 2 — Download Big Slick

From the [Releases page](https://github.com/frankdays/bigslick/releases), download **`bigslick-0.1.0.dmg`**.

Double-click it. A window opens showing a folder called `bigslick` and a short note. **Drag the `bigslick` folder into Documents** — don't run it from the disk image, which is read-only and disappears when you eject it.

*(There's a `.zip` on the same page if you prefer it. Same contents.)*

---

## Step 3 — Run the installer

Inside that folder is a file called **`INSTALL.command`**.

**Right-click it and choose "Open."** Then click **"Open"** again in the dialog that appears.

> **Why right-click instead of double-click?** macOS blocks apps it can't trace to a paid Apple developer account, and shows a warning like *"cannot be opened because it is from an unidentified developer."* Right-click → Open is how you tell macOS you trust this one. You only need to do it the first time. If you already double-clicked and got the warning, just close it and right-click → Open instead.

A black window opens and prints what it's doing. When it finishes you'll see:

```
Ready. 247 marketing skills installed and enabled.
Sample company loaded: hansel-ai
```

If it says something else, see **Troubleshooting** below. You can close the black window.

---

## Step 4 — Start using it

Open the `bigslick` folder in Terminal and type `claude`. If that sentence meant nothing to you, here's the shortest path:

1. Open the **Terminal** app (press `Cmd+Space`, type "Terminal", press Enter)
2. Type `cd ` — with a space after it — then **drag the `bigslick` folder onto the Terminal window** and press Enter
3. Type `claude` and press Enter

Then paste this:

```
Build a marketing plan for Hansel AI
```

Hansel AI is the sample company that ships with Big Slick, so this works before
you've entered anything about your own business.

Two more worth trying:

```
Define the ICP for Hansel AI
Run this plan past the marketing council
```

The last one convenes a simulated board of advisors — Seth Godin, David Ogilvy,
April Dunford and others — and gives you their arguments about your plan.

### Using your own company

Paste this:

```
Onboard my company
```

It interviews you about your business — positioning, ICP, competitors, funnel
numbers, tooling — and writes it all down. Every other skill reads what it
wrote, so you never edit files by hand.

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

A sample company called **hansel-ai** ships with it so you can try things before entering your own. It's fictional — every number in it is made up.

---

## Troubleshooting

**"Claude Code isn't installed yet"** — Step 1 didn't finish. Install Claude Code, then run `INSTALL.command` again.

**"cannot be opened because it is from an unidentified developer"** — you double-clicked. Close the dialog, right-click the file, choose Open.

**"Installed with problems — the plugin did not register"** — the installer checked its own work and something didn't take. Open Terminal in the folder and run `claude plugin install bigslick@bigslick` to see the actual error.

**A skill doesn't seem to fire** — say the skill's name directly: *"Use pipeline-math to model next year."* Skills are chosen from what you ask, so naming one removes the guesswork.

**Starting over** — `claude plugin uninstall bigslick@bigslick`, then run the installer again. Nothing you've written about your own company is touched; it lives in `core/clients/`.

---

## Removing it

```
claude plugin uninstall bigslick@bigslick
```

Then delete the folder. Your company packs are inside it, so copy `core/clients/` somewhere first if you want to keep them.
