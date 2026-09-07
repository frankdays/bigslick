#!/usr/bin/env bash
# Usage: ./scripts/activate_client.sh <client-folder-name>   (relative symlinks — repo can move)
set -e
LIB="$(cd "$(dirname "$0")/.." && pwd)"
CLIENT_DIR="$LIB/core/clients/$1"
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
mkdir -p "$HOME/.claude"
cp -f "$CLIENT_DIR/product-marketing.md" "$HOME/.claude/product-marketing.md" 2>/dev/null || true

echo "Active client: $1"
echo "  repo-local : .agents/product-marketing.md"
echo "  home-global: ~/.claude/product-marketing.md"
echo "  portable   : python3 scripts/make_context_plugin.py $1   (desktop app + any folder)"
