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

# Let Claude Code's own output through. Both of these used to be redirected to
# /dev/null 2>&1, which meant that between "Installing Big Slick..." and the
# final summary the user saw nothing at all — indistinguishable from a hang, and
# the single most common reason people asked whether it had actually worked.
# Hiding the output also hid the reason whenever a step failed.
echo ""
echo "${BOLD}Registering the marketplace...${NORM}"
claude plugin marketplace add "$(pwd)" || claude plugin marketplace update bigslick || true

echo ""
echo "${BOLD}Installing the core plugin...${NORM}"
claude plugin install bigslick@bigslick || claude plugin update bigslick@bigslick || {
  echo "Plugin install hit a snag — run manually: claude plugin install bigslick@bigslick"; exit 1; }

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
# Say "core" and name the rest. The old wording was "$SKILLS marketing skills
# installed", and INSTALL.md told people to expect 249 — so they read 32, or
# whatever the lean core happens to be, and reasonably concluded it half-failed.
BUNDLED=$(find bundles -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "${BOLD}Ready.${NORM} $SKILLS core skills installed and enabled."
if [ "${BUNDLED:-0}" -gt 0 ]; then
  echo "$BUNDLED more sit in optional bundles and are NOT installed yet — that is"
  echo "deliberate, so they cost you no context until you ask for them."
fi
echo "Confirm any time with:  claude plugin list"
[ "$ACTIVE" != "none" ] && echo "Active client: $ACTIVE"
echo ""
echo "To start, open Claude in this folder and paste:"
echo ""
echo "    Onboard my company"
echo ""
echo "It interviews you about your business and writes your context pack, so you"
echo "never have to edit files by hand. Every other skill reads what it wrote."
echo "Running marketing for several companies? Say 'Onboard a new client'."
echo ""
# The old smoke test named the fictional sample client, which was removed on
# 2026-09-15 — so it ran against a company that no longer exists and returned
# generic filler, looking precisely like a broken install. This check works with
# no pack present, because client-context exists to announce whether there is one.
echo "Want to confirm it is working first? Paste this instead:"
echo ""
echo "    What do you know about my business?"
echo ""
echo "A working install says it has no context pack yet and points you at the"
echo "skill that fixes it. A generic marketing answer means it is not loaded."
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
