#!/usr/bin/env bash
# Build the end-user download: a single zip that works on its own.
#
# The v0.1 asset was just dist/, which cannot actually be installed — it has no
# installer, no marketplace manifest (the file `claude plugin marketplace add`
# needs), and no client packs, so the sample client the installer promises did
# not exist. This ships the whole usable product with dist/ prebuilt, so the
# user needs no Python, no compose step, and no clone.
set -e
cd "$(dirname "$0")/.."

VERSION=$(python3 -c "import json;print(json.load(open('overlay/plugin/plugin.json'))['version'])")
OUT="bigslick-$VERSION.zip"
STAGE=$(mktemp -d)/bigslick

# dist/ must be current before anything is copied.
python3 scripts/compose.py >/dev/null

mkdir -p "$STAGE"
# What an end user needs, and nothing else. No upstream/, no overlay/, no
# core/skills/ — those are build inputs, already composed into dist/.
cp -R dist "$STAGE/dist"
# Stale per-skill claude.ai zips are regenerated on demand by
# package_for_claude_ai.py; shipping a months-old copy means shipping skills the
# manifest now excludes, under the old brand name.
rm -rf "$STAGE/dist/claude-ai"
mkdir -p "$STAGE/.claude-plugin" "$STAGE/scripts" "$STAGE/core/clients"
cp .claude-plugin/marketplace.json "$STAGE/.claude-plugin/"
cp install.sh INSTALL.command INSTALL.md README.md LICENSE LICENSING.md "$STAGE/"
cp scripts/activate_client.sh "$STAGE/scripts/"
cp -R core/clients/_template "$STAGE/core/clients/"
[ -d core/clients/hansel-ai ] && cp -R core/clients/hansel-ai "$STAGE/core/clients/"

rm -f "$OUT"
( cd "$(dirname "$STAGE")" && zip -qr "$OLDPWD/$OUT" bigslick -x "*.DS_Store" "*/__pycache__/*" )
rm -rf "$(dirname "$STAGE")"

echo "Built $OUT ($(du -h "$OUT" | cut -f1))"
echo "Contains: $(unzip -l "$OUT" | grep -c 'SKILL.md') skills, installer, marketplace manifest, client packs."
