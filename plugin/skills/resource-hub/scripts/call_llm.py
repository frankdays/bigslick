#!/usr/bin/env python3
"""Provider-agnostic LLM caller for the resource-hub skill.

Usage:
  python call_llm.py --capability deep_reasoning --prompt "Draft a positioning statement for..."
  python call_llm.py --capability bulk_classification --prompt-file items.txt --system "Classify each line..."

Reads config/registry.yaml, resolves the capability to a provider+model,
pulls the API key from the environment, and walks the fallback chain on failure.
Calling skills stay provider-agnostic: they only name a capability.
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

try:
    import yaml  # pip install pyyaml
except ImportError:
    sys.exit("Missing dependency: run `pip install pyyaml` first.")

REGISTRY = Path(__file__).resolve().parent.parent / "config" / "registry.yaml"


def load_registry():
    with open(REGISTRY) as f:
        return yaml.safe_load(f)


def resolve(reg, capability):
    """Yield (provider_name, provider_cfg, model_id) for primary then fallbacks."""
    cap = reg["capabilities"].get(capability)
    if not cap:
        sys.exit(f"Unknown capability '{capability}'. See config/registry.yaml.")
    chain = [(cap["provider"], cap.get("model"))]
    for fb in cap.get("fallbacks", []):
        if fb.startswith("builtin."):
            continue  # built-in tools are handled by the agent, not this script
        name, _, model_key = fb.partition(".")
        chain.append((name, model_key or None))
    for name, model_key in chain:
        p = reg["providers"].get(name)
        if not p:
            continue
        model = None
        if model_key and "models" in p:
            model = p["models"].get(model_key, model_key)
        elif "models" in p and cap.get("model"):
            model = p["models"].get(cap["model"], cap["model"])
        yield name, p, model


def call_anthropic(p, model, system, prompt, timeout):
    req = urllib.request.Request(
        p["api_base"],
        data=json.dumps({
            "model": model,
            "max_tokens": 4096,
            **({"system": system} if system else {}),
            "messages": [{"role": "user", "content": prompt}],
        }).encode(),
        headers={
            "content-type": "application/json",
            "x-api-key": os.environ[p["api_key_env"]],
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    return "".join(b.get("text", "") for b in data.get("content", []))


def call_openai_style(p, model, system, prompt, timeout):
    """Works for OpenAI, Perplexity, and other chat-completions-compatible APIs."""
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    req = urllib.request.Request(
        p["api_base"],
        data=json.dumps({"model": model, "messages": messages}).encode(),
        headers={
            "content-type": "application/json",
            "authorization": f"Bearer {os.environ[p['api_key_env']]}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    return data["choices"][0]["message"]["content"]


CALLERS = {
    "anthropic": call_anthropic,
    # everything else defaults to the OpenAI-compatible shape
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capability", required=True)
    ap.add_argument("--prompt")
    ap.add_argument("--prompt-file")
    ap.add_argument("--system", default=None)
    args = ap.parse_args()

    prompt = args.prompt or (Path(args.prompt_file).read_text() if args.prompt_file else None)
    if not prompt:
        sys.exit("Provide --prompt or --prompt-file.")

    reg = load_registry()
    timeout = reg.get("defaults", {}).get("timeout_seconds", 120)
    errors = []
    for name, p, model in resolve(reg, args.capability):
        key_env = p.get("api_key_env")
        if key_env and key_env not in os.environ:
            errors.append(f"{name}: env var {key_env} not set")
            continue
        if p.get("connection") == "mcp":
            errors.append(f"{name}: MCP provider — call via the connected MCP tools, not this script")
            continue
        caller = CALLERS.get(name, call_openai_style)
        try:
            print(caller(p, model, args.system, prompt, timeout))
            return
        except Exception as e:  # noqa: BLE001 — report and try next fallback
            errors.append(f"{name}: {e}")
    sys.exit("All providers failed for capability "
             f"'{args.capability}':\n  " + "\n  ".join(errors))


if __name__ == "__main__":
    main()
