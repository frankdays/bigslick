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
revendor marketingskills coreyhaines31/marketingskills
revendor openclaudia-skills OpenClaudia/openclaudia-skills
revendor anthropic-marketing anthropics/knowledge-work-plugins marketing
mv upstream/VERSIONS.new upstream/VERSIONS
echo "Done. Review add/removes above, update overlay/manifest.yaml, then: python3 scripts/compose.py"
