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

  <out>/<company>/plugin/     a plugin root  -> claude plugin marketplace add <path>
  <out>/<company>/company-context.zip        -> desktop app, upload as a skill

Regenerate after editing the pack. Nothing here is client-specific in code; the
company's data only ever lives in the generated output.
"""
import argparse, json, re, shutil, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIENTS = ROOT / "core" / "clients"

# Order matters: the master summary first, then depth. Claude reads top-down.
SECTIONS = [
    ("product-marketing.md", "Company summary"),
    ("icp.md",               "Ideal customer profile"),
    ("messaging.md",         "Positioning and messaging"),
    ("competitors.md",       "Competitors"),
    ("voice.md",             "Voice and tone"),
    ("stack.md",             "Tools and data"),
    ("metrics-baseline.md",  "Funnel definitions and baselines"),
    ("skills-profile.md",    "Which skills matter here"),
    ("team-map.md",          "Who holds which seat"),
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
    for fname, heading in SECTIONS:
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
        out += [f"## {heading}", "", body, ""]
        wrote += 1

    out += ["## When something is missing", "",
            "If the user asks for work that needs a fact this pack does not carry, say which",
            "fact is missing and ask for it. Do not fall back to industry averages silently."]
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

    # Desktop app takes one zip per skill, with the skill folder as the zip root.
    zp = out / "company-context.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("company-context/SKILL.md", skill_md)

    try:
        shown = out.relative_to(ROOT)
    except ValueError:
        shown = out            # --out pointed outside the repo; absolute path is still correct
    print(f"Built company context for {a.company} - {wrote} sections, {len(skill_md)} chars.\n")
    print("Claude Code (terminal):")
    print(f"  claude plugin marketplace add {out}/plugin")
    print(f"  claude plugin install bigslick-context-{a.company}\n")
    print("Claude desktop app:")
    print(f"  upload {shown}/company-context.zip under Settings -> Capabilities -> Skills\n")
    print("Re-run this after any change to the pack.")

if __name__ == "__main__":
    main()
