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
# T4 — everything shipped must be redistributable. Vendored upstreams are MIT/Apache-2.0;
# the first-party core/ layer is MIT under the root LICENSE. What must never come back is
# the source-available Reserved Component License removed in v0.2, so fail on any
# per-skill LICENSE.md in core/skills and on any provenance we don't recognise.
known={"marketingskills","openclaudia","anthropic-marketing","goose-skills","kostja-marketing","rampstack","wondel","core"}
bad_prov=sorted({n for n,src in prov.items() if src.replace("+patch","") not in known})
# Scan for an actual source-available LICENCE GRANT, not merely the words. Docs like
# LICENSING.md legitimately describe the removed licence in prose and must not trip this;
# a file *named* LICENSE that grants source-available terms is the thing that must never
# ship. The earlier version only checked core/skills/*/LICENSE.md and missed a stray
# core/clients/LICENSE.md sitting over the sample packs that DO ship in the release.
reserved=[]
for base in ["skills","bundles","core","."]:
    b=Path(base)
    if not b.exists(): continue
    for f in ([b] if b.is_file() else b.rglob("*")):
        if not f.is_file() or f.name.split(".")[0].upper() not in ("LICENSE","LICENCE","COPYING"): continue
        if any(part in ("upstream","licenses",".git") for part in f.parts): continue
        try: body=f.read_text(errors="ignore")
        except Exception: continue
        if "Reserved Component" in body or "NOT open source" in body: reserved.append(str(f))
reserved=sorted(set(reserved))
t4 = not bad_prov and not reserved
detail = "" if t4 else f"FAIL unknown={bad_prov[:5]} source-available-licence={reserved[:5]}"
print(f"T4 redistributable provenance ({len(prov)})", "PASS" if t4 else detail); fails+= [] if t4 else ["T4"]
# T5 — INVENTORY.md must document every composed skill (source/licence/deps).
inv=Path("INVENTORY.md")
if inv.exists():
    txt=inv.read_text()
    undoc=[d.name for d in skills if f"`{d.name}`" not in txt]
    print(f"T5 inventory coverage", "PASS" if not undoc else f"FAIL {len(undoc)} undocumented {undoc[:5]}"); fails+= [] if not undoc else ["T5"]
else:
    print("T5 inventory coverage FAIL (INVENTORY.md missing)"); fails+=["T5"]
p=json.load(open("dist/.claude-plugin/plugin.json")); mk=json.load(open(".claude-plugin/marketplace.json"))
ok = p["name"]=="bigslick" and mk["plugins"][0]["source"]=="."
print("T6 manifests", "PASS" if ok else "FAIL"); fails+= [] if ok else ["T6"]
# T7 — the repo root must be a valid plugin that is actually COMMITTED. dist/ is
# gitignored, so a marketplace pointing into it installs from a local checkout and 404s
# from GitHub. Checking the working tree is not enough: compose.py runs at the top of
# this script and would recreate skills/ every time, so the assertion that matters is
# what git tracks. Uncommitted skills/ is the exact state that breaks the public install.
import subprocess
rp=Path(".claude-plugin/plugin.json"); rs=Path("skills")
mk_src={pl["name"]: pl["source"] for pl in mk["plugins"]}
t7=[]
if not rp.exists(): t7.append(".claude-plugin/plugin.json missing")
if not rs.exists(): t7.append("skills/ missing")

# Every published plugin root must exist, and together they must partition dist/ exactly:
# no skill shipped twice (installing two bundles would register a duplicate name) and none
# dropped on the floor (composed but unreachable by any install).
published={}
for pname, src in mk_src.items():
    root=Path(src)
    if not (root/".claude-plugin"/"plugin.json").exists(): t7.append(f"{pname}: no plugin.json at {src}")
    sd=root/"skills"
    if not sd.is_dir(): t7.append(f"{pname}: no skills/ at {src}"); continue
    for d in sd.iterdir():
        if d.is_dir():
            if d.name in published: t7.append(f"{d.name} in both {published[d.name]} and {pname}")
            published[d.name]=pname
composed={d.name for d in skills}
missing=sorted(composed-set(published)); extra=sorted(set(published)-composed)
if missing: t7.append(f"{len(missing)} composed but unpublished e.g. {missing[:3]}")
if extra: t7.append(f"published but not composed: {extra[:3]}")

try:
    g=subprocess.run(["git","ls-files","skills","bundles"],capture_output=True,text=True,timeout=30)
    if g.returncode==0:
        tracked={l for l in g.stdout.splitlines()}
        if not any(l.startswith("skills/") for l in tracked):
            t7.append("skills/ is not committed — GitHub install would 404")
        if mk_src and not any(l.startswith("bundles/") for l in tracked):
            t7.append("bundles/ is not committed — bundle installs would 404")
except Exception as e:
    print(f"  (T7 git check skipped: {e})")
print(f"T7 plugin roots ({len(mk_src)} plugins, {len(published)} skills)", "PASS" if not t7 else f"FAIL {t7}"); fails+= [] if not t7 else ["T7"]
sys.exit(1 if fails else 0)
PY
# F1 client lifecycle
cp -r core/clients/_template core/clients/__testco 2>/dev/null || true
bash scripts/activate_client.sh __testco >/dev/null && [ -e .agents/product-marketing.md ] && echo "F1 client lifecycle PASS" || { echo "F1 FAIL"; exit 1; }
rm -rf core/clients/__testco core/clients/_active .agents
[ -d core/clients/hansel-ai ] && bash scripts/activate_client.sh hansel-ai >/dev/null || true
echo "ALL TESTS PASS"
