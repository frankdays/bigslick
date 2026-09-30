#!/usr/bin/env python3
"""Compose dist/skills from upstream + overlay + core. Later layers win; core wins all."""
import argparse, json, re, shutil, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml first")
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "skills"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_inventory import UPSTREAMS  # one source of truth for repo + licence

def skill_dirs(p): return sorted(d for d in p.iterdir() if d.is_dir() and (d/"SKILL.md").exists())

# Agent Skills cap a description at 1024 characters; claude.ai rejects an upload over it.
DESC_MAX = 1024
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
TOP_KEY_RE = re.compile(r"^[A-Za-z_][\w-]*:")

def source_line(src):
    """The attribution sentence appended to every shipped description."""
    if src == "core": return "Source: Big Slick (first-party, MIT)."
    repo, licence = UPSTREAMS[src][:2]
    return f"Source: {repo} ({licence})."

def attribute(skill_md: Path, src):
    """Append the source to the frontmatter description, leaving every other key untouched.

    Done here rather than as overlay patches so it costs nothing at an upstream refresh:
    upstream/ stays read-only and no skill file gains a merge conflict. The description is
    rewritten as a JSON string, which is valid YAML whatever style the upstream used.
    Returns the new description length.
    """
    text = skill_md.read_text()
    m = FM_RE.match(text)
    fm_text = m.group(1)
    fm = yaml.safe_load(fm_text)
    desc = " ".join(str(fm["description"]).split())
    tag = source_line(src)
    new = desc if desc.endswith(tag) else f"{desc} {tag}"
    lines, out, i = fm_text.split("\n"), [], 0
    while i < len(lines):
        if lines[i].startswith("description:"):
            out.append("description: " + json.dumps(new, ensure_ascii=False))
            i += 1
            while i < len(lines) and not TOP_KEY_RE.match(lines[i]): i += 1
            continue
        out.append(lines[i]); i += 1
    fm_new = "\n".join(out)
    check = yaml.safe_load(fm_new)
    if check.get("description") != new or {k: v for k, v in check.items() if k != "description"} \
            != {k: v for k, v in fm.items() if k != "description"}:
        sys.exit(f"attribution rewrite corrupted frontmatter in {skill_md}")
    skill_md.write_text(f"---\n{fm_new}\n---\n" + text[m.end():])
    return len(new)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    m = yaml.safe_load((ROOT/"overlay"/"manifest.yaml").read_text())
    plan, prov, new_up = {}, {}, []
    for up in m["upstreams"]:
        base = ROOT/up["path"]
        if not base.exists(): print(f"WARN missing upstream {up['name']}"); continue
        names = {d.name: d for d in skill_dirs(base)}
        if up.get("mode") == "include":
            chosen = {n: names[n] for n in up.get("include", []) if n in names}
            new_up += [f"{up['name']}/{n}" for n in names if n not in set(up.get("include", []))]
        else:
            excl = set(up.get("exclude", []))
            chosen = {n: d for n, d in names.items() if n not in excl}
        for n, d in chosen.items():
            if n in plan: print(f"  collision: {n} ({prov[n]} -> {up['name']}) — later wins")
            plan[n], prov[n] = d, up["name"]
    # The core (proprietary) layer is optional: v0.2 removed it and the
    # distribution is now open-source-only. A manifest with no `core:` key, or
    # one pointing at a directory that no longer exists, composes cleanly.
    core = m.get("core") or {}
    core_path = ROOT/core["path"] if core.get("path") else None
    if core_path and core_path.exists():
        for d in skill_dirs(core_path): plan[d.name], prov[d.name] = d, "core"
    if a.check:
        print(f"Would compose {len(plan)} skills.")
        if new_up: print(f"Upstream skills NOT in manifest include-lists (review after updates): {new_up}")
        c = {}
        for s in prov.values(): c[s] = c.get(s, 0)+1
        [print(f"  {k}: {v}") for k, v in sorted(c.items())]; return
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for name, src in sorted(plan.items()):
        shutil.copytree(src, DIST/name)
        patch = ROOT/"overlay"/"patches"/name
        if patch.exists(): shutil.copytree(patch, DIST/name, dirs_exist_ok=True); prov[name] += "+patch"
    too_long = []
    for name in sorted(plan):
        n = attribute(DIST/name/"SKILL.md", prov[name].replace("+patch", ""))
        if n > DESC_MAX: too_long.append(f"{name} ({n})")
    if too_long:
        sys.exit(f"descriptions over {DESC_MAX} chars once attributed — shorten via "
                 f"overlay/patches/<skill>/SKILL.md:\n  " + "\n  ".join(too_long))
    (ROOT/"dist"/"PROVENANCE.txt").write_text("\n".join(f"{n}\t{prov[n]}" for n in sorted(plan))+"\n")
    ps = ROOT/"overlay"/"plugin"/"plugin.json"
    if ps.exists():
        dest = ROOT/"dist"/".claude-plugin"; dest.mkdir(exist_ok=True); shutil.copy(ps, dest/"plugin.json")
    rd = ROOT/"overlay"/"plugin"/"README.md"
    if rd.exists(): shutil.copy(rd, ROOT/"dist"/"README.md")

    # Publish every plugin into its own subdirectory, the core included. dist/ is
    # gitignored and never reaches GitHub, so a marketplace pointing at "./dist" could
    # only ever install from a local checkout; these paths ARE committed, which is the
    # whole point of mirroring them.
    #
    # The core lives in plugin/ rather than at the repo root. A root source ("." ) made
    # the core the one entry that packaged the ENTIRE repository — upstream/, bundles/
    # and all — instead of its own lean skill set, and it was the only entry that failed
    # to appear in the desktop app's plugin browser while all ten bundles listed fine.
    # Every plugin root is now the same shape: <dir>/.claude-plugin/plugin.json + skills/.
    #
    # The root plugin is deliberately LEAN: every skill's frontmatter description is
    # loaded into every session, so shipping all of them by default taxes people who
    # wanted one specialty. Bundles carry the rest as separate installable plugins.
    bundles = m.get("bundles") or []
    assigned, dupes = {}, []
    for b in bundles:
        for n in b["skills"]:
            if n in assigned: dupes.append(f"{n} in both {assigned[n]} and {b['name']}")
            assigned[n] = b["name"]
    unknown = sorted(n for n in assigned if n not in plan)
    if dupes or unknown:
        sys.exit("manifest bundles invalid:\n  " + "\n  ".join(dupes + [f"unknown skill {n}" for n in unknown]))

    base_meta = json.loads(ps.read_text()) if ps.exists() else {"name": "bigslick"}

    def publish(dest: Path, names, meta):
        """Write one installable plugin root: .claude-plugin/plugin.json + skills/."""
        sk = dest/"skills"
        if sk.exists(): shutil.rmtree(sk)
        sk.mkdir(parents=True)
        for n in names: shutil.copytree(DIST/n, sk/n)
        cp = dest/".claude-plugin"; cp.mkdir(parents=True, exist_ok=True)
        (cp/"plugin.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    core_names = sorted(n for n in plan if n not in assigned)
    core_dir = ROOT/"plugin"
    publish(core_dir, core_names, base_meta)

    # Sweep the pre-0.2.9 root layout so a checkout that predates the move cannot leave a
    # second, stale copy of the core sitting at the repo root for the marketplace to find.
    legacy_skills, legacy_meta = ROOT/"skills", ROOT/".claude-plugin"/"plugin.json"
    if legacy_skills.exists(): shutil.rmtree(legacy_skills)
    if legacy_meta.exists(): legacy_meta.unlink()

    bundles_dir = ROOT/"bundles"
    if bundles_dir.exists(): shutil.rmtree(bundles_dir)
    entries = [{"name": base_meta["name"], "source": "./plugin",
                "description": base_meta.get("description", "")}]
    for b in bundles:
        meta = {"name": f"bigslick-{b['name']}", "version": base_meta.get("version", "0.0.0"),
                "description": b["description"].strip(), "author": base_meta.get("author", {})}
        publish(bundles_dir/b["name"], sorted(b["skills"]), meta)
        entries.append({"name": meta["name"], "source": f"./bundles/{b['name']}",
                        "description": meta["description"]})

    # marketplace.json is generated so the plugin list can never drift from the manifest.
    mkp = ROOT/".claude-plugin"/"marketplace.json"
    existing = json.loads(mkp.read_text()) if mkp.exists() else {}
    mkp.write_text(json.dumps({"name": existing.get("name", "bigslick"),
                               "owner": existing.get("owner", {}),
                               "plugins": entries}, indent=2, ensure_ascii=False) + "\n")

    print(f"Composed {len(plan)} skills into dist/skills/. "
          f"Published {len(core_names)} in plugin/ + "
          f"{len(bundles)} bundles ({len(assigned)} skills).")

if __name__ == "__main__": main()
