#!/usr/bin/env python3
"""Generate INVENTORY.md — every composed skill with its source, licence and external deps.

Reads dist/ (so it reflects what actually ships) plus overlay/manifest.yaml and
upstream/VERSIONS for provenance. Re-run after any manifest or upstream change:

    python3 scripts/compose.py && python3 scripts/gen_inventory.py

`scripts/test.sh` (T5) fails if a composed skill has no row here.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "skills"

# name -> (repo, licence, stars, one-line description of the slice we take)
UPSTREAMS = {
    "marketingskills":     ("coreyhaines31/marketingskills",      "MIT",        "46.1k"),
    "openclaudia":         ("OpenClaudia/openclaudia-skills",     "MIT",        "666"),
    "anthropic-marketing": ("anthropics/knowledge-work-plugins",  "Apache-2.0", "23.8k"),
    "goose-skills":        ("gooseworks-ai/goose-skills",         "MIT",        "1.2k"),
    "kostja-marketing":    ("kostja94/marketing-skills",          "MIT",        "936"),
    "rampstack":           ("rampstackco/claude-skills",          "MIT",        "786"),
    "wondel":              ("wondelai/skills",                    "MIT",        "2.1k"),
    # First-party infrastructure, MIT under the repo root LICENSE — not vendored,
    # so it has no upstream repo or star count of its own.
    "core":                ("frankdays/bigslick (first-party)",   "MIT",        "—"),
}

TEXT_SUFFIXES = {".md", ".py", ".sh", ".yaml", ".yml", ".json", ".txt", ".js", ".ts"}

# An upstream naming its own repo in an install line is self-reference, not a dependency.
SELF_NAMES = {"goose-skills", "marketing-skills", "claude-skills", "skills",
              "openclaudia-skills", "marketingskills", "knowledge-work-plugins"}

# Env vars that are Claude Code's own, not an external dependency the user must supply.
ENV_IGNORE = {"CLAUDE_PLUGIN_ROOT", "CLAUDE_PROJECT_DIR", "CLAUDE_CODE_ENTRYPOINT",
              "BASH_MAX_TIMEOUT_MS", "HOME", "PATH", "PWD", "USER", "SHELL", "LANG",
              "TMPDIR", "EDITOR", "HTTP_PROXY", "HTTPS_PROXY", "NO_COLOR",
              # API filter operators and schema words that match the env-var shape but
              # are values in a request body, not variables anyone has to set.
              "CONTAINS_TOKEN", "NOT_CONTAINS_TOKEN", "DOES_NOT_CONTAIN_TOKEN",
              "ACCESS_TOKEN", "REFRESH_TOKEN", "BEARER_TOKEN", "YOUR_TOKEN",
              "YOUR_API_KEY", "API_KEY", "SECRET_KEY", "PRIVATE_KEY", "PUBLIC_KEY"}

ENV_RE = re.compile(r"\b([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_(?:API_KEY|KEY|TOKEN|SECRET|"
                    r"PASSWORD|ACCESS_KEY|CLIENT_ID|CLIENT_SECRET|WEBHOOK|ENDPOINT))\b")
MCP_RE = re.compile(r"mcp__([a-zA-Z0-9_\-]+?)__")
PIP_RE = re.compile(r"pip3?\s+install\s+(?:-U\s+|--upgrade\s+)?([a-zA-Z0-9_\-\[\]]+)")
NPM_RE = re.compile(r"(?:npm\s+i(?:nstall)?|npx|pnpm\s+add|yarn\s+add)\s+(?:-g\s+)?"
                    r"(@?[a-zA-Z0-9_\-/\.]+)")
HOST_RE = re.compile(r"https?://((?:api|graph|ads)\.[a-z0-9\-]+\.[a-z]{2,})")


def scan(skill_dir):
    """Return (env_vars, mcp_servers, packages, api_hosts) referenced by a skill."""
    env, mcp, pkg, host = set(), set(), set(), set()
    for f in skill_dir.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            t = f.read_text(errors="ignore")
        except Exception:
            continue
        env |= {m for m in ENV_RE.findall(t) if m not in ENV_IGNORE}
        mcp |= set(MCP_RE.findall(t))
        pkg |= {p for p in PIP_RE.findall(t) if len(p) > 1}
        pkg |= {p for p in NPM_RE.findall(t) if len(p) > 1 and not p.startswith(".")}
        host |= set(HOST_RE.findall(t))
    return env, mcp, pkg - SELF_NAMES, host


def deps_cell(env, mcp, pkg, host):
    bits = []
    if env:
        bits.append("env: " + ", ".join(f"`{e}`" for e in sorted(env)[:6]))
    if mcp:
        bits.append("MCP: " + ", ".join(f"`{m}`" for m in sorted(mcp)[:4]))
    if pkg:
        bits.append("pkg: " + ", ".join(f"`{p}`" for p in sorted(pkg)[:4]))
    if host:
        bits.append("API: " + ", ".join(sorted(host)[:4]))
    return "; ".join(bits) if bits else "none"


def main():
    if not DIST.exists():
        sys.exit("dist/skills missing — run python3 scripts/compose.py first")
    prov = dict(l.split("\t") for l in
                (ROOT / "dist" / "PROVENANCE.txt").read_text().splitlines() if "\t" in l)
    versions = {}
    for line in (ROOT / "upstream" / "VERSIONS").read_text().splitlines():
        if " " in line:
            repo, sha = line.rsplit(" ", 1)
            versions[repo.split("(")[0]] = sha

    rows, tally, dep_count = [], {}, 0
    for d in sorted(p for p in DIST.iterdir() if p.is_dir()):
        src = prov.get(d.name, "unknown")
        patched = src.endswith("+patch")
        base = src.replace("+patch", "")
        repo, lic, stars = UPSTREAMS.get(base, ("unknown", "unknown", "—"))
        env, mcp, pkg, host = scan(d)
        cell = deps_cell(env, mcp, pkg, host)
        if cell != "none":
            dep_count += 1
        tally[base] = tally.get(base, 0) + 1
        rows.append((d.name, repo, lic, cell, patched))

    out = []
    out.append("# Skill Inventory — Big Slick\n")
    out.append(f"Every skill that ships in `dist/skills/`: **{len(rows)} skills**, "
               "with its upstream source, licence, and the external services it needs.\n")
    out.append("Generated by `scripts/gen_inventory.py` — do not hand-edit. Regenerate with:\n")
    out.append("```bash\npython3 scripts/compose.py && python3 scripts/gen_inventory.py\n```\n")
    out.append("`scripts/test.sh` fails if a composed skill is missing from this file.\n")

    out.append("## Sources\n")
    out.append("Curation bar for an upstream: **≥500 GitHub stars** and a licence that permits "
               "redistribution (MIT or Apache-2.0). Star counts recorded at vendoring time.\n")
    out.append("| Upstream | Repo | Licence | Stars | Skills | Pinned commit |")
    out.append("|---|---|---|---|---|---|")
    for name, (repo, lic, stars) in UPSTREAMS.items():
        sha = versions.get(repo, "—")[:10]
        out.append(f"| `{name}` | [{repo}](https://github.com/{repo}) | {lic} | {stars} | "
                   f"{tally.get(name, 0)} | `{sha}` |")
    out.append("")
    out.append("Licence texts ship in `licenses/` and in each `upstream/<name>/LICENSE`.\n")

    out.append("## External dependencies\n")
    out.append(f"{dep_count} of {len(rows)} skills reference something outside the repo. "
               "A skill with `none` runs on Claude alone — no keys, no network services.\n")
    out.append("- **env** — environment variables you must set (API keys and tokens)\n"
               "- **MCP** — an MCP server that must be connected\n"
               "- **pkg** — a pip/npm package the skill installs or imports\n"
               "- **API** — a third-party HTTP API the skill calls\n")
    out.append("Detected by static scan of each skill's files; treat it as a strong hint, "
               "not a contract. A skill listing an API key will degrade or fail without it.\n")

    out.append("## Skills\n")
    out.append("`†` = shipped with a local patch from `overlay/patches/` "
               "(usually a rewritten trigger description).\n")
    out.append("**Plugin** is which install ships the skill. `bigslick` is the lean default; "
               "the rest are opt-in bundles you add with "
               "`claude plugin install bigslick-<bundle>@bigslick`.\n")
    # Read the published plugin roots rather than the manifest, so this column reflects
    # what a user can actually install.
    where = {}
    import json as _json
    mkp = ROOT/".claude-plugin"/"marketplace.json"
    if mkp.exists():
        for pl in _json.loads(mkp.read_text()).get("plugins", []):
            sd = ROOT/pl["source"]/"skills"
            if sd.is_dir():
                for d in sd.iterdir():
                    if d.is_dir(): where[d.name] = pl["name"]
    out.append("| Skill | Plugin | Source | Licence | External dependencies |")
    out.append("|---|---|---|---|---|")
    for name, repo, lic, cell, patched in rows:
        out.append(f"| `{name}`{' †' if patched else ''} | `{where.get(name,'—')}` | {repo} | {lic} | {cell} |")
    out.append("")

    (ROOT / "INVENTORY.md").write_text("\n".join(out))
    print(f"Wrote INVENTORY.md — {len(rows)} skills, {dep_count} with external dependencies")
    for k, v in sorted(tally.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
