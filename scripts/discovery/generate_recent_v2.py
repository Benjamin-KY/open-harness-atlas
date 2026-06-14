r"""Generate the 22 high-signal YAMLs from the second recency sweep
(non-agent categories: routing, redteam, eval).

Run once::

    python -m scripts.discovery.generate_recent_v2

This script is one-shot scaffolding — each entry below is hand-curated
metadata. The candidate JSONL was produced by
``scripts/discovery/search_recent.py --only-categories eval,redteam,routing``.
"""
# Long-tagline literals are intentional; this file is one-shot scaffolding.
# ruff: noqa: E501
from __future__ import annotations

import json
from pathlib import Path

CANDIDATES_PATH = (
    Path(__file__).parent / "candidates.recent.non-agent.jsonl"
)
REGISTRY_DIR = Path(__file__).parent.parent.parent / "registry"

PROVENANCE = (
    "Added 2026-06-14 via the second recency-biased discovery sweep "
    "(non-agent categories: routing / redteam / eval)."
)

# Per-entry hand-curated metadata. Each value is (subcategory, tagline,
# description_para1, description_para2, maturity, maintainer_type,
# maintainer_name, origin_country, model_agnostic_score, posture,
# paradigm_alignment, adjacent_to, license_override).
#
# All entries get the standard PROVENANCE line prepended to sovereignty_notes
# plus a provider-portability statement.
PICKS: dict[str, dict] = {
    # ----- routing -----
    "jundot-omlx": {
        "category": "routing", "subcategory": "local-inference-server",
        "tagline": "MLX-based LLM inference server with continuous batching and SSD caching for Apple Silicon.",
        "para1": (
            "OMLX is an inference server tuned for Apple Silicon (M1-M4): "
            "continuous batching, paged attention, SSD-backed KV cache, "
            "OpenAI-compatible HTTP API. Brings vLLM-style throughput to "
            "Mac hardware without requiring an NVIDIA GPU."
        ),
        "para2": (
            "In the atlas: a local-only alternative to `vllm` / `tgi` / "
            "`llama-cpp-server` for Apple Silicon workstations and edge "
            "deployments. Pairs naturally with `litellm`, `openrouter`, "
            "`portkey` as the upstream provider in a routing pattern."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "jundot",
        "origin_country": "null", "mas": 5, "posture": "local-only",
        "alignment": "full",
        "adjacent_to": ["vllm", "llama-cpp", "litellm", "mlx-omni-server", "swiftlm"],
        "sov_extra": (
            "Apple Silicon only (MLX framework). Apache-2.0 with no "
            "telemetry. Serves an OpenAI-compatible API so anything that "
            "speaks OpenAI can swap to a Mac-hosted endpoint with one "
            "config change. No outbound network calls from the server "
            "itself; all inference is local. Provider-agnostic in the "
            "downstream sense: the server IS the provider."
        ),
    },
    "mlx-omni-server": {
        "category": "routing", "subcategory": "local-inference-server",
        "tagline": "Apple-MLX local inference server exposing an OpenAI-compatible API across modalities.",
        "para1": (
            "MLX Omni Server is a local inference server built on Apple's "
            "MLX framework. Supports text, image, and audio models, with "
            "OpenAI-compatible REST endpoints (chat, embeddings, images, "
            "audio)."
        ),
        "para2": (
            "In the atlas: complements `omlx` (raw-throughput LLM server) "
            "and `swiftlm` (Swift-native) as another local-only MLX option. "
            "Useful when a project wants the same OpenAI-shape endpoint on "
            "an Apple machine for development that production hits in the "
            "cloud."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "madroidmaq",
        "origin_country": "CN", "mas": 5, "posture": "local-only",
        "alignment": "full",
        "adjacent_to": ["jundot-omlx", "swiftlm", "ollama", "litellm"],
        "sov_extra": (
            "Apple Silicon only. MIT licence; self-hosted; no telemetry. "
            "Inference stays on-device; the server only speaks to its own "
            "MLX runtime. Provider-portable because client code targets "
            "the standard OpenAI shape."
        ),
    },
    "swiftlm": {
        "category": "routing", "subcategory": "local-inference-server",
        "tagline": "Native MLX-Swift LLM inference server for Apple Silicon — OpenAI + Anthropic API compatible.",
        "para1": (
            "SwiftLM is a Swift-native (no Python) LLM inference server for "
            "Apple Silicon, built on MLX-Swift. Exposes both OpenAI and "
            "Anthropic-shape HTTP APIs and supports SSD streaming for large "
            "models that exceed RAM."
        ),
        "para2": (
            "In the atlas: the dual-API surface makes it interesting in "
            "routing patterns where downstream clients are split between "
            "the OpenAI and Anthropic SDKs — both can hit one local server."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "SharpAI",
        "origin_country": "null", "mas": 5, "posture": "local-only",
        "alignment": "full",
        "adjacent_to": ["jundot-omlx", "mlx-omni-server", "ollama", "litellm"],
        "sov_extra": (
            "Swift / MLX — Apple Silicon only. No Python runtime to "
            "manage. MIT licence. Both OpenAI and Anthropic API surfaces "
            "make this a useful drop-in target when migrating off a "
            "managed provider."
        ),
    },
    "inferrs": {
        "category": "routing", "subcategory": "inference-server",
        "tagline": "TurboQuant inference server.",
        "para1": (
            "Inferrs is an inference server using TurboQuant quantisation "
            "for fast on-device or single-GPU serving. Focuses on "
            "small-footprint deployment of quantised models with "
            "OpenAI-compatible endpoints."
        ),
        "para2": (
            "In the atlas: a lighter-weight alternative to `vllm` / `tgi` "
            "when serving a small number of quantised models on modest "
            "hardware."
        ),
        "maturity": "alpha",
        "maintainer_type": "individual", "maintainer_name": "ericcurtin",
        "origin_country": "null", "mas": 4, "posture": "local-first",
        "alignment": "partial",
        "adjacent_to": ["vllm", "llama-cpp", "ollama"],
        "sov_extra": (
            "Apache-2.0; self-hosted. Quantisation-first design keeps the "
            "deployment local on consumer/single-GPU hardware. No "
            "managed-provider dependency."
        ),
    },
    "smg": {
        "category": "routing", "subcategory": "llm-gateway",
        "tagline": "Engine-agnostic LLM gateway in Rust with multi-provider routing.",
        "para1": (
            "SMG is a Rust-implemented LLM gateway with full OpenAI and "
            "Anthropic API compatibility on its public surface, while "
            "supporting vLLM, TensorRT-LLM, and llama.cpp on the back end. "
            "Designed for low-overhead routing in production."
        ),
        "para2": (
            "In the atlas: peer to `litellm`, `portkey`, `traceloop-hub` "
            "in the gateway role. The Rust implementation matters where "
            "Python overhead is unacceptable (high-RPS edge gateways)."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "lightseekorg",
        "origin_country": "null", "mas": 5, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["litellm", "portkey-gateway", "traceloop-hub", "vllm"],
        "sov_extra": (
            "Apache-2.0; self-hosted. Rust binary — no Python runtime; "
            "easier to ship into hardened environments. Routes to whatever "
            "back-end the operator chooses; gateway itself has no "
            "vendor lock-in."
        ),
    },
    "atopos31-llmio": {
        "category": "routing", "subcategory": "llm-gateway",
        "tagline": "Unified LLM gateway with weighted load balancing, observability, and cost tracking.",
        "para1": (
            "LLMIO is a Go-based LLM gateway focused on weighted load "
            "balancing across providers, per-key cost tracking, and "
            "OpenTelemetry-based observability. Single binary deployment."
        ),
        "para2": (
            "In the atlas: peer to `litellm`, `portkey` in the gateway "
            "role; differentiator is the weighted-routing primitives and "
            "the single-binary Go deployment story."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "atopos31",
        "origin_country": "CN", "mas": 5, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["litellm", "portkey-gateway", "smg", "traceloop-hub"],
        "sov_extra": (
            "MIT licence; single Go binary; self-hosted. Gateway itself "
            "does not phone home; emitter is OpenTelemetry which the "
            "operator points at their own collector."
        ),
    },
    "traceloop-hub": {
        "category": "routing", "subcategory": "llm-gateway",
        "tagline": "High-scale LLM gateway in Rust with built-in OpenTelemetry observability.",
        "para1": (
            "Traceloop Hub is a Rust LLM gateway built by the Traceloop "
            "team (also behind OpenLLMetry). Multi-provider routing, "
            "first-class OTel instrumentation, designed for high-RPS "
            "production traffic."
        ),
        "para2": (
            "In the atlas: complements `openllmetry` (the SDK) with the "
            "gateway-side counterpart. Peer to `litellm`, `portkey`, "
            "`smg` in the gateway role; differentiator is the deep OTel "
            "integration and the Rust performance profile."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "Traceloop",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["openllmetry", "litellm", "portkey-gateway", "smg", "atopos31-llmio"],
        "sov_extra": (
            "Apache-2.0; self-hosted. The companion `openllmetry` SDK is "
            "vendor-neutral OTel — observability data goes wherever the "
            "operator routes it (Honeycomb, Tempo, Jaeger, Grafana, your "
            "in-tenancy collector). Gateway routes to any OpenAI-shape "
            "provider."
        ),
    },
    "inference-benchmarker": {
        "category": "routing", "subcategory": "inference-benchmark",
        "tagline": "Hugging Face inference server benchmarking tool — measure throughput across vLLM / TGI / providers.",
        "para1": (
            "Hugging Face's inference-benchmarker measures throughput, "
            "latency percentiles, and time-to-first-token across "
            "OpenAI-compatible inference servers. Built to compare "
            "vLLM, TGI, sglang, hosted providers under identical load."
        ),
        "para2": (
            "In the atlas: the missing benchmarking peer to all the "
            "routing entries. Use to validate the model-agnostic claim "
            "of any stack — same prompts, different backends, head-to-head "
            "numbers."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Hugging Face",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["vllm", "huggingface-tgi", "sglang", "litellm"],
        "sov_extra": (
            "Apache-2.0. Benchmarking tool is fully local; the SUT (server "
            "under test) is whatever the operator chooses. Useful "
            "evidence-tool when a sovereignty migration needs to be "
            "justified ('here are the numbers showing vLLM on-prem matches "
            "the managed provider')."
        ),
    },
    # ----- redteam -----
    "anamorpher": {
        "category": "redteam", "subcategory": "multimodal-attack",
        "tagline": "Image-scaling attacks for multi-modal prompt injection (Trail of Bits research).",
        "para1": (
            "Anamorpher implements the image-scaling attack pattern: "
            "craft an image such that, when downsampled to the model's "
            "input resolution, it reveals a hidden adversarial prompt. "
            "Released as research-grade reproducible code by Trail of "
            "Bits."
        ),
        "para2": (
            "In the atlas: fills a real gap on the multimodal red-team "
            "side. Complements `pyrit`, `garak`, `llm-attacks` on the "
            "text side; closest neighbour is the multimodal section of "
            "`agentdojo` and the image-attack corner of `harmbench`."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Trail of Bits",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["pyrit", "garak", "harmbench", "agentdojo", "llm-attacks"],
        "sov_extra": (
            "MIT licence; runs locally; attack-corpus generation is "
            "fully offline. Target model can be any vision-language model "
            "the tester points the tool at (OpenAI, Anthropic, local "
            "Llama-vision, etc.). No telemetry."
        ),
    },
    "luckypipewrench-pipelock": {
        "category": "redteam", "subcategory": "mcp-firewall",
        "tagline": "Open-source AI-agent firewall for MCP security and agent egress.",
        "para1": (
            "Pipelock is a firewall/proxy that sits in front of MCP "
            "servers and AI-agent egress paths, scanning mediated HTTP, "
            "MCP, A2A, and arbitrary tool calls for prompt-injection "
            "payloads, secret leakage, and policy violations."
        ),
        "para2": (
            "In the atlas: peer to `agent-security-scanner-mcp`, "
            "`ai-infra-guard`, `securemcp` on the runtime-defence side. "
            "Closest match to the gateway-of-tools concept from the "
            "`audit-log-fsm-escalation` pattern."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "luckyPipewrench",
        "origin_country": "null", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["agent-security-scanner-mcp", "ai-infra-guard", "garak"],
        "sov_extra": (
            "Apache-2.0; runs as a local proxy. All inspection is "
            "in-process; the firewall does not call out to any managed "
            "service. Provider-agnostic on both sides: any MCP client / "
            "any MCP server / any LLM provider."
        ),
    },
    "api-relay-audit": {
        "category": "redteam", "subcategory": "relay-audit",
        "tagline": "Local security audit for AI API relays and LLM proxies — detects prompt injection, model substitution, telemetry leaks.",
        "para1": (
            "API-relay-audit inspects LLM proxies / API relays for "
            "common security issues: silent model substitution, "
            "prompt-injection passthrough, unexpected telemetry, "
            "weak auth, and CORS / TLS misconfigurations."
        ),
        "para2": (
            "In the atlas: novel niche. Complements `pipelock` (runtime "
            "defence) by auditing the relay or gateway itself — useful "
            "before adopting any of the routing-category entries in a "
            "sovereignty-sensitive environment."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "toby-bridges",
        "origin_country": "null", "mas": 4, "posture": "local-only",
        "alignment": "full",
        "adjacent_to": ["luckypipewrench-pipelock", "garak", "agent-security-scanner-mcp"],
        "sov_extra": (
            "MIT licence; CLI tool that runs entirely locally against "
            "an operator-supplied relay endpoint. Output is a JSON / "
            "HTML report; no data leaves the host. Especially valuable "
            "when validating that a third-party LLM gateway behaves as "
            "advertised."
        ),
    },
    "camel-prompt-injection": {
        "category": "redteam", "subcategory": "prompt-injection-defence",
        "tagline": "Reference code for 'Defeating Prompt Injections by Design' (Google Research).",
        "para1": (
            "Camel is the reference implementation for the Google "
            "Research paper 'Defeating Prompt Injections by Design'. "
            "Demonstrates an architectural defence where the agent "
            "executes in a typed action space that is provably immune "
            "to text-only prompt injection."
        ),
        "para2": (
            "In the atlas: the design-by-construction counterpart to "
            "the runtime defences in `pipelock` and "
            "`agent-security-scanner-mcp`. Important reference for the "
            "`audit-log-fsm-escalation` and "
            "`sovereignty-preserving-routing` patterns."
        ),
        "maturity": "alpha",
        "maintainer_type": "company", "maintainer_name": "Google Research",
        "origin_country": "US", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["pyrit", "garak", "luckypipewrench-pipelock", "agent-security-scanner-mcp"],
        "sov_extra": (
            "Apache-2.0; research-grade code that runs locally. "
            "Demonstration repo, not production middleware — read it for "
            "the architecture pattern rather than as a drop-in tool. "
            "Provider-agnostic at the model layer."
        ),
    },
    "cryptex-oss": {
        "category": "redteam", "subcategory": "red-team-toolkit",
        "tagline": "Open-source LLM red-teaming toolkit: 162 transforms, 36 mutators, 25 tool surfaces.",
        "para1": (
            "Cryptex-OSS is a red-teaming toolkit that bundles 162 "
            "input transforms, 36 mutators, and 25 tool-surface probes "
            "into a single CLI. Designed for offline corpus generation "
            "and reproducible adversarial campaigns."
        ),
        "para2": (
            "In the atlas: peer to `garak`, `pyrit`, `inspect_evals` "
            "with strong overlap on the transform/mutator dimension; "
            "differentiator is the breadth of tool-surface probes "
            "(useful for MCP-era agents)."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "m4xx101",
        "origin_country": "null", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["garak", "pyrit", "harmbench", "agentdojo"],
        "sov_extra": (
            "MIT licence; runs entirely locally; the 162 transforms "
            "and 36 mutators are deterministic functions, no external "
            "calls. Target LLM is whatever the operator points it at."
        ),
    },
    "secureagentics-adrian": {
        "category": "redteam", "subcategory": "runtime-agent-defence",
        "tagline": "Runtime security monitoring and control for AI agents — catches malicious tool use, prompt injection, exfiltration.",
        "para1": (
            "Adrian is a runtime guard that sits inside an agent loop and "
            "intercepts tool calls before they execute. Detects malicious "
            "tool use, suspected prompt-injection-derived actions, and "
            "data-exfiltration patterns; can block, log, or escalate."
        ),
        "para2": (
            "In the atlas: peer to `pipelock`, `agent-security-scanner-mcp`. "
            "Implements the runtime half of the "
            "`audit-log-fsm-escalation` pattern; pairs naturally with "
            "`langfuse` / `arize-phoenix` for the observability half."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "Secureagentics",
        "origin_country": "null", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["luckypipewrench-pipelock", "agent-security-scanner-mcp", "ai-infra-guard"],
        "sov_extra": (
            "Apache-2.0; self-hosted runtime; no managed-service "
            "dependency. Sits between the agent and its tools, so the "
            "LLM provider is unconstrained."
        ),
    },
    "praetorian-inc-augustus": {
        "category": "redteam", "subcategory": "llm-security-framework",
        "tagline": "LLM security testing framework from Praetorian — prompt injection, jailbreaks, adversarial attacks.",
        "para1": (
            "Augustus is Praetorian's LLM security testing framework, "
            "covering prompt injection, jailbreaks, and adversarial "
            "attacks. Built for security teams running pre-deployment "
            "and continuous testing of LLM-integrated applications."
        ),
        "para2": (
            "In the atlas: peer to `garak`, `pyrit`, `cryptex-oss`; the "
            "differentiator is provenance — a credentialed security firm "
            "(Praetorian) maintains the corpus."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "Praetorian",
        "origin_country": "US", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["garak", "pyrit", "cryptex-oss", "harmbench"],
        "sov_extra": (
            "Apache-2.0; runs locally. Target LLM is operator-supplied. "
            "Praetorian uses this internally on engagements; the OSS "
            "release is the same engine with the proprietary playbook "
            "redacted."
        ),
    },
    "sandlock": {
        "category": "redteam", "subcategory": "agent-sandbox",
        "tagline": "Process-based Linux sandbox for AI-agent tool execution — no container, no VM, no privilege.",
        "para1": (
            "Sandlock is a lightweight process-based sandbox for "
            "untrusted agent tool execution on Linux. Uses seccomp, "
            "namespaces, and cgroups directly — no container runtime, "
            "no VM, no root required."
        ),
        "para2": (
            "In the atlas: the sandbox primitive that the "
            "`audit-log-fsm-escalation` pattern's tool layer needs. "
            "Complements `e2b` (cloud sandbox), `daytona` (managed "
            "dev container) by offering a local-only option."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "multikernel",
        "origin_country": "null", "mas": 4, "posture": "local-only",
        "alignment": "full",
        "adjacent_to": ["agentdojo"],
        "sov_extra": (
            "Apache-2.0; Linux-only; runs entirely as an unprivileged "
            "user-space process. No managed-service component. The agent "
            "and the sandbox are co-located, so no agent input ever "
            "leaves the host through the sandbox itself."
        ),
    },
    "reverseclabs-spikee": {
        "category": "redteam", "subcategory": "prompt-injection-eval",
        "tagline": "Simple Prompt Injection Kit for Evaluation and Exploitation (ReversecLabs).",
        "para1": (
            "Spikee is a focused prompt-injection evaluation and "
            "exploitation kit. Small CLI, opinionated payload catalogue, "
            "designed for fast iteration during application red-team."
        ),
        "para2": (
            "In the atlas: peer to `promptfoo` (eval-side), `garak` "
            "(scanner). Differentiator is the offensive emphasis — "
            "kit is shaped for an actual red-team engagement, not for "
            "passive CI scanning."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "ReversecLabs",
        "origin_country": "null", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["garak", "promptfoo", "pyrit", "cryptex-oss"],
        "sov_extra": (
            "Apache-2.0; CLI tool; runs locally. Targets any HTTP-served "
            "LLM endpoint, so provider-agnostic."
        ),
    },
    "llmmap": {
        "category": "redteam", "subcategory": "prompt-injection-testing",
        "tagline": "Automated prompt-injection testing framework with dual-LLM architecture.",
        "para1": (
            "LLMMap is an automated prompt-injection testing framework "
            "that uses a dual-LLM architecture: one LLM generates "
            "candidate injections, a separate LLM judges responses for "
            "compromise. Inspired by the nmap workflow for traditional "
            "vuln scanning."
        ),
        "para2": (
            "In the atlas: peer to `garak`, `promptfoo` on the CI-style "
            "scanning side. Dual-LLM judge architecture is the "
            "interesting bit — same pattern as `aigis` and modern eval "
            "frameworks."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "Hellsender01",
        "origin_country": "null", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["garak", "promptfoo", "pyrit", "reverseclabs-spikee"],
        "sov_extra": (
            "MIT licence; runs locally. The 'attacker' LLM and 'judge' "
            "LLM are both operator-selected — can be the same model, "
            "different providers, or local-only (Llama, etc.)."
        ),
    },
    "agent-audit": {
        "category": "redteam", "subcategory": "static-agent-security",
        "tagline": "Static security scanner for LLM agents — prompt injection, MCP config auditing, taint analysis.",
        "para1": (
            "Agent-audit is a static-analysis tool for LLM-agent "
            "codebases. Detects prompt-injection sinks via taint "
            "analysis, audits MCP server configurations for unsafe "
            "patterns, flags missing input validation. 51 rules out of "
            "the box."
        ),
        "para2": (
            "In the atlas: novel — static-analysis-for-agents niche. "
            "Complements runtime defences (`pipelock`, `adrian`) by "
            "catching issues before deployment. Closest peer is "
            "`semgrep` rules for LLM/agent patterns."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "HeadyZhang",
        "origin_country": "CN", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["agent-security-scanner-mcp", "luckypipewrench-pipelock", "garak"],
        "sov_extra": (
            "Apache-2.0; CLI tool that runs locally against the operator's "
            "source tree. No code leaves the host; results are local "
            "JSON / SARIF. Provider-agnostic — analyses the agent code, "
            "not the model."
        ),
    },
    "seojoonkim-prompt-guard": {
        "category": "redteam", "subcategory": "prompt-injection-defence",
        "tagline": "Multi-language prompt-injection defence with severity scoring.",
        "para1": (
            "Prompt-guard (seojoonkim) is a runtime prompt-injection "
            "defence for AI agents. Multi-language detection, severity "
            "scoring, and a small declarative ruleset for "
            "tenant-specific policy."
        ),
        "para2": (
            "In the atlas: peer to `llm-guard`, `nemo-guardrails`, "
            "`pipelock`. Differentiator is the multi-language emphasis "
            "(non-English injection payloads) and severity-scoring "
            "primitive that is easy to wire into an escalation policy."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "seojoonkim",
        "origin_country": "null", "mas": 4, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["llm-guard", "nemo-guardrails", "luckypipewrench-pipelock"],
        "sov_extra": (
            "MIT licence; runs locally as middleware. No managed-service "
            "dependency. Provider-agnostic. Multi-language detection is "
            "particularly relevant for non-English deployments."
        ),
    },
    # ----- eval -----
    "open-rag-eval": {
        "category": "eval", "subcategory": "rag-eval",
        "tagline": "RAG evaluation without the need for 'golden answers' (Vectara).",
        "para1": (
            "Open-RAG-Eval is Vectara's open-source RAG evaluation "
            "framework. Reference-free metrics for faithfulness, "
            "answer relevance, and context precision — designed to "
            "score RAG systems without a labelled gold-standard set."
        ),
        "para2": (
            "In the atlas: peer to `ragas`, `trulens`, `tonic-validate`, "
            "`deepeval` on the RAG-eval shelf; differentiator is the "
            "reference-free orientation, useful when production traffic "
            "is unlabelled."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "Vectara",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["ragas", "trulens", "tonic-validate", "deepeval"],
        "sov_extra": (
            "Apache-2.0; Python library; runs locally against "
            "operator-supplied RAG endpoints and judge LLM. Judge model "
            "can be local (Llama, Mistral) or managed — operator's "
            "choice."
        ),
    },
    "kieranklaassen-leva": {
        "category": "eval", "subcategory": "ruby-llm-eval",
        "tagline": "Production-data LLM evaluation framework for Ruby on Rails apps.",
        "para1": (
            "Leva (kieranklaassen) is an LLM evaluation framework "
            "designed for Ruby on Rails applications, focused on "
            "evaluating production data (not synthetic test sets). "
            "Integrates with ActiveRecord and Rails background-job "
            "infrastructure."
        ),
        "para2": (
            "In the atlas: fills the Ruby-ecosystem gap in eval. Peer "
            "to `langfuse` and `langwatch` on the production-traces "
            "side; differentiator is Rails-native."
        ),
        "maturity": "beta",
        "maintainer_type": "individual", "maintainer_name": "kieranklaassen",
        "origin_country": "null", "mas": 5, "posture": "local-first",
        "alignment": "full",
        "adjacent_to": ["langfuse", "langwatch", "ragas"],
        "sov_extra": (
            "MIT licence; Ruby gem; runs inside the host Rails app. "
            "Evaluation judge is whatever LLM the app already uses. "
            "Provider-agnostic."
        ),
    },
}


def yaml_escape(s: str) -> str:
    return s.replace('"', '\\"')


def render(eid: str, rec: dict, cand: dict) -> str:
    license_key = cand.get("license_key") or "MIT"
    # Capitalisation expected by schema: 'Apache-2.0', 'MIT', etc.
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

    # sovereignty_notes: PROVENANCE + rec['sov_extra']
    sov_full = f"{PROVENANCE}\n  {rec['sov_extra']}"

    homepage_line = f'homepage: {homepage}\n' if homepage else ''
    adjacent_lines = "\n".join(f"  - {a}" for a in rec["adjacent_to"])
    tagline_quoted = '"' + yaml_escape(rec['tagline']) + '"'
    name_quoted = '"' + yaml_escape(eid.replace('-', ' ').title()) + '"'

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

harness_paradigm_alignment: aligned

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
