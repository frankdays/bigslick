# BUILD-BIGSLICK.md — Executable Build Specification v0.1
**Run this with Claude Code.** Put this file in a working folder and say: *"Execute BUILD-BIGSLICK.md exactly. Run each phase in order, verify each checkpoint, and stop and report if a checkpoint fails."*

## Agent operating rules (read first)
1. Execute phases **in order**; after each, run its CHECKPOINT and confirm expected output before continuing.
2. Embedded file contents below are **canonical** — write them verbatim (overwrite existing copies of the same files). Do not improvise, "improve," or reformat them.
3. **Never modify anything under `upstream/`** and **never modify the content of existing `core/skills/*/SKILL.md` files** (they are frozen shipped assets) — the only files this build may add inside core are `LICENSE.md` notices.
4. The build is idempotent — safe to re-run; it converges to the same state.
5. If a network clone fails, retry once, then stop and report which domain failed.

---

## Phase 1 — Acquire the core layer (the frozen proprietary skills)
The 28 core skills, client-pack template, sample client, and docs **cannot be regenerated from this spec** — they are acquired from an existing copy. Detect, in order:

```bash
set -e
if   [ -d bigslick/core/skills ]; then cd bigslick
elif [ -d mkt-core/core/skills ]; then mv mkt-core bigslick && cd bigslick
elif [ -f mkt-core.zip ]; then unzip -q mkt-core.zip && mv mkt-core bigslick && cd bigslick
elif [ -f bigslick.zip ];  then unzip -q bigslick.zip && cd bigslick
else echo "HALT: no core layer found. Place the bigslick/ or mkt-core/ folder (or its zip) beside this file and re-run."; exit 1; fi
echo "CORE OK: $(ls core/skills | wc -l) core skill folders"
```
**CHECKPOINT 1:** prints `CORE OK:` with **28** folders (accept 20–32; if outside that range, stop and report the folder list). All later phases run from inside this `bigslick/` directory.

## Phase 2 — Vendor upstreams at pinned SHAs
```bash
mkdir -p upstream licenses && rm -rf upstream/marketingskills upstream/openclaudia-skills upstream/anthropic-marketing /tmp/kwp
: > upstream/VERSIONS
git clone -q https://github.com/coreyhaines31/marketingskills upstream/marketingskills
git -C upstream/marketingskills checkout -q 3df87f97621e18fbed7f6aa684edba54f49779a7 || echo "WARN: pinned SHA missing; using HEAD $(git -C upstream/marketingskills rev-parse HEAD)"
echo "coreyhaines31/marketingskills $(git -C upstream/marketingskills rev-parse HEAD)" >> upstream/VERSIONS
git clone -q https://github.com/OpenClaudia/openclaudia-skills upstream/openclaudia-skills
git -C upstream/openclaudia-skills checkout -q 285676555938fc47446b396c40a56356b850cba8 || echo "WARN: pinned SHA missing; using HEAD"
echo "OpenClaudia/openclaudia-skills $(git -C upstream/openclaudia-skills rev-parse HEAD)" >> upstream/VERSIONS
git clone -q https://github.com/anthropics/knowledge-work-plugins /tmp/kwp
git -C /tmp/kwp checkout -q 5267cf7bff3031921d4474b8e8f86ad02d2b8f6d || echo "WARN: pinned SHA missing; using HEAD"
mkdir -p upstream/anthropic-marketing && cp -r /tmp/kwp/marketing/. upstream/anthropic-marketing/ && cp /tmp/kwp/LICENSE upstream/anthropic-marketing/LICENSE
echo "anthropics/knowledge-work-plugins(marketing) $(git -C /tmp/kwp rev-parse HEAD)" >> upstream/VERSIONS
rm -rf upstream/marketingskills/.git upstream/openclaudia-skills/.git /tmp/kwp
cp upstream/marketingskills/LICENSE licenses/LICENSE-coreyhaines-marketingskills 2>/dev/null || true
cp upstream/openclaudia-skills/LICENSE licenses/LICENSE-openclaudia 2>/dev/null || true
cp upstream/anthropic-marketing/LICENSE licenses/LICENSE-anthropic 2>/dev/null || true
cat upstream/VERSIONS
```
**CHECKPOINT 2:** `VERSIONS` shows three entries; `ls upstream/marketingskills/skills | wc -l` ≈ 49; `ls upstream/openclaudia-skills/skills | wc -l` ≈ 75. If WARN lines appeared, note them in the final report (curation counts may drift).

## Phase 3 — Write canonical build files
Write each file below **exactly**.

### 3.1 `overlay/manifest.yaml`
```bash
mkdir -p overlay/patches overlay/plugin && cat > overlay/manifest.yaml << 'EOF'
# Overlay manifest — v0.1 (inventory of 2026-08-22). Precedence: core > patches > later upstream > earlier.
upstreams:
  - name: marketingskills
    path: upstream/marketingskills/skills
    mode: all
    exclude: []
  - name: openclaudia
    path: upstream/openclaudia-skills/skills
    mode: all
    exclude:
      [seo-audit, copywriting, copy-editing, product-marketing, programmatic-seo,
       content-strategy, marketing-ideas, launch-strategy, pricing-strategy,
       page-cro, signup-flow-cro, onboarding-cro, schema-markup, lead-magnet,
       referral-program, social-content, competitor-analysis,
       task-banner, organize-skills, github-stars, stripe-dispute, feishu-lark,
       wechat-moments]
  - name: anthropic-marketing
    path: upstream/anthropic-marketing/skills
    mode: include
    include: [brand-review, campaign-plan, performance-report]
core:
  path: core/skills
EOF
```

### 3.2 `overlay/plugin/plugin.json` and `.claude-plugin/marketplace.json`
```bash
cat > overlay/plugin/plugin.json << 'EOF'
{
  "name": "bigslick",
  "version": "0.1.0",
  "description": "Big Slick: the open-source marketing distribution for Claude. 132 skills spanning pipeline models, board reporting, ABM, field marketing, win-loss, case studies, PR/AR, and an AI-visibility (GEO) system — with a marketing leadership persona layer (staff meetings on demand) and swappable per-company context packs.",
  "author": { "name": "Frank Days" }
}
EOF
mkdir -p .claude-plugin && cat > .claude-plugin/marketplace.json << 'EOF'
{
  "name": "bigslick",
  "owner": { "name": "Frank Days" },
  "plugins": [
    { "name": "bigslick",
      "displayName": "Big Slick — Marketing Distribution",
      "source": "./dist",
      "description": "The open-source marketing distribution for Claude: 132 curated + proprietary skills plus a marketing leadership persona layer and per-company context packs. The best starting hand a marketer can be dealt." }
  ]
}
EOF
```

### 3.3 `scripts/compose.py`
```bash
mkdir -p scripts && cat > scripts/compose.py << 'EOF'
#!/usr/bin/env python3
"""Compose dist/skills from upstream + overlay + core. Later layers win; core wins all."""
import argparse, shutil, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml first")
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "skills"

def skill_dirs(p): return sorted(d for d in p.iterdir() if d.is_dir() and (d/"SKILL.md").exists())

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    m = yaml.safe_load((ROOT/"overlay"/"manifest.yaml").read_text())
    plan, prov, new_up = {}, {}, []
    for up in m["upstreams"]:
        base = ROOT/up["path"]
        if not base.exists(): print(f"WARN missing upstream {up['name']}"); continue
        names = {d.name: d for d in skill_dirs(base)}
        if up.get("mode") == "include":
            chosen = {n: names[n] for n in up.get("include", []) if n in names}
            new_up += [f"{up['name']}/{n}" for n in names if n not in set(up.get("include", []))]
        else:
            excl = set(up.get("exclude", []))
            chosen = {n: d for n, d in names.items() if n not in excl}
        for n, d in chosen.items():
            if n in plan: print(f"  collision: {n} ({prov[n]} -> {up['name']}) — later wins")
            plan[n], prov[n] = d, up["name"]
    for d in skill_dirs(ROOT/m["core"]["path"]): plan[d.name], prov[d.name] = d, "core"
    if a.check:
        print(f"Would compose {len(plan)} skills.")
        if new_up: print(f"Upstream skills NOT in manifest include-lists (review after updates): {new_up}")
        c = {}
        for s in prov.values(): c[s] = c.get(s, 0)+1
        [print(f"  {k}: {v}") for k, v in sorted(c.items())]; return
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for name, src in sorted(plan.items()):
        shutil.copytree(src, DIST/name)
        patch = ROOT/"overlay"/"patches"/name
        if patch.exists(): shutil.copytree(patch, DIST/name, dirs_exist_ok=True); prov[name] += "+patch"
    (ROOT/"dist"/"PROVENANCE.txt").write_text("\n".join(f"{n}\t{prov[n]}" for n in sorted(plan))+"\n")
    ps = ROOT/"overlay"/"plugin"/"plugin.json"
    if ps.exists():
        dest = ROOT/"dist"/".claude-plugin"; dest.mkdir(exist_ok=True); shutil.copy(ps, dest/"plugin.json")
    rd = ROOT/"overlay"/"plugin"/"README.md"
    if rd.exists(): shutil.copy(rd, ROOT/"dist"/"README.md")
    print(f"Composed {len(plan)} skills into dist/skills/ (installable plugin; provenance: dist/PROVENANCE.txt)")

if __name__ == "__main__": main()
EOF
```

### 3.4 `scripts/activate_client.sh`
```bash
cat > scripts/activate_client.sh << 'EOF'
#!/usr/bin/env bash
# Usage: ./scripts/activate_client.sh <client-folder-name>   (relative symlinks — repo can move)
set -e
LIB="$(cd "$(dirname "$0")/.." && pwd)"
CLIENT_DIR="$LIB/core/clients/$1"
[ -d "$CLIENT_DIR" ] || { echo "No such client pack: $CLIENT_DIR"; ls "$LIB/core/clients"; exit 1; }
mkdir -p "$LIB/.agents"
ln -sfn "../core/clients/$1/product-marketing.md" "$LIB/.agents/product-marketing.md"
ln -sfn "$1" "$LIB/core/clients/_active"
echo "Active client: $1"
EOF
chmod +x scripts/activate_client.sh
```

### 3.5 `scripts/update_upstreams.sh`
```bash
cat > scripts/update_upstreams.sh << 'EOF'
#!/usr/bin/env bash
# Re-vendor upstreams at latest; report skill add/removes vs current; rewrite VERSIONS. Then edit manifest & recompose.
set -e
cd "$(dirname "$0")/.."
> upstream/VERSIONS.new
revendor(){ # $1 dir  $2 repo  $3 subpath(optional)
  tmp=$(mktemp -d); git clone -q --depth 1 "https://github.com/$2.git" "$tmp"
  sha=$(git -C "$tmp" rev-parse HEAD); src="$tmp/${3:-.}"
  echo "== $1 -> $sha"
  diff <(ls "upstream/$1/skills" 2>/dev/null) <(ls "$src/skills") | grep '^[<>]' || echo "   (no skill add/removes)"
  rm -rf "upstream/$1"; mkdir -p "upstream/$1"; cp -r "$src/." "upstream/$1/"
  [ -f "$tmp/LICENSE" ] && cp "$tmp/LICENSE" "upstream/$1/LICENSE"
  rm -rf "$tmp"; rm -rf "upstream/$1/.git"
  echo "$2${3:+($3)} $sha" >> upstream/VERSIONS.new
}
revendor marketingskills coreyhaines31/marketingskills
revendor openclaudia-skills OpenClaudia/openclaudia-skills
revendor anthropic-marketing anthropics/knowledge-work-plugins marketing
mv upstream/VERSIONS.new upstream/VERSIONS
echo "Done. Review add/removes above, update overlay/manifest.yaml, then: python3 scripts/compose.py"
EOF
chmod +x scripts/update_upstreams.sh
```

### 3.6 `install.sh` and `INSTALL.command`
```bash
cat > install.sh << 'EOF'
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
if [ ! -d dist/skills ]; then
  command -v python3 >/dev/null && pip3 install -q pyyaml && python3 scripts/compose.py \
    || { echo "dist/skills missing and couldn't rebuild — re-download the package."; exit 1; }
fi
claude plugin marketplace add "$(pwd)" >/dev/null 2>&1 || claude plugin marketplace update bigslick >/dev/null 2>&1 || true
claude plugin install bigslick@bigslick >/dev/null 2>&1 || claude plugin update bigslick@bigslick >/dev/null 2>&1 || {
  echo "Plugin install hit a snag — run manually: claude plugin install bigslick@bigslick"; exit 1; }
[ -d core/clients/hansel-ai ] && bash scripts/activate_client.sh hansel-ai >/dev/null || true
echo ""; echo "${BOLD}Done. $(find dist/skills -name SKILL.md | wc -l | tr -d ' ') marketing skills installed.${NORM}"
echo ""; echo "Open Terminal here, type ${BOLD}claude${NORM}, and try:"
echo "  1. \"Build the pipeline model for Hansel AI's year\"   (sample client pre-loaded)"
echo "  2. \"Run this plan past the staff meeting\""
echo "  3. \"Onboard <your company>\"                          (your real setup)"
echo ""; echo "Uninstall anytime:  claude plugin uninstall bigslick@bigslick"
EOF
chmod +x install.sh
printf '#!/usr/bin/env bash\ncd "$(dirname "$0")" && bash install.sh\necho ""\nread -p "Press Enter to close..."\n' > INSTALL.command
chmod +x INSTALL.command
```

### 3.7 `.gitignore` and licensing (Option A open-core)
```bash
cat > .gitignore << 'EOF'
core/clients/*
!core/clients/_template/
!core/clients/hansel-ai/
core/clients/_active
.agents/
dist/
.env
*.key
EOF
YEAR=$(date +%Y); OWNER="Frank Days"
cat > LICENSE << EOF
MIT License

Copyright (c) $YEAR $OWNER

SCOPE NOTE: This MIT license applies to all contents of this repository EXCEPT
(a) directories containing their own LICENSE.md (see LICENSING.md), and
(b) vendored third-party content under upstream/, which retains its original
licenses (preserved in each upstream folder and in licenses/).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
read -r -d '' RES << EOF || true
# Big Slick Reserved Component License (v0.1)
Copyright (c) $YEAR $OWNER. All rights reserved, except as granted below.
Source-available, NOT open source.
YOU MAY, free of charge: use this component as part of the Big Slick
distribution for yourself, your company's internal business, or client
engagements you personally serve; read and modify it for that use.
YOU MAY NOT, without a commercial license: redistribute this component
(modified or not) outside the official Big Slick distribution; offer it or a
derivative as part of a competing product, template pack, hosted service, or
paid offering; remove this notice.
Commercial licensing: contact the copyright holder. No warranty. Plain-language
terms, not attorney-reviewed; may be replaced by formal terms in future versions.
EOF
for d in core/skills/company-onboarding core/skills/staff-meeting core/clients core/skills/persona-*; do
  [ -d "$d" ] && printf '%s\n' "$RES" > "$d/LICENSE.md"
done
cat > LICENSING.md << 'EOF'
# Licensing Map — Big Slick (open-core)
MIT (root LICENSE): compose/installer/scripts, resource-hub, all function skills, docs.
Reserved Component License (LICENSE.md in each dir): core/skills/company-onboarding, core/clients,
core/skills/persona-*, core/skills/staff-meeting — free for individuals, internal company use, and a
practitioner's own client work; no redistribution outside the distribution; no competing products.
upstream/*: original upstream licenses preserved (also in licenses/). PRs welcome on MIT paths only (v0.1).
EOF
```

### 3.8 `scripts/test.sh` (release gate)
```bash
cat > scripts/test.sh << 'EOF'
#!/usr/bin/env bash
set -e; cd "$(dirname "$0")/.."
python3 scripts/compose.py >/dev/null
python3 - << 'PY'
import yaml, re, json, sys
from pathlib import Path
dist = Path("dist/skills"); fails=[]
skills = sorted(d for d in dist.iterdir() if d.is_dir())
prov = dict(l.split("\t") for l in Path("dist/PROVENANCE.txt").read_text().splitlines())
print(f"T1 composed {len(skills)} skills; provenance {len(prov)}", "PASS" if len(skills)==len(prov) else "FAIL"); fails+= [] if len(skills)==len(prov) else ["T1"]
bad=[]
for d in skills:
    m = re.match(r"^---\n(.*?)\n---\n", (d/"SKILL.md").read_text(), re.S)
    try: fm = yaml.safe_load(m.group(1)); assert fm.get("description")
    except Exception: bad.append(d.name)
print(f"T2 frontmatter invalid: {len(bad)}", "PASS" if not bad else f"FAIL {bad[:5]}"); fails+= [] if not bad else ["T2"]
leak=[e for e in ["task-banner","wechat-moments","feishu-lark","launch-strategy"] if (dist/e).exists()]
print("T3 exclusions", "PASS" if not leak else f"FAIL {leak}"); fails+= [] if not leak else ["T3"]
core=[d.name for d in Path("core/skills").iterdir() if (d/"SKILL.md").exists()]
miss=[n for n in core if prov.get(n)!="core"]
print(f"T4 core precedence ({len(core)})", "PASS" if not miss else f"FAIL {miss}"); fails+= [] if not miss else ["T4"]
p=json.load(open("dist/.claude-plugin/plugin.json")); mk=json.load(open(".claude-plugin/marketplace.json"))
ok = p["name"]=="bigslick" and mk["plugins"][0]["source"]=="./dist"
print("T6 manifests", "PASS" if ok else "FAIL"); fails+= [] if ok else ["T6"]
sys.exit(1 if fails else 0)
PY
# F1 client lifecycle
cp -r core/clients/_template core/clients/__testco 2>/dev/null || true
bash scripts/activate_client.sh __testco >/dev/null && [ -e .agents/product-marketing.md ] && echo "F1 client lifecycle PASS" || { echo "F1 FAIL"; exit 1; }
rm -rf core/clients/__testco core/clients/_active .agents
[ -d core/clients/hansel-ai ] && bash scripts/activate_client.sh hansel-ai >/dev/null || true
echo "ALL TESTS PASS"
EOF
chmod +x scripts/test.sh
```
**CHECKPOINT 3:** all files exist; `bash -n install.sh scripts/*.sh` reports no syntax errors.

## Phase 4 — Compose, test, package
```bash
pip3 install -q pyyaml 2>/dev/null || pip install -q pyyaml --break-system-packages
python3 scripts/compose.py
bash scripts/test.sh
( cd dist && rm -f ../bigslick.plugin && zip -qr ../bigslick.plugin . -x "*.DS_Store" )
ls -la bigslick.plugin && head -3 dist/PROVENANCE.txt
```
**CHECKPOINT 4:** compose reports ~**132 skills** (exact count depends on SHA pinning warnings from Phase 2); `test.sh` ends with `ALL TESTS PASS`; `bigslick.plugin` exists.

## Phase 5 — Install and version control
```bash
# Install into Claude Code if the CLI is present (skip silently otherwise)
command -v claude >/dev/null && { claude plugin marketplace add "$(pwd)" 2>/dev/null || true; claude plugin install bigslick@bigslick 2>/dev/null || claude plugin update bigslick@bigslick 2>/dev/null || true; claude plugin list | grep -A1 bigslick || true; }
# Git
git init -q 2>/dev/null || true
git add -A && git commit -q -m "Big Slick v0.1 — built from BUILD-BIGSLICK.md ($(date +%F))" || echo "(nothing new to commit)"
git branch -M main
# If a remote is configured, push; otherwise report the command for the user:
git remote get-url origin >/dev/null 2>&1 && git push -u origin main && git tag -f v0.1 && git push -f origin v0.1 \
  || echo "To publish: git remote add origin https://github.com/<user>/bigslick.git && git push -u origin main"
```
**CHECKPOINT 5:** plugin listed as enabled (if CLI present); git committed.

## Final report (produce this for the user)
1. Skill count composed + provenance breakdown (core / marketingskills / openclaudia / anthropic-marketing counts)
2. Any SHA-pinning WARNs from Phase 2 (means upstream drifted; counts may differ from 132)
3. Test results (all gates)
4. Install state (plugin enabled? sample client active?)
5. Git state (committed? pushed?)
6. Anything this build could NOT do (e.g., no core layer found; no claude CLI; no git remote) with the exact next command for the user.
