#!/usr/bin/env bash
# Re-vendor upstreams at latest; report skill add/removes vs current; rewrite VERSIONS. Then edit manifest & recompose.
set -e
cd "$(dirname "$0")/.."
> upstream/VERSIONS.new
revendor(){ # $1 dir  $2 repo  $3 subpath(optional)
  tmp=$(mktemp -d); git clone -q --depth 1 "https://github.com/$2.git" "$tmp"
  sha=$(git -C "$tmp" rev-parse HEAD); src="$tmp/${3:-.}"
  echo "== $1 -> $sha"
  diff <(ls "upstream/$1/skills" 2>/dev/null) <(ls "$src/skills") | grep '^[<>]' || echo "   (no skill add/removes)"
  rm -rf "upstream/$1"; mkdir -p "upstream/$1"; cp -r "$src/." "upstream/$1/"
  [ -f "$tmp/LICENSE" ] && cp "$tmp/LICENSE" "upstream/$1/LICENSE"
  rm -rf "$tmp"; rm -rf "upstream/$1/.git"
  echo "$2${3:+($3)} $sha" >> upstream/VERSIONS.new
}
# Wholesale upstreams (manifest selects with exclude-lists).
revendor marketingskills coreyhaines31/marketingskills
revendor openclaudia-skills OpenClaudia/openclaudia-skills
revendor anthropic-marketing anthropics/knowledge-work-plugins marketing

# Curated upstreams: only the skills named in overlay/manifest.yaml are vendored, so the
# repo stays lean. re-vendor <dir> <repo> re-clones and re-copies exactly that include-list.
curated(){ # $1 dir  $2 repo
  tmp=$(mktemp -d); git clone -q --depth 1 "https://github.com/$2.git" "$tmp"
  sha=$(git -C "$tmp" rev-parse HEAD)
  echo "== $1 -> $sha (curated)"
  python3 - "$1" "$tmp" <<'PY'
import os, shutil, sys, yaml
name, tmp = sys.argv[1], sys.argv[2]
m = yaml.safe_load(open("overlay/manifest.yaml"))
up = next(u for u in m["upstreams"] if u["name"] == name)
want = set(up.get("include", []))
found = {}
for root, _, files in os.walk(tmp):
    if "SKILL.md" in files:
        found[os.path.basename(root)] = root
dest = os.path.join("upstream", name, "skills")
shutil.rmtree(os.path.join("upstream", name), ignore_errors=True)
os.makedirs(dest)
for s in sorted(want):
    if s in found:
        shutil.copytree(found[s], os.path.join(dest, s))
    else:
        print(f"   MISSING upstream skill: {s}")
for cand in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
    p = os.path.join(tmp, cand)
    if os.path.exists(p):
        shutil.copy(p, os.path.join("upstream", name, "LICENSE")); break
print(f"   vendored {len(os.listdir(dest))}/{len(want)} skills")
PY
  echo "$2 $sha" >> upstream/VERSIONS.new
  rm -rf "$tmp"
}
curated goose-skills gooseworks-ai/goose-skills
curated kostja-marketing kostja94/marketing-skills
curated rampstack rampstackco/claude-skills
curated wondel wondelai/skills
mv upstream/VERSIONS.new upstream/VERSIONS
echo "Done. Review add/removes above, update overlay/manifest.yaml, then:"
echo "  python3 scripts/compose.py && python3 scripts/gen_inventory.py"
