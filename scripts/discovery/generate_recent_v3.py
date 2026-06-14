r"""Generate the 10 high-signal YAMLs from the awesome-list discovery sweep.

These were found via the GraphQL-batched awesome-list parser (~3 min
vs ~5h for the legacy REST path). All 10 had >= 2-list endorsement
from the curated `AWESOME_LISTS` set and were missing from the
existing registry — major coverage gaps.

Run once::

    python -m scripts.discovery.generate_recent_v3
"""
# Long-tagline literals are intentional; this file is one-shot scaffolding.
# ruff: noqa: E501
from __future__ import annotations

import json
from pathlib import Path

CANDIDATES_PATH = (
    Path(__file__).parent / "candidates.awesome.jsonl"
)
REGISTRY_DIR = Path(__file__).parent.parent.parent / "registry"

PROVENANCE = (
    "Added 2026-06-14 via the awesome-list discovery sweep "
    "(GraphQL-batched parser; >= 2-list endorsement)."
)

# Hand-curated per-entry metadata. category may differ from the
# candidate-record's primary_category because awesome-list categorisation
# is hint-based; we re-categorise here using domain knowledge.
PICKS: dict[str, dict] = {
    # ----- agent -----
    "aider": {
        "category": "agent", "subcategory": "code-agent",
        "tagline": "AI pair programming in the terminal — Git-aware coding agent.",
        "para1": (
            "Aider is a terminal-based AI pair-programming agent. "
            "Operates directly on the user's git working tree: reads "
            "diffs, edits files, runs tests, commits changes with "
            "co-author trailers. Provider-agnostic via litellm."
        ),
        "para2": (
            "In the atlas: peer to `cline`, `open-swe`, `swe-agent`, "
            "`mini-swe-agent` on the code-agent shelf. Differentiator "
            "is the no-IDE-no-server posture — runs as a single CLI "
            "process and treats git as the persistent state."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Aider-AI",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["cline", "open-swe", "swe-agent", "mini-swe-agent", "openhands"],
        "sov_extra": (
            "Apache-2.0; CLI tool; no telemetry. Talks to whatever "
            "LLM provider the user configures via litellm — works "
            "with OpenAI, Anthropic, local Ollama / llama.cpp, "
            "Bedrock, Azure OpenAI, etc. Source code never leaves "
            "the host unless the operator chose a managed provider."
        ),
    },
    "e2b": {
        "category": "agent", "subcategory": "agent-sandbox",
        "tagline": "Open-source sandbox runtime for AI-agent code execution.",
        "para1": (
            "E2B is a sandbox runtime for AI agents that need to "
            "execute LLM-generated code safely. Provides Firecracker / "
            "Cloud Hypervisor microVMs with per-session isolation, "
            "filesystem snapshots, and language-runtime templates "
            "(Python, Node, custom)."
        ),
        "para2": (
            "In the atlas: the cloud / managed-microVM counterpart to "
            "`sandlock` (local process sandbox) and `daytona`. "
            "Critical primitive for the `audit-log-fsm-escalation` "
            "pattern's tool layer."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "E2B",
        "origin_country": "CZ", "mas": 5, "posture": "hybrid",
        "alignment": "aligned",
        "adjacent_to": ["sandlock", "agentdojo", "openhands", "swe-agent"],
        "sov_extra": (
            "Apache-2.0; can be run either as the managed E2B cloud "
            "(api.e2b.dev) OR self-hosted via the open-source runtime "
            "on the operator's own hardware. The self-host path keeps "
            "all code-execution traffic in-tenancy. Posture noted as "
            "`hybrid` to reflect both deployment modes."
        ),
    },
    "continue": {
        "category": "agent", "subcategory": "code-agent",
        "tagline": "Open-source code AI assistant for VS Code / JetBrains — bring-your-own model.",
        "para1": (
            "Continue is an open-source IDE extension (VS Code + "
            "JetBrains) that turns any LLM into a code assistant. "
            "Chat, autocomplete, edit-in-place, and agent-mode "
            "actions, all configurable to the user's choice of "
            "model."
        ),
        "para2": (
            "In the atlas: the OSS BYO-model alternative to GitHub "
            "Copilot / Cursor. Peer to `aider`, `cline`; "
            "differentiator is the deep IDE integration and the "
            "config-driven multi-provider setup."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Continue",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["aider", "cline", "open-swe", "openhands"],
        "sov_extra": (
            "Apache-2.0; runs locally as an IDE extension. Model "
            "provider is fully operator-controlled — supports OpenAI, "
            "Anthropic, Bedrock, Azure, Ollama, vLLM, LM Studio, "
            "llama.cpp, etc. The IDE extension itself does not phone "
            "home (telemetry is opt-in and documented)."
        ),
    },
    "devika": {
        "category": "agent", "subcategory": "autonomous-agent",
        "tagline": "Open-source agentic software engineer — plans, codes, executes whole engineering tasks.",
        "para1": (
            "Devika is an autonomous software-engineering agent that "
            "decomposes a high-level objective into a plan, writes "
            "code, browses for documentation, and iterates against "
            "test feedback. Web UI plus an LLM-agnostic back end."
        ),
        "para2": (
            "In the atlas: peer to `openhands`, `swe-agent`, "
            "`gpt-engineer`, `metagpt`. Differentiator is the "
            "interactive UI and explicit planning trace."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "stitionai",
        "origin_country": "null", "mas": 4, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["openhands", "swe-agent", "gpt-engineer", "metagpt", "cline"],
        "sov_extra": (
            "MIT licence; self-hosted (Python + a small web UI). "
            "Configurable across Claude, GPT-4, Ollama, Mistral, etc. "
            "Browser actions go through Playwright on the host; no "
            "managed-service dependency."
        ),
    },
    "privategpt": {
        "category": "agent", "subcategory": "private-rag-agent",
        "tagline": "Privacy-preserving RAG over local documents — no data leaves the host.",
        "para1": (
            "PrivateGPT is a fully local RAG stack: document loaders, "
            "embedding store (Qdrant), local LLM inference (Llama, "
            "Mistral, etc.), API + UI — all running on the operator's "
            "own hardware. 100% no-egress by default."
        ),
        "para2": (
            "In the atlas: the canonical reference for the "
            "`local-possible-spine` pattern. Peer to `localgpt`, "
            "`anythingllm`, `khoj` on the local-first-RAG shelf."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Zylon",
        "origin_country": "ES", "mas": 5, "posture": "local-only",
        "alignment": "aligned",
        "adjacent_to": ["anythingllm", "khoj"],
        "sov_extra": (
            "Apache-2.0; designed from day one for air-gapped / "
            "fully-local operation. Default config makes ZERO outbound "
            "calls — the embedding model, the vector store (Qdrant), "
            "and the LLM all run on the host. Optionally swappable "
            "to a managed provider, but that defeats the point."
        ),
    },
    # ----- redteam -----
    "superagent": {
        "category": "redteam", "subcategory": "agent-firewall",
        "tagline": "Open-source agent firewall — protects AI apps against prompt injection and data leaks.",
        "para1": (
            "Superagent is an agent-side firewall that intercepts "
            "LLM inputs and outputs to detect and block prompt "
            "injection, secret leakage, PII exfiltration, and "
            "policy-violating tool calls. Pluggable detectors + "
            "declarative policy."
        ),
        "para2": (
            "In the atlas: peer to `luckypipewrench-pipelock`, "
            "`agent-security-scanner-mcp`, `secureagentics-adrian`, "
            "`llm-guard` on the runtime-defence shelf. Companion to "
            "the `audit-log-fsm-escalation` and "
            "`multi-tenant-policy-isolation` patterns."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Superagent",
        "origin_country": "SE", "mas": 4, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": [
            "luckypipewrench-pipelock", "agent-security-scanner-mcp",
            "secureagentics-adrian", "llm-guard",
        ],
        "sov_extra": (
            "MIT licence; self-hostable middleware. Sits in-process "
            "with the agent, so the upstream LLM provider is "
            "unconstrained. Detection runs entirely locally; no "
            "data leaves the firewall for inspection."
        ),
    },
    # ----- governance -----
    "evidently": {
        "category": "governance", "subcategory": "llm-observability",
        "tagline": "Open-source ML + LLM observability framework — evaluate, test, monitor.",
        "para1": (
            "Evidently is an open-source observability framework for "
            "ML and LLM systems. 100+ pre-built metrics, drift "
            "detection, prompt-eval tests, dashboards, and a Python "
            "SDK that drops into existing pipelines."
        ),
        "para2": (
            "In the atlas: peer to `langfuse`, `arize-phoenix`, "
            "`openllmetry`, `langwatch` on the observability shelf. "
            "Differentiator is the dual ML + LLM coverage (useful "
            "in mixed-stack environments)."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Evidently AI",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["langfuse", "arize-phoenix", "openllmetry", "langwatch"],
        "sov_extra": (
            "Apache-2.0; self-hosted Python library + optional "
            "self-hosted UI service. No managed-service dependency. "
            "Observability data goes wherever the operator routes "
            "it. Vendor-neutral metrics; works with any LLM provider."
        ),
    },
    # ----- routing -----
    "gpustack": {
        "category": "routing", "subcategory": "gpu-cluster-manager",
        "tagline": "Open-source GPU cluster manager that orchestrates inference engines (vLLM, llama.cpp, MLX).",
        "para1": (
            "GPUStack is an open-source GPU cluster manager and "
            "model gateway. Discovers available accelerators across "
            "a heterogeneous fleet (NVIDIA, AMD, Apple Silicon), "
            "schedules model loads, and exposes a unified "
            "OpenAI-compatible endpoint."
        ),
        "para2": (
            "In the atlas: the missing cluster-orchestration layer "
            "below the gateway entries (`litellm`, `portkey-gateway`, "
            "`smg`). Peer to `kubernetes` add-ons like KServe, but "
            "lighter-weight and ML-native."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "GPUStack",
        "origin_country": "CN", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["vllm", "llama-cpp", "litellm", "portkey-gateway", "ollama"],
        "sov_extra": (
            "Apache-2.0; self-hosted control plane. Manages the "
            "operator's own GPUs (on-prem, cloud VMs, or a mixed "
            "fleet). The exposed API is OpenAI-compatible so any "
            "client can swap to a self-hosted endpoint without code "
            "changes."
        ),
    },
    "text-embeddings-inference": {
        "category": "routing", "subcategory": "embedding-server",
        "tagline": "Hugging Face's blazing-fast inference server for text-embedding models.",
        "para1": (
            "Text-Embeddings-Inference (TEI) is Hugging Face's "
            "specialised inference server for embedding and "
            "reranking models. Rust core, dynamic batching, "
            "OpenAI-compatible embeddings endpoint, supports "
            "BGE / E5 / GTE / Jina families and many more."
        ),
        "para2": (
            "In the atlas: the embedding-side counterpart to `vllm` "
            "and `tgi` for the LLM side. Peer to `infinity` "
            "(another fast embedding server). Critical for any "
            "local-first RAG stack."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Hugging Face",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["vllm", "huggingface-tgi", "litellm"],
        "sov_extra": (
            "Apache-2.0; self-hosted Rust binary. No telemetry; "
            "no managed-service dependency. Embedding models run on "
            "operator hardware, so document contents and queries "
            "stay local. OpenAI-compatible API surface enables drop-in "
            "replacement of managed embedding providers."
        ),
    },
    # ----- eval -----
    "autorag": {
        "category": "eval", "subcategory": "rag-eval",
        "tagline": "Open-source AutoML-style framework for finding the best RAG pipeline.",
        "para1": (
            "AutoRAG is an automated RAG-pipeline optimisation "
            "framework. Treats RAG as a search problem: enumerate "
            "retriever / chunker / re-ranker / prompt-strategy "
            "combinations, evaluate against the user's QA set, "
            "report the best pipeline."
        ),
        "para2": (
            "In the atlas: peer to `ragas`, `open-rag-eval`, "
            "`tonic-validate`, `trulens`. Differentiator is the "
            "search-and-optimise framing — produces a recommended "
            "pipeline, not just metrics."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Marker Inc",
        "origin_country": "KR", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["ragas", "open-rag-eval", "tonic-validate", "trulens"],
        "sov_extra": (
            "Apache-2.0; Python library; runs locally against the "
            "operator's documents + QA set. Judge LLM is "
            "operator-supplied (any OpenAI-compatible endpoint, "
            "including local Llama / Mistral)."
        ),
    },
}


def render(eid: str, rec: dict, cand: dict) -> str:
    license_key = cand.get("license_key") or "MIT"
    license_display = {
        "mit": "MIT", "apache-2.0": "Apache-2.0",
        "bsd-3-clause": "BSD-3-Clause", "bsd-2-clause": "BSD-2-Clause",
        "mpl-2.0": "MPL-2.0", "gpl-3.0": "GPL-3.0",
        "agpl-3.0": "AGPL-3.0", "lgpl-3.0": "LGPL-3.0",
    }.get(license_key, license_key.upper())
    language = cand.get("language") or "null"
    repo_url = cand.get("url") or f"https://github.com/{cand['full_name']}"
    homepage = cand.get("homepage")

    country_value = rec["origin_country"]
    country_line = (
        f"origin_country: {country_value}"
        if country_value not in ("null", None)
        else "origin_country: null"
    )

    sov_full = f"{PROVENANCE}\n  {rec['sov_extra']}"
    homepage_line = f'homepage: {homepage}\n' if homepage else ''
    adjacent_lines = "\n".join(f"  - {a}" for a in rec["adjacent_to"])
    tagline_quoted = '"' + rec["tagline"].replace('"', '\\"') + '"'
    name_quoted = '"' + eid.replace('-', ' ').title().replace('"', '\\"') + '"'

    return f"""id: {eid}
name: {name_quoted}

category: {rec['category']}
subcategory: {rec['subcategory']}

repo_url: {repo_url}
{homepage_line}license: {license_display}
primary_language: {language}

tagline: {tagline_quoted}

description: |
  {rec['para1']}

  {rec['para2']}

maturity: {rec['maturity']}

maintainer:
  type: {rec['maintainer_type']}
  name: {rec['maintainer_name']}

{country_line}

model_agnostic_score: {rec['mas']}

sovereignty_notes: |
  {sov_full}

harness_paradigm_alignment: {rec['alignment']}

deployment_posture: {rec['posture']}

adjacent_to:
{adjacent_lines}
"""


def main() -> int:
    cand_index: dict[str, dict] = {}
    for line in CANDIDATES_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        cand_index[rec["candidate_id"]] = rec

    written = 0
    for eid, rec in PICKS.items():
        if eid not in cand_index:
            print(f"  [skip] {eid}: not in candidates file")
            continue
        cand = cand_index[eid]
        out_dir = REGISTRY_DIR / rec["category"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{eid}.yaml"
        if out_path.exists():
            print(f"  [skip] {eid}: already exists at {out_path}")
            continue
        out_path.write_text(render(eid, rec, cand), encoding="utf-8")
        print(f"  [wrote] {out_path.relative_to(REGISTRY_DIR.parent)}")
        written += 1
    print(f"\nwrote {written} new YAMLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
