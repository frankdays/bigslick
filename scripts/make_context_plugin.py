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
import argparse, json, shutil, sys, zipfile
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

def build_skill_md(company: str, pack: Path) -> str:
    desc = (
        f"Company context for {company}: positioning, ICP, messaging, competitors, voice, "
        f"tools and funnel baselines. Load this BEFORE any marketing work — planning, copy, "
        f"campaigns, pricing, outreach, SEO, reporting — so the answer reflects this business "
        f"rather than generic advice. Also use when the user asks what you know about them."
    )
    if len(desc) > 1024:
        desc = desc[:1020] + "..."

    out = ["---", f"name: company-context", f"description: {desc}", "---", ""]
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
        # Drop the file's own H1; this document supplies the heading.
        lines = [l for l in body.splitlines() if not l.startswith("# ")]
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
    ap.add_argument("--out", default="dist/context")
    a = ap.parse_args()

    pack = CLIENTS / a.company
    if not pack.is_dir():
        sys.exit(f"No pack at core/clients/{a.company} — run company-onboarding first.")

    skill_md, wrote = build_skill_md(a.company, pack)
    if wrote == 0:
        sys.exit(f"Pack at {pack} has no content yet. Fill it in, or re-run onboarding.")

    out = ROOT / a.out / a.company
    if out.exists():
        shutil.rmtree(out)
    skill_dir = out / "plugin" / "skills" / "company-context"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(skill_md)

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

    rel = out.relative_to(ROOT)
    print(f"Built company context for {a.company} — {wrote} sections, {len(skill_md)} chars.\n")
    print("Claude Code (terminal):")
    print(f"  claude plugin marketplace add {ROOT/rel}/plugin")
    print(f"  claude plugin install bigslick-context-{a.company}\n")
    print("Claude desktop app:")
    print(f"  upload {rel}/company-context.zip under Settings -> Capabilities -> Skills\n")
    print("Re-run this after any change to the pack.")

if __name__ == "__main__":
    main()
