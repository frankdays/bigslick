#!/usr/bin/env bash
# Build a double-clickable macOS .pkg installer.
#
# macOS-only, and not part of scripts/test.sh — CI runs on Linux. Run when
# cutting a release, after package_release.sh.
#
# Why a .pkg rather than the .dmg: the disk image asks the user to drag a folder
# and then right-click a script, which is two unfamiliar gestures. A .pkg is the
# format macOS users already know — double-click, click through Installer.app,
# done. No Terminal, no dragging.
#
# It installs into the user's home (Documents/bigslick) via the currentUserHome
# domain, so it never asks for an admin password.
#
# NOTE: still not code-signed, so the first launch needs right-click -> Open.
# Only an Apple Developer ID plus notarisation removes that.
set -e
cd "$(dirname "$0")/.."

command -v pkgbuild >/dev/null || { echo "pkgbuild not found — macOS only."; exit 1; }

VERSION=$(python3 -c "import json;print(json.load(open('overlay/plugin/plugin.json'))['version'])")
ZIP="bigslick-$VERSION.zip"
PKG="bigslick-$VERSION.pkg"
[ -f "$ZIP" ] || bash scripts/package_release.sh

BUILD=$(mktemp -d); trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/root" "$BUILD/scripts"
unzip -q "$ZIP" -d "$BUILD/unzipped"
# Payload lands at ~/Documents/bigslick — install-location is relative to the home.
mkdir -p "$BUILD/root/Documents"
mv "$BUILD/unzipped/bigslick" "$BUILD/root/Documents/bigslick"

cat > "$BUILD/scripts/postinstall" << 'POST'
#!/bin/bash
# Runs as the logged-in user (currentUserHome domain), not root.
DEST="$HOME/Documents/bigslick"
LOG="$DEST/install-log.txt"
{
  echo "Big Slick postinstall — $(date)"
  cd "$DEST" || exit 0

  # Installer.app runs with a minimal PATH, so a normally-installed claude is
  # invisible here. Look where it actually lives before giving up.
  for d in /usr/local/bin /opt/homebrew/bin "$HOME/.local/bin" "$HOME/.claude/local" \
           "$HOME/.bun/bin" "$HOME/.volta/bin" /usr/bin; do
    [ -x "$d/claude" ] && PATH="$d:$PATH"
  done
  export PATH

  if command -v claude >/dev/null 2>&1; then
    bash install.sh && echo "install.sh completed"
  else
    echo "claude not found — skills copied, plugin not registered"
  fi
} > "$LOG" 2>&1

# Leave the user somewhere useful rather than silently finishing.
open "$DEST" 2>/dev/null || true
exit 0
POST
chmod +x "$BUILD/scripts/postinstall"

pkgbuild --quiet --root "$BUILD/root" --scripts "$BUILD/scripts" \
  --identifier com.frankdays.bigslick --version "$VERSION" \
  --install-location "/" "$BUILD/component.pkg"

cat > "$BUILD/distribution.xml" << XML
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
  <title>Big Slick — $VERSION</title>
  <organization>com.frankdays</organization>
  <domains enable_anywhere="false" enable_currentUserHome="true" enable_localSystem="false"/>
  <options customize="never" require-scripts="false" hostArchitectures="arm64,x86_64"/>
  <welcome file="welcome.txt" mime-type="text/plain"/>
  <conclusion file="conclusion.txt" mime-type="text/plain"/>
  <choices-outline><line choice="default"/></choices-outline>
  <choice id="default" visible="false"><pkg-ref id="com.frankdays.bigslick"/></choice>
  <pkg-ref id="com.frankdays.bigslick" version="$VERSION">component.pkg</pkg-ref>
</installer-gui-script>
XML

mkdir -p "$BUILD/resources"
cat > "$BUILD/resources/welcome.txt" << 'TXT'
Big Slick installs a library of marketing skills for Claude.

It will be placed in your Documents folder, and registered with Claude Code
automatically. No admin password is needed.

You need Claude Code installed first. If it isn't, the files are still copied
and you can finish later by opening the folder and running install.sh.

Get Claude Code at https://claude.com/claude-code
TXT
cat > "$BUILD/resources/conclusion.txt" << 'TXT'
Done. Big Slick is in your Documents folder.

TO START
   Open the Terminal app and paste this:

       cd ~/Documents/bigslick && claude

   Then type:  Build a marketing plan for Hansel AI

Hansel AI is a sample company included for trying things out, so that
works before you enter anything about a real business.

Your Documents/bigslick folder has been opened for you. If something
went wrong, install-log.txt in that folder says what.
TXT

rm -f "$PKG"
productbuild --quiet --distribution "$BUILD/distribution.xml" \
  --package-path "$BUILD" --resources "$BUILD/resources" "$PKG"

echo "Built $PKG ($(du -h "$PKG" | cut -f1))"
echo "Double-click to install. Unsigned, so first run needs right-click -> Open."
