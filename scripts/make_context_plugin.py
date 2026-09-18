#!/usr/bin/env python3
"""Turn a client context pack into something Claude loads everywhere.

    python3 scripts/make_context_plugin.py <company> [--out dist/context]

The pack in core/clients/<company>/ is markdown on a filesystem, and skills find
it by relative path (.agents/product-marketing.md). That only resolves when Claude
Code is launched from this repo — not from the user's own project, and not at all
in the desktop app, which has no working directory. So the customisation layer,
the thing that makes any of this better than generic advice, silently does nothing
for most installs.

A skill, by contrast, is loaded wherever Claude runs. This packages the pack AS a
skill, and emits it two ways because the two apps install differently:

  company-context-<company>.zip   on your Desktop -> upload as a global skill
  company-context-<company>.md    on your Desktop -> attach to a Project
  <out>/<company>/plugin/                         -> claude plugin marketplace add

All three every run, from one body, because the destinations take different
wrappers: the skill uploader requires a zip with the skill folder as its root and
will not accept a bare .md, while a Project takes the markdown directly.

Which you use depends on how you work. Someone at ONE company wants the skill:
uploaded once, on in every conversation, never switched. A consultant with several
clients wants the Project, because uploaded skills are all loaded at once -- five
clients would mean five company contexts competing in every chat, with nothing but
manual enabling and disabling between them. A Project holds one client's context,
and switching clients is switching project: the isolation is structural rather
than remembered.

Regenerate after editing the pack. Nothing here is client-specific in code; the
company's data only ever lives in the generated output.
"""
import argparse, json, re, shutil, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIENTS = ROOT / "core" / "clients"

# Order matters: the master summary first, then depth. Claude reads top-down.
SECTIONS = [
    ("product-marketing.md", "Company summary", ""),
    ("icp.md",               "Ideal customer profile", ""),
    ("messaging.md",         "Positioning and messaging", ""),
    ("competitors.md",       "Competitors", ""),
    ("voice.md",             "Voice and tone", ""),
    ("stack.md",             "Tools and data",
     "**Act on this, don't just read it.** Recommend workflows around the tools listed as "
     "owned; if something genuinely needs a tool they lack, say so explicitly and price the "
     "switch rather than assuming it. Never suggest anything under *Deliberately not used* "
     "without acknowledging they already rejected it. Where a tool is owned but **not "
     "connected**, you cannot call its API — ask the user for the figures instead of "
     "presenting an estimate as retrieved data. Respect the budget and procurement "
     "constraints before proposing a new vendor."),
    ("metrics-baseline.md",  "Funnel definitions and baselines",
     "Use these definitions rather than generic ones, and these actuals rather than industry "
     "benchmarks. If a number you need is missing, ask for it."),
    ("skills-profile.md",    "Which skills matter here", ""),
    ("team-map.md",          "Who holds which seat", ""),
]

def build_skill_md(company: str, pack: Path) -> tuple[str, int]:
    desc = (
        f"Company context for {company} - positioning, ICP, messaging, competitors, voice, "
        f"tools and funnel baselines. Load this BEFORE any marketing work: planning, copy, "
        f"campaigns, pricing, outreach, SEO, reporting, so the answer reflects this business "
        f"rather than generic advice. Also use when the user asks what you know about them."
    )
    # The description MUST be a quoted YAML scalar. A bare scalar containing ": " makes the
    # frontmatter unparseable, and a skill whose frontmatter will not parse simply never
    # loads — silently, which is how the first version of this shipped broken.
    out = ["---", "name: company-context", f"description: {json.dumps(desc)}", "---", ""]
    out += [f"# Company context — {company}", "",
            "You are working for the business described below. Treat this as fact and do not",
            "re-ask what it already answers. Where something is marked TBD, ask for it rather",
            "than inventing a value.", "",
            "**Say one line before your first substantive answer in a session:**",
            f"`Working from {company}'s context pack.` That tells the user their customisation",
            "is actually being applied — without it they cannot distinguish tailored work from",
            "generic advice.", ""]

    wrote = 0
    for fname, heading, guidance in SECTIONS:
        f = pack / fname
        if not f.exists():
            continue
        body = f.read_text().strip()
        # Drop only a leading H1 — this document supplies the heading. Filtering every
        # line starting with "# " would also eat comments inside fenced code blocks.
        lines = body.splitlines()
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        body = "\n".join(lines).strip()
        if not body:
            continue
        out += [f"## {heading}", ""]
        if guidance:
            out += [guidance, ""]
        out += [body, ""]
        wrote += 1

    out += ["## When something is missing — keep going", "",
            "A missing fact, tool or API key is never a reason to refuse the work. Most of the",
            "value here is judgement; the data is an input you can obtain another way.", "",
            "1. Try a built-in substitute first — web search, reading the page, or reasoning",
            "   from this pack.",
            "2. If you still need something only they have, ask for exactly that, once, and",
            "   specifically. \"Paste your top 10 keywords with volume and position\" gets",
            "   answered; \"do you have Semrush?\" stalls the conversation.",
            "3. Produce the deliverable anyway, marking which figures were supplied rather",
            "   than measured, and flagging the gaps inside the deliverable so they can be",
            "   filled later.", "",
            "Never present an estimate as retrieved data, and never raise the same missing",
            "credential more than once in a session — say the env var name and what it would",
            "automate, then carry on.", "",
            "Check *Tools and data* above before assuming anything is unavailable: a tool",
            "listed as owned but not connected means they have the data and you simply cannot",
            "fetch it, so ask. A tool they do not own means find another route, and put any",
            "recommendation to buy it at the end of the deliverable rather than in its way."]
    return "\n".join(out) + "\n", wrote

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("company")
    ap.add_argument("--pack", help="path to the pack, if it is not in core/clients/ "
                                   "(desktop-app users have no repo checkout)")
    ap.add_argument("--out", help="where to write; defaults beside the pack")
    a = ap.parse_args()

    if a.pack:
        pack = Path(a.pack).expanduser().resolve()
        if not pack.is_dir():
            sys.exit(f"No pack directory at {pack}")
    else:
        pack = CLIENTS / a.company
        if not pack.is_dir():
            sys.exit(f"No pack at core/clients/{a.company} — run company-onboarding first, "
                     f"or pass --pack <path> if your pack lives outside this repo.")

    skill_md, wrote = build_skill_md(a.company, pack)
    if wrote == 0:
        sys.exit(f"Pack at {pack} has no content yet. Fill it in, or re-run onboarding.")

    if a.out:
        out = Path(a.out).expanduser()
        out = (out if out.is_absolute() else ROOT / out) / a.company
    elif a.pack:
        out = pack.parent / f"{a.company}-context"   # stays with the user's own files
    else:
        out = ROOT / "dist" / "context" / a.company
    if out.exists():
        shutil.rmtree(out)
    skill_dir = out / "plugin" / "skills" / "company-context"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(skill_md)

    # Fail loudly rather than emit a skill that will never load. Deliberately does NOT use
    # pyyaml: this script ships in the end-user download, where system Python is
    # externally-managed and pyyaml is usually absent. The description is written with
    # json.dumps, and a JSON string is a valid quoted YAML scalar, so round-tripping it
    # through json.loads proves the exact property that broke the first version.
    fm = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
    problem = None
    if not fm:
        problem = "no frontmatter block"
    else:
        keys = dict(l.split(": ", 1) for l in fm.group(1).splitlines() if ": " in l)
        if keys.get("name") != "company-context":
            problem = "name missing or wrong"
        else:
            try:
                if not json.loads(keys.get("description", "")).strip():
                    problem = "description empty"
            except Exception:
                problem = "description is not a quoted scalar — YAML would reject it"
    if problem:
        sys.exit(f"Generated frontmatter is invalid ({problem}). Refusing to emit a skill "
                 f"that would silently fail to load.")

    cp = out / "plugin" / ".claude-plugin"
    cp.mkdir(parents=True)
    pname = f"bigslick-context-{a.company}"
    pdesc = (f"Company context for {a.company} — loaded by every Big Slick skill so "
             f"answers reflect this business.")
    cp.joinpath("plugin.json").write_text(json.dumps({
        "name": pname, "version": "1.0.0", "description": pdesc,
    }, indent=2) + "\n")
    # A directory marketplace needs its own manifest as well as the plugin one,
    # otherwise `claude plugin marketplace add <dir>` refuses it.
    cp.joinpath("marketplace.json").write_text(json.dumps({
        "name": pname,
        "owner": {"name": "Big Slick"},
        "plugins": [{"name": pname, "source": ".", "description": pdesc}],
    }, indent=2) + "\n")

    # Two wrappers around one body, because the two destinations accept different
    # things: a Project takes a markdown file (or pasted text), and the skill uploader
    # requires a zip with the skill folder as its root — it will not take a bare .md.
    # Emit both every run so nobody has to know which flag produces which.
    zp = out / "company-context.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("company-context/SKILL.md", skill_md)

    # The markdown drops the skill frontmatter: that block is addressed to the skill
    # loader, and inside a Project it reads as noise.
    body = re.sub(r"^---\n.*?\n---\n", "", skill_md, count=1, flags=re.S).lstrip()
    mp = out / "company-context.md"
    mp.write_text(body)

    # dist/ is gitignored build output and no place to send someone hunting from a file
    # dialog, so both land on the Desktop, named for the company to keep clients apart.
    desktop = Path.home() / "Desktop"
    out_zip, out_md = zp, mp
    if desktop.is_dir():
        try:
            out_zip = desktop / f"company-context-{a.company}.zip"
            out_md = desktop / f"company-context-{a.company}.md"
            shutil.copy2(zp, out_zip)
            shutil.copy2(mp, out_md)
        except Exception:
            out_zip, out_md = zp, mp      # read-only Desktop: the dist/ copies still work

    copied = revealed = False
    if sys.platform == "darwin":
        try:
            subprocess.run(["pbcopy"], input=body.encode(), check=True)
            copied = True
        except Exception:
            pass
        try:
            subprocess.run(["open", "-R", str(out_md)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            revealed = True
        except Exception:
            pass                          # headless or non-mac: the printed paths stand

    print(f"Built company context for {a.company} - {wrote} sections, {len(body)} chars.\n")

    print("Work at ONE company? Install it globally, as a skill:")
    print("  Settings -> Capabilities -> Skills -> Upload skill  (Cowork: Customize -> + -> Skills)")
    print(f"  {out_zip}\n")

    print("Several clients? Give each their own Project instead — uploaded skills all")
    print("load at once, so five clients would be five contexts competing in every chat.")
    print("  Add to the project's knowledge:")
    print(f"  {out_md}")
    if copied:
        print("  (its text is also on your clipboard, if you would rather paste)")
    print()

    print("Claude Code (terminal):")
    print(f"  claude plugin marketplace add {out}/plugin")
    print(f"  claude plugin install bigslick-context-{a.company}\n")

    if revealed:
        print("Finder is open on both files.")
    print("Re-run this after any change to the pack.")

if __name__ == "__main__":
    main()
