#!/usr/bin/env bash
# BigSlick installer — sets up everything. Safe to re-run.
set -e
cd "$(dirname "$0")"
BOLD=$(tput bold 2>/dev/null || true); NORM=$(tput sgr0 2>/dev/null || true)
echo "${BOLD}Installing BigSlick...${NORM}"

# 1) Claude Code present?
if ! command -v claude >/dev/null 2>&1; then
  echo ""
  echo "Claude Code isn't installed yet. Two options:"
  echo "  A) If you have Node.js:  npm install -g @anthropic-ai/claude-code"
  echo "  B) Download the app:     https://claude.com/claude-code"
  echo "Then double-click this installer again."
  exit 1
fi

# 2) Skills built? (shipped pre-built; rebuild only if missing and python exists)
if [ ! -d dist/skills ]; then
  command -v python3 >/dev/null && pip3 install -q pyyaml && python3 scripts/compose.py \
    || { echo "dist/skills missing and couldn't rebuild — re-download the package."; exit 1; }
fi

# 3) Register + install the plugin (idempotent)
claude plugin marketplace add "$(pwd)" >/dev/null 2>&1 || claude plugin marketplace update bigslick >/dev/null 2>&1 || true
claude plugin install bigslick@bigslick >/dev/null 2>&1 || claude plugin update bigslick@bigslick >/dev/null 2>&1 || {
  echo "Plugin install hit a snag — run manually: claude plugin install bigslick@bigslick"; exit 1; }

# 4) Activate the sample client so everything works immediately
bash scripts/activate_client.sh hansel-ai >/dev/null

echo ""
echo "${BOLD}Done. $(find dist/skills -name SKILL.md | wc -l | tr -d ' ') marketing skills installed.${NORM}"
echo ""
echo "Open Terminal in this folder, type ${BOLD}claude${NORM}, and try:"
echo "  1. \"Build the pipeline model for Hansel AI's year\"     (sample client is pre-loaded)"
echo "  2. \"Run this plan past the staff meeting\""
echo "  3. \"Onboard <your company>\"                            (starts your real setup)"
echo ""
echo "Uninstall anytime:  claude plugin uninstall bigslick@bigslick"
