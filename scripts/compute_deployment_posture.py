"""Classify deployment_posture for every registry entry.

Strategy (no network calls — uses existing YAML + sidecar signals only):

1. Strong-signal rules from the description + sovereignty_notes:
   - "no network", "fully offline", "air-gap" -> local-only
   - "Ollama", "llama.cpp", "GGUF", "self-contained binary" + no cloud refs -> local-first
   - "Docker", "Helm", "Kubernetes" + "self-host" + cloud-compat -> hybrid
   - "Hosted service", "SaaS", "API key required", "signup at" -> api-only
   - Education entries (notebooks / docs / courses) -> local-only

2. MAS-based fallback (per `docs/sovereignty-rubric.md`):
   - MAS 0  -> api-only
   - MAS 1-2 -> cloud-first (provider-locked but self-host possible)
   - MAS 3   -> hybrid
   - MAS 4   -> local-first
   - MAS 5   -> local-first

3. Confidence: rules above produce confidence 0.85-0.95; MAS-only
   fallback is 0.55. Anything below 0.7 is flagged for ensemble.

Writes:
  - registry/_metadata/_deployment.json (id -> {posture, confidence, signals})
  - reports a histogram of postures and a list of low-confidence ids
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

try:
    from scripts._atomic import atomic_write_text
except ModuleNotFoundError:
    from _atomic import atomic_write_text  # type: ignore[no-redef]

REGISTRY = Path(r"C:\Users\benke\open-harness-atlas\registry")
META = REGISTRY / "_metadata"

POSTURES = ("local-only", "local-first", "hybrid", "cloud-first", "api-only")

# Pre-compiled regexes for signal extraction
RX_LOCAL_ONLY = re.compile(
    r"\b(offline|air[- ]?gap|no network|disconnected|fully (?:local|offline)|"
    r"runs (?:entirely )?(?:offline|locally|on[- ]device)|on[- ]device only)\b",
    re.IGNORECASE,
)
RX_LOCAL_FIRST = re.compile(
    r"\b(ollama|llama\.cpp|llamacpp|gguf|local model|local weights|vllm|"
    r"localhost|self[- ]host(?:ed|ing)?|run locally|hugging ?face transformers|"
    r"local inference|on[- ]premise)\b",
    re.IGNORECASE,
)
RX_HYBRID = re.compile(
    r"\b(local (?:classifier|model|cache) (?:with|and|plus) (?:cloud|hosted|api)|"
    r"(?:cloud|hosted) (?:judge|generator|tier) (?:with|and) local|"
    r"mixed (?:local and cloud|cloud and local) (?:components|tiers|model)|"
    r"hybrid (?:deployment|setup|stack|inference))\b",
    re.IGNORECASE,
)
RX_CONTAINERIZED = re.compile(
    r"\b(docker|helm|kubernetes|k8s|compose\.ya?ml|"
    r"deploy (?:to|in) (?:aws|gcp|azure)|terraform|pulumi)\b",
    re.IGNORECASE,
)
RX_CLOUD_FIRST = re.compile(
    r"\b(saas|cloud[- ]native|managed (?:service|platform)|hosted (?:platform|version)|"
    r"hosted instance|fully managed|managed cloud|"
    r"production cloud|hosted with us|signup at|sign up at|free tier)\b",
    re.IGNORECASE,
)
RX_API_ONLY = re.compile(
    r"\b(api key required|requires (?:an? )?api key|requires (?:an? )?(?:openai|anthropic|gemini) api|"
    r"closed[- ]source backend|hosted only|no self[- ]host|cloud only|"
    r"requires signup|requires (?:a |an )?account|paid plan)\b",
    re.IGNORECASE,
)
RX_PROVIDER_LOCKED = re.compile(
    r"\b(claude code|gpt[- ]?4|chatgpt|anthropic only|openai only|"
    r"only works with claude|only supports openai|gemini cli|"
    r"provider[- ]locked)\b",
    re.IGNORECASE,
)
RX_GATEWAY_MULTI = re.compile(
    r"\b(\d+\+? providers?|provider[- ]agnostic|multi[- ]provider|"
    r"openai[- ]compatible|drop[- ]in replacement|provider gateway|"
    r"litellm|portkey|openrouter)\b",
    re.IGNORECASE,
)


def classify(entry: dict) -> tuple[str, float, list[str]]:
    """Return (posture, confidence, signals)."""
    cat = entry.get("category", "")
    mas = entry.get("model_agnostic_score", 3)
    desc = (entry.get("description") or "")
    sn = (entry.get("sovereignty_notes") or "")
    tagline = (entry.get("tagline") or "")
    blob = f"{desc}\n\n{sn}\n\n{tagline}"

    signals: list[str] = []

    # Education entries: notebooks/docs/courses are universally local-only
    if cat == "education":
        signals.append("category=education")
        return "local-only", 0.95, signals

    # Strong patterns first (most specific wins)
    if RX_LOCAL_ONLY.search(blob):
        signals.append("re=local-only")
        return "local-only", 0.9, signals

    if RX_PROVIDER_LOCKED.search(blob) and mas <= 1:
        signals.append("re=provider-locked+mas<=1")
        return "api-only", 0.9, signals

    if RX_API_ONLY.search(blob) and mas <= 2:
        signals.append("re=api-only-text+mas<=2")
        return "api-only", 0.88, signals

    # Routing/gateway: multi-provider; lean local-first if self-hostable
    if cat == "routing" and RX_GATEWAY_MULTI.search(blob):
        signals.append("re=routing-gateway-multi")
        if RX_CONTAINERIZED.search(blob) or RX_LOCAL_FIRST.search(blob) or mas >= 4:
            signals.append("re=self-hostable-or-local")
            return "local-first", 0.85, signals
        return "cloud-first", 0.78, signals

    if RX_LOCAL_FIRST.search(blob):
        signals.append("re=local-first")
        return "local-first", 0.88, signals

    if RX_HYBRID.search(blob):
        signals.append("re=hybrid-explicit")
        return "hybrid", 0.85, signals

    # Containerized (Docker/Helm/K8s) without explicit local-first OR hybrid signal
    # = self-hostable cloud-deployable -> local-first (since they're self-host-capable)
    if RX_CONTAINERIZED.search(blob):
        signals.append("re=containerized-only")
        if RX_CLOUD_FIRST.search(blob):
            signals.append("re=cloud-first-emphasis")
            return "cloud-first", 0.78, signals
        if mas >= 3:
            return "local-first", 0.75, signals
        return "cloud-first", 0.7, signals

    if RX_CLOUD_FIRST.search(blob):
        signals.append("re=cloud-first")
        return "cloud-first", 0.8, signals

    # MAS-only fallback (lower confidence)
    signals.append(f"mas-fallback={mas}")
    if mas == 0:
        return "api-only", 0.6, signals
    if mas <= 2:
        return "cloud-first", 0.55, signals
    if mas == 3:
        return "hybrid", 0.55, signals
    if mas == 4:
        return "local-first", 0.6, signals
    return "local-first", 0.6, signals  # mas 5


def main() -> int:
    results: dict[str, dict] = {}
    posture_counts: Counter = Counter()
    low_conf: list[str] = []

    for cat_dir in REGISTRY.iterdir():
        if not cat_dir.is_dir() or cat_dir.name.startswith("_"):
            continue
        for yml in cat_dir.glob("*.yaml"):
            if yml.name.startswith("_"):
                continue
            entry = yaml.safe_load(yml.read_text(encoding="utf-8"))
            if not entry:
                continue
            posture, conf, signals = classify(entry)
            results[entry["id"]] = {
                "posture": posture,
                "confidence": round(conf, 3),
                "signals": signals,
                "category": entry.get("category"),
                "mas": entry.get("model_agnostic_score"),
            }
            posture_counts[posture] += 1
            if conf < 0.7:
                low_conf.append(entry["id"])

    META.mkdir(parents=True, exist_ok=True)
    out = META / "_deployment.json"
    atomic_write_text(out, json.dumps(results, indent=2, ensure_ascii=False))

    print(f"Classified {len(results)} entries -> {out}")
    print("\nPosture distribution:")
    for p in POSTURES:
        n = posture_counts[p]
        pct = (n / len(results)) * 100 if results else 0
        print(f"  {p:<14} {n:>4}  ({pct:5.1f}%)")
    print(f"\nLow-confidence (<0.7): {len(low_conf)}")
    print(f"  ({(len(low_conf)/len(results)*100):.1f}% of total — candidates for ensemble pass)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
