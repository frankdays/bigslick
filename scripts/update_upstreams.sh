#!/usr/bin/env bash
# Re-vendor upstreams at latest, report diffs vs manifest, then re-run compose manually.
set -e
cd "$(dirname "$0")/.."
declare -A REPOS=(
  [marketingskills]=coreyhaines31/marketingskills
  [openclaudia-skills]=OpenClaudia/openclaudia-skills
)
> upstream/VERSIONS.new
for dir in "${!REPOS[@]}"; do
  tmp=$(mktemp -d); git clone -q --depth 1 "https://github.com/${REPOS[$dir]}.git" "$tmp"
  sha=$(git -C "$tmp" rev-parse HEAD); rm -rf "$tmp/.git"
  echo "== $dir -> $sha"
  diff <(ls upstream/$dir/skills) <(ls $tmp/skills) | grep '^[<>]' || echo "   (no skill add/removes)"
  rm -rf "upstream/$dir"; mv "$tmp" "upstream/$dir"
  echo "${REPOS[$dir]} $sha" >> upstream/VERSIONS.new
done
# anthropic marketing plugin
tmp=$(mktemp -d); git clone -q --depth 1 https://github.com/anthropics/knowledge-work-plugins.git "$tmp"
sha=$(git -C "$tmp" rev-parse HEAD)
diff <(ls upstream/anthropic-marketing/skills) <(ls $tmp/marketing/skills) | grep '^[<>]' || echo "   anthropic: (no skill add/removes)"
rm -rf upstream/anthropic-marketing && mkdir -p upstream/anthropic-marketing
cp -r "$tmp"/marketing/. upstream/anthropic-marketing/ && cp "$tmp"/LICENSE upstream/anthropic-marketing/LICENSE
rm -rf "$tmp"; echo "anthropics/knowledge-work-plugins(marketing) $sha" >> upstream/VERSIONS.new
mv upstream/VERSIONS.new upstream/VERSIONS
echo "Done. Review skill add/removes above, update overlay/manifest.yaml if needed, then: python scripts/compose.py"
