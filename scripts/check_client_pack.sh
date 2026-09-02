#!/usr/bin/env bash
# Did company-onboarding actually produce a usable client pack?
#
#   bash scripts/check_client_pack.sh <company>
#
# The skill is an interview, so "it ran" and "it worked" are different things:
# it can finish the conversation and still leave files that are empty, missing,
# or word-for-word the blank template. This checks the artifacts instead of the
# transcript. Exit 0 = usable, 1 = not.
set -u
NAME="${1:-}"
[ -n "$NAME" ] || { echo "usage: bash scripts/check_client_pack.sh <company>"; exit 2; }
cd "$(dirname "$0")/.."
DIR="core/clients/$NAME"
[ -d "$DIR" ] || { echo "FAIL  no pack at $DIR"; echo "      company-onboarding never wrote one — that is the headline result."; exit 1; }

CORE="product-marketing.md icp.md messaging.md competitors.md voice.md stack.md metrics-baseline.md"
EXTRA="skills-profile.md team-map.md setup-checklist.md"
fails=0; warns=0

echo "Client pack: $DIR"
echo
printf '%-24s %-9s %s\n' FILE STATUS NOTE
for f in $CORE $EXTRA; do
  p="$DIR/$f"
  req="required"; case " $EXTRA " in *" $f "*) req="optional";; esac
  if [ ! -f "$p" ]; then
    if [ "$req" = required ]; then printf '%-24s %-9s %s\n' "$f" MISSING "required"; fails=$((fails+1))
    else printf '%-24s %-9s %s\n' "$f" "-" "optional, not written"; fi
    continue
  fi
  # Content, ignoring headings, blank lines and the template's own filler.
  body=$(grep -vE '^\s*$|^#|^\s*>|\(fill in\)' "$p" | grep -vE '^\s*-\s*[A-Za-z /&]+:\s*$' | wc -l | tr -d ' ')
  if grep -q '{CLIENT NAME}' "$p"; then
    printf '%-24s %-9s %s\n' "$f" TEMPLATE "still the blank scaffold"; fails=$((fails+1))
  elif [ "$body" -lt 3 ]; then
    printf '%-24s %-9s %s\n' "$f" THIN "$body lines of real content"; warns=$((warns+1))
  else
    tbd=$(grep -ci 'TBD' "$p" 2>/dev/null); tbd=${tbd:-0}
    note="$body lines"; [ "$tbd" -gt 0 ] && note="$note, $tbd TBD"
    printf '%-24s %-9s %s\n' "$f" OK "$note"
  fi
done

echo
# The pack is only reachable by skills once it's the active client.
ACTIVE=$(basename "$(readlink core/clients/_active 2>/dev/null || echo none)")
if [ "$ACTIVE" = "$NAME" ]; then
  if [ -e .agents/product-marketing.md ]; then echo "Activation   OK        active, and .agents/product-marketing.md resolves"
  else echo "Activation   BROKEN    active but .agents/product-marketing.md is missing"; fails=$((fails+1)); fi
else
  echo "Activation   NOT ACTIVE  active client is '$ACTIVE' — run: bash scripts/activate_client.sh $NAME"
  warns=$((warns+1))
fi

echo
if [ "$fails" -gt 0 ]; then
  echo "RESULT: NOT USABLE — $fails blocking, $warns warnings."
  echo "A missing or still-template file means that part of the interview did not land."
  exit 1
fi
[ "$warns" -gt 0 ] && echo "RESULT: USABLE, $warns thin/inactive warnings — fill the gaps or re-run onboarding on them." \
                   || echo "RESULT: USABLE — every required file written and populated."
exit 0
