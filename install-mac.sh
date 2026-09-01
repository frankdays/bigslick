#!/usr/bin/env bash
# Big Slick — one-line macOS installer.
#
#   curl -fsSL https://raw.githubusercontent.com/frankdays/bigslick/main/install-mac.sh | bash
#
# Piped from a URL, so macOS never quarantines it and there is no Gatekeeper
# prompt — the thing that makes the .dmg a three-step process. Installs the full
# package (skills + sample company) into ~/Documents/bigslick.
set -e

BOLD=$(tput bold 2>/dev/null || true); NORM=$(tput sgr0 2>/dev/null || true)
DEST="$HOME/Documents/bigslick"
REPO="frankdays/bigslick"

echo ""
echo "${BOLD}Installing Big Slick${NORM}"
echo ""

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code isn't installed yet — Big Slick is a set of skills for it."
  echo ""
  echo "  Install it from:  https://claude.com/claude-code"
  echo "  (or, with Node:   npm install -g @anthropic-ai/claude-code)"
  echo ""
  echo "Then run this same command again."
  exit 1
fi

# Resolve the latest release rather than hard-coding a version, so this line keeps
# working after every release without being reissued.
echo "Finding the latest release..."
URL=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
      | grep -o '"browser_download_url": *"[^"]*\.zip"' | head -1 | cut -d'"' -f4)
[ -n "$URL" ] || { echo "Couldn't find a release to download. Check https://github.com/$REPO/releases"; exit 1; }

if [ -d "$DEST" ]; then
  BACKUP="$DEST.previous-$(date +%Y%m%d%H%M%S)"
  echo "Existing install found — moving it to $(basename "$BACKUP")"
  mv "$DEST" "$BACKUP"
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
echo "Downloading..."
curl -fsSL "$URL" -o "$TMP/bigslick.zip"
echo "Unpacking..."
unzip -q "$TMP/bigslick.zip" -d "$TMP"
mkdir -p "$(dirname "$DEST")"
mv "$TMP/bigslick" "$DEST"

# Files written by this script are not quarantined, so install.sh runs directly.
cd "$DEST"
bash install.sh

echo ""
echo "${BOLD}Installed to:${NORM} $DEST"
echo ""
echo "To start, copy and paste this:"
echo ""
echo "    cd ~/Documents/bigslick && claude"
echo ""
