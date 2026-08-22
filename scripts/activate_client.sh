#!/usr/bin/env bash
# Usage: ./scripts/activate_client.sh <client-folder-name>
# Makes <client>'s context pack the one skills read (.agents/product-marketing.md convention).
# Uses RELATIVE symlinks so the repo can move/clone without breaking activation.
set -e
LIB="$(cd "$(dirname "$0")/.." && pwd)"
CLIENT_DIR="$LIB/core/clients/$1"
[ -d "$CLIENT_DIR" ] || { echo "No such client pack: $CLIENT_DIR"; ls "$LIB/core/clients"; exit 1; }
mkdir -p "$LIB/.agents"
ln -sfn "../core/clients/$1/product-marketing.md" "$LIB/.agents/product-marketing.md"
ln -sfn "$1" "$LIB/core/clients/_active"
echo "Active client: $1"
