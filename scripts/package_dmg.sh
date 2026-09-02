#!/usr/bin/env bash
# Build the macOS disk image from the release bundle.
#
# macOS-only (hdiutil), and deliberately NOT part of scripts/test.sh or the
# required build path — CI runs on Linux and would fail on it. Run this when
# cutting a release, after package_release.sh.
#
# NOTE: a .dmg does not bypass Gatekeeper. Files inside a downloaded image are
# still quarantined. On macOS 15+ the user must approve it in System Settings →
# Privacy & Security → Open Anyway; right-click → Open no longer works. Only Apple
# code-signing plus notarisation removes that step.
set -e
cd "$(dirname "$0")/.."

command -v hdiutil >/dev/null || { echo "hdiutil not found — this script only runs on macOS."; exit 1; }

VERSION=$(python3 -c "import json;print(json.load(open('overlay/plugin/plugin.json'))['version'])")
ZIP="bigslick-$VERSION.zip"
DMG="bigslick-$VERSION.dmg"
[ -f "$ZIP" ] || bash scripts/package_release.sh

STAGE=$(mktemp -d)
unzip -q "$ZIP" -d "$STAGE"

# A plain-language note at the top level of the image, because the first thing a
# user does with a mounted DMG is look at it, not read a web page.
cat > "$STAGE/Read Me First.txt" << 'TXT'
BIG SLICK — INSTALLING

1. Drag the "bigslick" folder out of this window, into Documents.

2. Open that folder and double-click INSTALL.command.
   macOS will refuse, saying it can't verify the developer. Expected.

3. Open System Settings - Privacy & Security. Scroll down to Security.
   Click "Open Anyway" next to the message naming INSTALL.command,
   then confirm with Touch ID or your password. You only do this once.

   (Older guides say to right-click and choose Open. That stopped
   working in macOS 15. Use System Settings.)

4. Wait for it to say "Ready." Then follow the instructions it prints.

Need Claude Code first? Get it at https://claude.com/claude-code

Full guide: INSTALL.md inside the folder.
TXT

rm -f "$DMG"
hdiutil create -quiet -volname "Big Slick $VERSION" -srcfolder "$STAGE" \
  -ov -format UDZO "$DMG"
rm -rf "$STAGE"

echo "Built $DMG ($(du -h "$DMG" | cut -f1))"
