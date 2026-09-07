#!/usr/bin/env bash
# Usage: ./scripts/activate_client.sh <client-folder-name>   (relative symlinks — repo can move)
set -e
LIB="$(cd "$(dirname "$0")/.." && pwd)"
CLIENT_DIR="$LIB/core/clients/$1"
PREV_ACTIVE=$(basename "$(readlink "$LIB/core/clients/_active" 2>/dev/null || echo "")" 2>/dev/null)
[ -d "$CLIENT_DIR" ] || { echo "No such client pack: $CLIENT_DIR"; ls "$LIB/core/clients"; exit 1; }
mkdir -p "$LIB/.agents"
ln -sfn "../core/clients/$1/product-marketing.md" "$LIB/.agents/product-marketing.md"
ln -sfn "$1" "$LIB/core/clients/_active"

# Skills look for .agents/product-marketing.md relative to the working directory, so the
# symlink above only resolves when Claude Code is launched from this repo. Most people run
# it from their own project folder instead. Copying to ~/.claude/ covers the case where
# Claude is launched from the home directory, which is the common default.
#
# Neither covers the desktop app, which has no working directory at all — for that, and for
# any other folder, generate the portable context skill:
#     python3 scripts/make_context_plugin.py <client>
HOME_COPY="$HOME/.claude/product-marketing.md"
if mkdir -p "$HOME/.claude" 2>/dev/null && cp -f "$CLIENT_DIR/product-marketing.md" "$HOME_COPY" 2>/dev/null; then
  HOME_STATE="~/.claude/product-marketing.md"
  # Switching clients silently replaces the global copy; say so, since a stale one there
  # would quietly feed the wrong company's context to anything reading it.
  [ -n "$PREV_ACTIVE" ] && [ "$PREV_ACTIVE" != "$1" ] && HOME_STATE="$HOME_STATE  (replaced $PREV_ACTIVE's)"
else
  HOME_STATE="FAILED to write ~/.claude/product-marketing.md — home-global lookup unavailable"
fi

echo "Active client: $1"
echo "  repo-local : .agents/product-marketing.md   (24 skills; only when Claude runs from this repo)"
echo "  home-global: $HOME_STATE"
echo "               (18 skills look for .claude/product-marketing.md, and only when Claude"
echo "                runs from your home directory — it does NOT satisfy the .agents/ lookup)"
echo "  portable   : python3 scripts/make_context_plugin.py $1"
echo "               the only route that works in the desktop app and from any folder"
