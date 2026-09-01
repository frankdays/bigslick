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
# core/skills/ — those are build inputs, already composed.
#
# The extracted folder must have the same shape as the repo root, because
# marketplace.json says `"source": "."` — so skills/ and .claude-plugin/ sit at
# the top level here, exactly as they do in git. Shipping dist/ instead would
# leave the marketplace pointing at a directory this zip does not contain.
mkdir -p "$STAGE/.claude-plugin" "$STAGE/scripts" "$STAGE/core/clients"
cp -R skills "$STAGE/skills"
cp .claude-plugin/plugin.json "$STAGE/.claude-plugin/"
# Bundles ship in the download too, so the offline installer can offer them without a
# network round-trip. They cost nothing until the user installs one — an uninstalled
# bundle contributes zero always-on tokens.
[ -d bundles ] && cp -R bundles "$STAGE/bundles"
cp dist/PROVENANCE.txt "$STAGE/" 2>/dev/null || true
cp .claude-plugin/marketplace.json "$STAGE/.claude-plugin/"
cp install.sh INSTALL.command INSTALL.md README.md LICENSE LICENSING.md "$STAGE/"
cp scripts/activate_client.sh "$STAGE/scripts/"
cp -R core/clients/_template "$STAGE/core/clients/"
[ -d core/clients/hansel-ai ] && cp -R core/clients/hansel-ai "$STAGE/core/clients/"

# Client packs are real customer data. The copies above are an explicit allowlist, but a
# leak here ships a client's positioning and funnel numbers to everyone who downloads the
# release, so assert rather than trust — this is cheap next to the failure it prevents.
STAGED=$(ls "$STAGE/core/clients" 2>/dev/null | sort | tr '\n' ' ')
EXPECTED="_template hansel-ai "
if [ "$STAGED" != "$EXPECTED" ]; then
  echo "ABORT: unexpected client packs staged for release: $STAGED" >&2
  echo "Expected exactly: $EXPECTED" >&2
  rm -rf "$(dirname "$STAGE")"; exit 1
fi

rm -f "$OUT"
( cd "$(dirname "$STAGE")" && zip -qr "$OLDPWD/$OUT" bigslick -x "*.DS_Store" "*/__pycache__/*" )
rm -rf "$(dirname "$STAGE")"

echo "Built $OUT ($(du -h "$OUT" | cut -f1))"
echo "Contains: $(unzip -l "$OUT" | grep -c 'SKILL.md') skills, installer, marketplace manifest, client packs."
echo "Layout matches the repo root (skills/ + bundles/ + .claude-plugin/), so every source resolves."
