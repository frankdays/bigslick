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
