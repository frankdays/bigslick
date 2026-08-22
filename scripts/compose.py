#!/usr/bin/env python3
"""Compose the deployable skill library from upstream + overlay + core.

Usage:  python scripts/compose.py           # builds dist/skills/
        python scripts/compose.py --check   # report what would change / new upstream skills

Rules: later layers overwrite earlier ones. Patches in overlay/patches/<skill>/ overlay
onto the composed skill. Core always wins. Upstream files are never modified.
"""
import argparse, shutil, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml first")

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "skills"


def skill_dirs(path: Path):
    return sorted(d for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    m = yaml.safe_load((ROOT / "overlay" / "manifest.yaml").read_text())
    plan, provenance, new_upstream = {}, {}, []

    for up in m["upstreams"]:
        base = ROOT / up["path"]
        if not base.exists():
            print(f"WARN: missing upstream {up['name']} at {base}"); continue
        names = {d.name: d for d in skill_dirs(base)}
        if up.get("mode") == "include":
            chosen = {n: names[n] for n in up.get("include", []) if n in names}
            skipped_new = [n for n in names if n not in up.get("include", [])]
        else:
            excl = set(up.get("exclude", []))
            chosen = {n: d for n, d in names.items() if n not in excl}
            skipped_new = []
        for n, d in chosen.items():
            if n in plan:
                print(f"  collision: {n} ({provenance[n]} -> {up['name']}) — later layer wins")
            plan[n], provenance[n] = d, up["name"]
        # surface upstream skills the manifest has no opinion on (mode:include only)
        known = set(up.get("include", [])) if up.get("mode") == "include" else set()
        new_upstream += [f"{up['name']}/{n}" for n in skipped_new if n not in known]

    core = ROOT / m["core"]["path"]
    for d in skill_dirs(core):
        plan[d.name], provenance[d.name] = d, "core"

    if args.check:
        print(f"Would compose {len(plan)} skills.")
        if new_upstream:
            print(f"Upstream skills NOT in manifest include-lists (review after updates): {new_upstream}")
        counts = {}
        for src in provenance.values():
            counts[src] = counts.get(src, 0) + 1
        for k, v in sorted(counts.items()):
            print(f"  {k}: {v}")
        return

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for name, src in sorted(plan.items()):
        shutil.copytree(src, DIST / name)
        patch = ROOT / "overlay" / "patches" / name
        if patch.exists():
            shutil.copytree(patch, DIST / name, dirs_exist_ok=True)
            provenance[name] += "+patch"
    (ROOT / "dist" / "PROVENANCE.txt").write_text(
        "\n".join(f"{n}\t{provenance[n]}" for n in sorted(plan)) + "\n")
    # stamp plugin manifest so dist/ is directly installable as a Claude Code plugin
    plugin_src = ROOT / "overlay" / "plugin" / "plugin.json"
    if plugin_src.exists():
        dest = ROOT / "dist" / ".claude-plugin"
        dest.mkdir(exist_ok=True)
        shutil.copy(plugin_src, dest / "plugin.json")
    print(f"Composed {len(plan)} skills into dist/skills/  (installable plugin; provenance: dist/PROVENANCE.txt)")


if __name__ == "__main__":
    main()
