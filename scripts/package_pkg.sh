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
# NOTE: still not code-signed. On macOS 15+ the user approves it once under
# System Settings -> Privacy & Security -> Open Anyway (right-click -> Open was
# removed in Sequoia). Only an Apple Developer ID plus notarisation removes that.
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
    touch "$DEST/.registered"
  else
    echo "claude CLI not found — skills copied, plugin NOT registered"
  fi
} > "$LOG" 2>&1

# Installer.app reports "Installation Successful" whichever way the above went,
# so a failure to register is invisible unless we put it in front of the user.
# This is exactly how a tester ended up with files on disk and no skills in Claude.
if [ -f "$DEST/.registered" ]; then
  rm -f "$DEST/.registered" "$DEST/FINISH SETUP.txt"
  open "$DEST" 2>/dev/null || true
else
  cat > "$DEST/FINISH SETUP.txt" << 'NOTE'
BIG SLICK IS NOT FINISHED INSTALLING
====================================

The files copied across fine, but the skills were NOT added to Claude.

The installer looks for Claude Code's command-line tool, and it isn't on this
Mac. That is completely normal if you use Claude in the desktop app — the app
and the command-line tool are separate things.

Pick whichever describes you.


IF YOU USE THE CLAUDE DESKTOP APP
---------------------------------
You do not need this installer at all, and you can delete this folder when
you are done. Add Big Slick inside the app instead:

  1. Open the Claude desktop app
  2. Click the "Customize" button in the left sidebar
  3. Open "Plugins"
  4. Click "Add"
  5. Choose "Add marketplace"
  6. Choose "Add from a repository"
  7. Paste this in and confirm:

         https://github.com/frankdays/bigslick

  8. Click "Sync" — this pulls the marketplace down, and nothing
     appears until you do
  9. Click "Browse" to see what's in it
 10. Go to "Personal"
 11. Add the packages you want. Start with "bigslick" — the 31-skill core
 12. Start a chat and say "Onboard my company" to tailor it to your business

Type "/" in a chat at any point to see the skills you've added.


IF YOU USE CLAUDE CODE IN THE TERMINAL
--------------------------------------
The command-line tool isn't installed yet. Get it from:

    https://claude.com/claude-code

Then open this folder and double-click INSTALL.command to finish.


WHAT WENT WRONG EXACTLY
-----------------------
install-log.txt in this folder has the details.
NOTE
  open "$DEST/FINISH SETUP.txt" 2>/dev/null || open "$DEST" 2>/dev/null || true
fi
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

BEFORE YOU CONTINUE — this installer is for Claude Code, the command-line
tool. If you use Claude in the DESKTOP APP, you don't need it: add Big Slick
inside the app under Customize > Plugins > "+" > Add marketplace > Add from a
repository, and paste https://github.com/frankdays/bigslick

Carrying on is harmless either way. Files go in your Documents folder, no
admin password is needed, and if the command-line tool isn't found the
installer tells you what to do instead.

Get Claude Code at https://claude.com/claude-code
TXT
cat > "$BUILD/resources/conclusion.txt" << 'TXT'
The files are in your Documents folder.

CHECK THIS FIRST
   If a file called "FINISH SETUP.txt" just opened, the skills were NOT
   added to Claude and that file tells you how to finish. This is normal
   if you use the Claude desktop app rather than the command-line tool.

   If your Documents/bigslick folder opened instead, you're all set.

TO START
   Open the Terminal app and paste this:

       cd ~/Documents/bigslick && claude

   Then type:  Build a marketing plan for Hansel AI

Hansel AI is a sample company included for trying things out, so that
works before you enter anything about a real business.

install-log.txt in the folder records exactly what happened.
TXT

rm -f "$PKG"
productbuild --quiet --distribution "$BUILD/distribution.xml" \
  --package-path "$BUILD" --resources "$BUILD/resources" "$PKG"

echo "Built $PKG ($(du -h "$PKG" | cut -f1))"
echo "Double-click to install. Unsigned: first run needs System Settings ->"
echo "Privacy & Security -> Open Anyway."
