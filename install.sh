#!/usr/bin/env bash
# Big Slick installer — sets up everything. Safe to re-run.
set -e
cd "$(dirname "$0")"
BOLD=$(tput bold 2>/dev/null || true); NORM=$(tput sgr0 2>/dev/null || true)
echo "${BOLD}Installing Big Slick...${NORM}"

if ! command -v claude >/dev/null 2>&1; then
  echo ""; echo "Claude Code isn't installed yet:"
  echo "  A) With Node.js:  npm install -g @anthropic-ai/claude-code"
  echo "  B) Download:      https://claude.com/claude-code"
  echo "Then run this installer again."; exit 1
fi

# The downloaded package ships skills/ prebuilt, so there is nothing to build and
# no Python needed. Only a source checkout with an unbuilt tree hits this branch.
if [ ! -d skills ]; then
  if [ -f scripts/compose.py ] && command -v python3 >/dev/null; then
    pip3 install -q pyyaml && python3 scripts/compose.py
  else
    echo "skills/ is missing and this package can't rebuild it — re-download Big Slick."; exit 1
  fi
fi

claude plugin marketplace add "$(pwd)" >/dev/null 2>&1 || claude plugin marketplace update bigslick >/dev/null 2>&1 || true
claude plugin install bigslick@bigslick >/dev/null 2>&1 || claude plugin update bigslick@bigslick >/dev/null 2>&1 || {
  echo "Plugin install hit a snag — run manually: claude plugin install bigslick@bigslick"; exit 1; }
[ -d core/clients/hansel-ai ] && bash scripts/activate_client.sh hansel-ai >/dev/null 2>&1 || true

# Verify rather than assume. "Done" printed over a failed install is worse than
# an error, because the user only finds out when a skill silently never fires.
SKILLS=$(find skills -name SKILL.md | wc -l | tr -d ' ')
PROBLEMS=""
claude plugin list 2>/dev/null | grep -q "bigslick@bigslick" || PROBLEMS="the plugin did not register"
[ "$SKILLS" -gt 0 ] || PROBLEMS="${PROBLEMS:+$PROBLEMS; }no skills found in skills/"
if [ -n "$PROBLEMS" ]; then
  echo ""; echo "Installed with problems — $PROBLEMS."
  echo "Try:  claude plugin install bigslick@bigslick"; exit 1
fi

ACTIVE=$(basename "$(readlink core/clients/_active 2>/dev/null || echo none)")
echo ""
echo "${BOLD}Ready.${NORM} $SKILLS marketing skills installed and enabled."
[ "$ACTIVE" != "none" ] && echo "Sample company loaded: $ACTIVE"
echo ""
echo "To start, open Claude in this folder and paste one of these:"
echo ""
echo "    Build a marketing plan for Hansel AI"
echo "    Define the ICP for Hansel AI"
echo "    Run this plan past the marketing council"
echo ""
echo "Those run against the sample company. For your own, run:"
echo ""
echo "    Onboard my company"
echo ""
echo "It interviews you and writes your company's context pack, so you never"
echo "have to edit files by hand."
echo ""
echo "Big Slick installs lean — $SKILLS core skills. Add a specialty when you need it:"
echo ""
echo "    claude plugin install bigslick-seo@bigslick"
echo "    claude plugin install bigslick-paid@bigslick"
echo ""
echo "Also available: ai-search, content, social, gtm, lifecycle, strategy,"
echo "research, ops. Each one only costs you context once installed."
echo ""
echo "Not sure how to open Claude here? Run:  claude"
echo "Uninstall anytime:  claude plugin uninstall bigslick@bigslick"
