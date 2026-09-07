#!/usr/bin/env python3
"""What should this company wire up to get more out of Big Slick?

    python3 scripts/suggest_addons.py                     # everything installed
    python3 scripts/suggest_addons.py --plugin bigslick   # just the lean core
    python3 scripts/suggest_addons.py --pack ~/Documents/bigslick/acme

Onboarding ends with a context pack and a set of priority skills, and a fair number
of those skills reach an external service. Nothing told the user which ones, so the
first time a skill needed a key they found out by watching it fail.

This reads what each skill actually references and ranks the services by how much
they unlock, so the answer is "these four keys turn on 31 skills" rather than a
wall of every credential in the library. With --pack it also flags what the
company already owns, read from their stack.md — those come first, because a tool
they are already paying for needs a key, not a purchase decision.

Reuses gen_inventory's scanner so the two never disagree.
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from gen_inventory import scan  # noqa: E402  (same scanner the inventory uses)

# An env var is a credential; what a human needs to know is the service behind it.
SERVICE = {
    "SEMRUSH": ("Semrush", "SEO and competitive data", "paid"),
    "AHREFS": ("Ahrefs", "backlinks and keyword data", "paid"),
    "DATAFORSEO": ("DataForSEO", "SERP and keyword data, pay-as-you-go", "paid"),
    "SERPAPI": ("SerpAPI", "live search results", "paid"),
    "APIFY": ("Apify", "web scraping actors", "freemium"),
    "APOLLO": ("Apollo.io", "B2B contact and company enrichment", "freemium"),
    "GOOGLE": ("Google Cloud OAuth", "Search Console, Analytics, Ads, YouTube", "free"),
    "GSC": ("Google Search Console", "your own search performance", "free"),
    "POSTHOG": ("PostHog", "product analytics", "freemium"),
    "HUBSPOT": ("HubSpot", "CRM records and campaigns", "freemium"),
    "BRANDDEV": ("Brand.dev", "brand lookup and monitoring", "freemium"),
    "UNSPLASH": ("Unsplash", "stock imagery", "free"),
    "OPENAI": ("OpenAI", "image generation in a few skills", "paid"),
    "STABILITY": ("Stability AI", "image generation", "paid"),
    "ELEVENLABS": ("ElevenLabs", "voice for video skills", "paid"),
    "GEMINI": ("Google Gemini", "used by some vendored skills", "freemium"),
    "RESEND": ("Resend", "transactional email sending", "freemium"),
    "SLACK": ("Slack", "posting into channels", "free"),
    "DISCORD": ("Discord", "posting into channels", "free"),
    "TELEGRAM": ("Telegram", "posting into channels", "free"),
    "YOUTUBE": ("YouTube Data API", "channel and video analytics", "free"),
    "ENCEPTION": ("Enception", "GEO/AI-search analysis", "paid"),
    "GOOSEWORKS": ("Gooseworks", "the goose-skills upstream's own service", "paid"),
    "GOOSE": ("Gooseworks", "the goose-skills upstream's own service", "paid"),
    "FIRECRAWL": ("Firecrawl", "page crawling for AI-search skills", "freemium"),
    "SAVVYCAL": ("SavvyCal", "booking-link attribution", "paid"),
}
PLACEHOLDER = re.compile(r"^(YOUR|MY|EXAMPLE|TEST|SAMPLE)_")

# What to look for in stack.md to call a service "already owned". Several names share
# a first word, so matching on that alone mislabels them.
MATCH = {
    "Google Cloud OAuth": ("google analytics", "search console", "google ads", "ga4", "youtube"),
    "Google Gemini": ("gemini",),
    "Google Search Console": ("search console", "gsc"),
    "OpenAI": ("openai", "chatgpt"),
    "Stability AI": ("stability",),
    "Apollo.io": ("apollo",),
    "Brand.dev": ("brand.dev",),
    "YouTube Data API": ("youtube",),
    "Gooseworks": ("gooseworks",),
}

def service_of(env_var: str):
    for prefix, meta in SERVICE.items():
        if env_var.startswith(prefix):
            return meta
    return (env_var.split("_")[0].title(), "", "unknown")

def skill_dirs():
    """[(skill_dir, plugin_name)] from the published plugin roots.

    Reads skills/ and bundles/*/skills/ rather than dist/, because dist/ is a build
    artifact that only exists in a source checkout — the end-user download ships the
    plugin roots instead, and this script now ships with it.
    """
    mk = ROOT / ".claude-plugin" / "marketplace.json"
    found = []
    if mk.exists():
        for pl in json.loads(mk.read_text()).get("plugins", []):
            sd = ROOT / pl["source"] / "skills"
            if sd.is_dir():
                found += [(d, pl["name"]) for d in sorted(sd.iterdir()) if d.is_dir()]
    if not found:                       # source checkout with no marketplace yet
        dist = ROOT / "dist" / "skills"
        if dist.is_dir():
            found = [(d, None) for d in sorted(dist.iterdir()) if d.is_dir()]
    return found

def owned_tools(pack: Path):
    """The company's stack.md, lowercased. Kept as raw text rather than a word set so
    multi-word names like "google analytics" can still match."""
    f = pack / "stack.md"
    return f.read_text().lower() if f.is_file() else ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plugin", help="only skills shipped by this plugin, e.g. bigslick")
    ap.add_argument("--pack", help="client pack, to flag tools they already own")
    a = ap.parse_args()

    skills = skill_dirs()
    if not skills:
        sys.exit("No skills found. In a source checkout, run scripts/compose.py first.")

    owned = owned_tools(Path(a.pack).expanduser()) if a.pack else ""

    services, mcps, considered = {}, {}, 0
    for d, owner in skills:
        if a.plugin and owner != a.plugin:
            continue
        considered += 1
        env, mcp, _pkg, _host = scan(d)
        for e in env:
            if PLACEHOLDER.match(e):
                continue
            name, what, cost = service_of(e)
            s = services.setdefault(name, {"what": what, "cost": cost, "vars": set(), "skills": set()})
            s["vars"].add(e); s["skills"].add((d.name, owner))
        for m in mcp:
            mcps.setdefault(m, set()).add(d.name)

    scope = f"plugin '{a.plugin}'" if a.plugin else "all installed skills"
    print(f"Add-ons worth wiring up — {considered} skills scanned ({scope})\n")

    ranked = sorted(services.items(), key=lambda kv: (-len(kv[1]["skills"]), kv[0]))
    def is_owned(name):
        toks = MATCH.get(name) or (name.split()[0].lower(),)
        return any(tok in owned for tok in toks)

    if owned:
        ranked.sort(key=lambda kv: (not is_owned(kv[0]), -len(kv[1]["skills"])))
        print("Tools your stack.md says you already use are listed first — those need a key,\n"
              "not a purchase decision.\n")

    for name, s in ranked:
        n = len(s["skills"])
        have = " [you already use this]" if owned and is_owned(name) else ""
        cost = f" · {s['cost']}" if s["cost"] != "unknown" else ""
        print(f"{name}{cost}{have}")
        if s["what"]:
            print(f"  {s['what']}")
        print(f"  unlocks {n} skill{'s' if n != 1 else ''}: "
              + ", ".join(sorted(sk for sk, _ in list(s['skills'])[:6]))
              + (" ..." if n > 6 else ""))
        bundles = sorted({o for _, o in s["skills"] if o and o != "bigslick"})
        if bundles:
            print(f"  needs bundle: {', '.join(bundles)}")
        print(f"  set: {', '.join(sorted(s['vars'])[:4])}")
        print()

    if mcps:
        print("MCP connectors referenced by skills:")
        for m, sk in sorted(mcps.items(), key=lambda kv: -len(kv[1])):
            print(f"  {m} — {len(sk)} skill{'s' if len(sk) != 1 else ''}: {', '.join(sorted(sk)[:4])}")
        print()

    print("Nothing here is required. Every skill still works from what you tell it;\n"
          "these just let it fetch the numbers itself instead of asking you for them.")

if __name__ == "__main__":
    main()
