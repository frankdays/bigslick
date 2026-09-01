#!/usr/bin/env python3
"""Compose dist/skills from upstream + overlay + core. Later layers win; core wins all."""
import argparse, json, shutil, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml first")
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "skills"

def skill_dirs(p): return sorted(d for d in p.iterdir() if d.is_dir() and (d/"SKILL.md").exists())

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
    (ROOT/"dist"/"PROVENANCE.txt").write_text("\n".join(f"{n}\t{prov[n]}" for n in sorted(plan))+"\n")
    ps = ROOT/"overlay"/"plugin"/"plugin.json"
    if ps.exists():
        dest = ROOT/"dist"/".claude-plugin"; dest.mkdir(exist_ok=True); shutil.copy(ps, dest/"plugin.json")
    rd = ROOT/"overlay"/"plugin"/"README.md"
    if rd.exists(): shutil.copy(rd, ROOT/"dist"/"README.md")

    # Publish the repo root as the plugin itself, so `claude plugin marketplace add
    # <github url>` resolves. dist/ is gitignored and never reaches GitHub, so a
    # marketplace pointing at "./dist" can only ever install from a local checkout.
    # These paths ARE committed; that is the whole point of mirroring them.
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
    publish(ROOT, core_names, base_meta)

    bundles_dir = ROOT/"bundles"
    if bundles_dir.exists(): shutil.rmtree(bundles_dir)
    entries = [{"name": base_meta["name"], "source": ".",
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
          f"Published {len(core_names)} in the root plugin + "
          f"{len(bundles)} bundles ({len(assigned)} skills).")

if __name__ == "__main__": main()
