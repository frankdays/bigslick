#!/usr/bin/env python3
"""Package composed skills as upload-ready zips for Claude.ai / desktop app.

Usage:  python scripts/package_for_claude_ai.py --set leadership
        python scripts/package_for_claude_ai.py pipeline-review stakeholder-communication
        python scripts/package_for_claude_ai.py --all --client unleash
        python scripts/package_for_claude_ai.py --set leadership --check

Claude.ai's custom-skill format differs from the Claude Code plugin format in three
ways this script reconciles:

  1. One zip per skill, with the skill folder as the zip root (not a subfolder).
  2. `description` is capped at 200 chars (Claude Code allows ~1024). Hand-written
     short descriptions live in overlay/claude-ai/descriptions.yaml; anything without
     one is auto-compressed and REPORTED so the triggers can be fixed by hand.
  3. No filesystem, so the active client pack is bundled into the zip as client/*.md
     and the skill's repo-relative pack references are rewritten to point at it.

Claude Code-only frontmatter keys (metadata, allowed-tools, argument-hint,
user_invocable) are stripped — claude.ai reads name + description only.

Reads dist/skills/ — run scripts/compose.py first.
"""
import argparse, re, shutil, sys, zipfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml first")

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "skills"
OUT = ROOT / "dist" / "claude-ai"
OVERRIDES = ROOT / "overlay" / "claude-ai" / "descriptions.yaml"
CLIENTS = ROOT / "core" / "clients"

DESC_MAX = 200
NAME_MAX = 64
KEEP_KEYS = ("name", "description")

# Curated upload sets — claude.ai is the phone/couch surface, not the full library.
SETS = {
    "leadership": ["stakeholder-communication", "pipeline-review", "good-strategy-bad-strategy",
                   "predictable-revenue"],
    "proof": ["customer-story-builder", "review-intelligence-digest", "testimonials",
              "voice-of-customer-synthesizer"],
}


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("no YAML frontmatter")
    return yaml.safe_load(m.group(1)), m.group(2)


LEAD_MAX = 105  # chars of "what it does" before the trigger list gets the rest

def lead_clause(desc):
    """First sentence, de-boilerplated and trimmed, as the 'what it does' opener."""
    lead = re.split(r"(?<=[.!?])\s", desc.lstrip('"'), 1)[0].strip().rstrip(".")
    # these library-wide openers burn budget without adding meaning
    lead = re.sub(r"^When the user (?:wants|needs)(?:\s+(?:to|help))?\s+", "", lead, flags=re.I)
    lead = re.sub(r"^Use (?:this )?when (?:the user |you )?(?:wants? to\s+)?", "", lead, flags=re.I)
    if len(lead) > LEAD_MAX:  # cut at a clause boundary if there is one, else a word
        cut = max(lead.rfind(m, 0, LEAD_MAX) for m in (" — ", ", ", "; ", ": "))
        lead = (lead[:cut] if cut > 40 else lead[:LEAD_MAX].rsplit(" ", 1)[0]).rstrip(" ,;:—-")
        # a truncated enumeration reads as an exhaustive claim ("...content for LinkedIn"
        # when the skill covers six networks), so drop the dangling tail entirely
        trimmed = re.sub(r"\s+(?:for|on|across|including|like|such as|with|in)\s+[^,;:—]*$",
                         "", lead)
        if len(trimmed) > 30:
            lead = trimmed
        lead = lead.rstrip(" ,;:—-")  # trimming the tail can re-expose a dangling dash
    return lead[:1].upper() + lead[1:]


def triggers(desc):
    """Quoted trigger phrases, in order, deduped. 117/128 skills quote theirs."""
    # single-quoted triggers may contain contractions ("this page isn't converting"), so an
    # inner ' counts as content when a letter follows it, and the closing ' must not
    found = [a or b for a, b in re.findall(
        r'"([^"]{2,45})"|\'((?:[^\']|\'(?=[A-Za-z])){2,45}?)[,.]?\'(?![A-Za-z])', desc)]
    seen, out = set(), []
    for t in found:
        t = t.strip().rstrip(",.;").strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def compress(desc):
    """Fallback when no hand-written override exists. Returns (text, was_cut).

    Rebuilds rather than truncates: a short lead clause plus as many quoted trigger
    phrases as fit. Truncation drops the trigger sentence wholesale — and the triggers
    are what make a skill fire — so packing them explicitly is much closer to intent.
    Skills that quote no triggers fall back to packing whole leading sentences.
    """
    desc = " ".join(desc.split())
    if len(desc) <= DESC_MAX:
        return desc, False

    lead, trigs = lead_clause(desc), triggers(desc)
    if trigs:
        picked, body = [], ""
        for t in trigs:
            cand = ", ".join(f'"{x}"' for x in picked + [t])
            if len(f"{lead}. Use for {cand}.") > DESC_MAX:
                break
            picked, body = picked + [t], cand
        if picked:
            return f"{lead}. Use for {body}.", True
        return (lead + ".")[:DESC_MAX], True

    out, rest = "", re.findall(r"[^.!?]*[.!?]+(?:\s|$)", desc) or [desc]
    while rest and len(out) + len(rest[0]) <= DESC_MAX:
        out += rest.pop(0)
    out = out.strip()
    if not out:
        out = desc[: DESC_MAX - 1].rsplit(" ", 1)[0].rstrip(" ,;:—-") + "…"
    return out, True


def rewrite_pack_refs(body, has_pack):
    """Point repo-relative client-pack paths at the bundled copy."""
    if not has_pack:
        return body
    body = re.sub(r"(?<![\w/])\.agents/", "client/", body)
    body = re.sub(r"(?<![\w/])clients/_active/", "client/", body)
    body = re.sub(r"(?<![\w/])core/clients/_active/", "client/", body)
    return body


PACK_NOTE = (
    "\n\n---\n"
    "**Packaged for Claude.ai.** No filesystem here: the client context pack is bundled "
    "in `client/` beside this file — read it there, not from repo paths. External APIs are "
    "unreachable; use built-in tools and connected MCPs instead.\n"
)


def build(name, pack_files, overrides, check):
    src = DIST / name
    if not (src / "SKILL.md").exists():
        return {"name": name, "error": "not found in dist/skills/"}

    fm, body = split_frontmatter((src / "SKILL.md").read_text())
    orig_desc = " ".join(str(fm.get("description", "")).split())

    if name in overrides:
        desc, cut, source = " ".join(str(overrides[name]).split()), False, "override"
        if len(desc) > DESC_MAX:
            return {"name": name, "error": f"override is {len(desc)} chars (max {DESC_MAX})"}
    else:
        desc, cut = compress(orig_desc)
        source = "auto" if cut else "verbatim"

    if len(str(fm.get("name", name))) > NAME_MAX:
        return {"name": name, "error": f"name exceeds {NAME_MAX} chars"}

    new_fm = {k: fm[k] for k in KEEP_KEYS if k in fm}
    new_fm["name"], new_fm["description"] = fm.get("name", name), desc
    dropped = [k for k in fm if k not in KEEP_KEYS]

    body = rewrite_pack_refs(body, bool(pack_files)).rstrip() + (PACK_NOTE if pack_files else "\n")
    skill_md = "---\n" + yaml.safe_dump(new_fm, sort_keys=False, allow_unicode=True,
                                        width=10**6, default_style=None) + "---\n\n" + body.lstrip("\n")

    result = {"name": name, "desc_len": len(desc), "orig_len": len(orig_desc),
              "source": source, "cut": cut, "dropped": dropped,
              "pack": len(pack_files), "error": None}
    if check:
        return result

    stage = OUT / "_stage" / name
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(src, stage)
    (stage / "SKILL.md").write_text(skill_md)
    if pack_files:
        (stage / "client").mkdir(exist_ok=True)
        for f in pack_files:
            shutil.copy(f, stage / "client" / f.name)

    zpath = OUT / f"{name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(stage.rglob("*")):
            if f.is_file():
                z.write(f, Path(name) / f.relative_to(stage))  # zip root == skill folder
    result["zip"] = zpath
    result["kb"] = round(zpath.stat().st_size / 1024, 1)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="*", help="skill names from dist/skills/")
    ap.add_argument("--set", choices=sorted(SETS), help=f"curated set: {', '.join(sorted(SETS))}")
    ap.add_argument("--all", action="store_true", help="package all 128 (one zip each)")
    ap.add_argument("--client", default="_active", help="client pack to bundle, or 'none'")
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    a = ap.parse_args()

    if not DIST.exists():
        sys.exit("No dist/skills/ — run scripts/compose.py first.")

    names = list(a.skills)
    if a.set:
        names += SETS[a.set]
    if a.all:
        names = sorted(d.name for d in DIST.iterdir() if (d / "SKILL.md").exists())
    names = sorted(dict.fromkeys(names))
    if not names:
        sys.exit("Nothing to package. Pass skill names, --set, or --all.")

    pack_files = []
    if a.client != "none":
        pack_dir = CLIENTS / a.client
        if not pack_dir.exists():
            sys.exit(f"No client pack at {pack_dir}. Available: "
                     f"{[d.name for d in CLIENTS.iterdir() if d.is_dir()]}")
        pack_files = sorted(f for f in pack_dir.glob("*.md") if f.is_file())
        print(f"Client pack: {a.client} -> {pack_dir.resolve().name} ({len(pack_files)} files)\n")

    overrides = {}
    if OVERRIDES.exists():
        overrides = yaml.safe_load(OVERRIDES.read_text()) or {}

    if not a.check:
        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.mkdir(parents=True)

    rows = [build(n, pack_files, overrides, a.check) for n in names]
    if not a.check and (OUT / "_stage").exists():
        shutil.rmtree(OUT / "_stage")

    errors = [r for r in rows if r.get("error")]
    good = [r for r in rows if not r.get("error")]

    print(f"{'skill':<34} {'desc':>9}  source     bundled")
    print("-" * 68)
    for r in good:
        flag = "" if r["source"] != "auto" else "  <-- REVIEW"
        print(f"{r['name']:<34} {r['desc_len']:>3}/{DESC_MAX:<5} {r['source']:<10} "
              f"{r['pack']} pack files{flag}")
    for r in errors:
        print(f"{r['name']:<34} ERROR: {r['error']}")

    auto = [r for r in good if r["source"] == "auto"]
    print(f"\n{len(good)} packaged, {len(errors)} failed.")
    if not a.check and good:
        print(f"Zips: {OUT}")
    if auto:
        print(f"\n{len(auto)} description(s) auto-compressed — triggers were dropped to fit "
              f"{DESC_MAX} chars.\nHand-write better ones in {OVERRIDES.relative_to(ROOT)}:\n")
        for r in auto:
            print(f"  {r['name']}:  # was {r['orig_len']} chars")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
