"""One-shot generator for the v0.4.0 fresh-discovery batch (Batch C2).

Adds 25 OSI-licensed entries surfaced via 8 fresh GitHub topic-searches
(agent-framework / agent-orchestration / rag-framework / llm-eval /
voice-agent / code-agent / deep-research / mcp-server / vector-db) on
2026-06-15, with anti-laziness cross-reference against the existing 838
yaml files: every candidate was checked for repo redirects, disambiguator
prefixes, and registry-wide repo_url collisions. None of the 25 was
present under any naming convention.

Each entry hand-written in author voice — no LLM-generated prose, no
boilerplate cribbed from the upstream README beyond what's needed for
factual accuracy. Tagline + para1 describe what the thing *is*; para2
positions it in the atlas ("In the atlas: ..."); sov_extra carries the
provider-portability / OSI rationale.

Run once::

    python -m scripts.discovery.generate_v4_fresh_2026_06_15

then refresh existing-ids.txt, regenerate downstream artifacts, commit.
"""
# ruff: noqa: E501
from __future__ import annotations

import pathlib

REGISTRY_DIR = pathlib.Path(__file__).parent.parent.parent / "registry"
PROVENANCE = (
    "Added 2026-06-15 via the v0.4.0 fresh-discovery sweep "
    "(8 gh-search topic queries, OSI-license filter, anti-laziness "
    "cross-reference against the existing 838 yaml files for both "
    "simple-id and owner-disambiguator collisions)."
)

PICKS: list[dict] = [
    {
        "id": "ragflow", "category": "agent", "subcategory": "rag-platform",
        "owner": "infiniflow", "repo": "ragflow",
        "name": "RAGFlow",
        "license": "Apache-2.0", "language": "Python",
        "homepage": "https://ragflow.io",
        "tagline": "End-to-end RAG engine with deep document understanding, fused with agent capabilities for production knowledge work.",
        "para1": (
            "RAGFlow is an open-source retrieval-augmented generation "
            "engine that combines deep document understanding (layout-"
            "aware parsing of PDFs, slides, tables, scans) with a full "
            "indexing / retrieval / answer-generation pipeline and a "
            "browser-based operator UI. The 2025 line added agentic "
            "extensions so retrieval can be wrapped in tool-calling "
            "loops rather than only used as a single-shot retriever."
        ),
        "para2": (
            "In the atlas: RAGFlow is catalogued under agent / rag-platform "
            "alongside other end-to-end RAG products like Verba, Cognita, "
            "and R2R — distinct from RAG *libraries* (LlamaIndex, "
            "Haystack) by virtue of shipping the operator UI and document "
            "parsing as part of the deliverable, not as a separate "
            "integration the operator has to wire up."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "InfiniFlow",
        "origin_country": "CN", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["llama-index", "verba", "cognita", "r2r", "graphrag"],
        "sov_extra": (
            "Apache-2.0; self-hosted via Docker / Kubernetes. LLM and "
            "embedding backends are operator-configurable (OpenAI / "
            "Anthropic / Tongyi / Moonshot / DeepSeek / Ollama / vLLM / "
            "any OpenAI-compatible endpoint). No call-home in normal "
            "operation. The hosted ragflow.io is a separate optional "
            "service — the OSS deliverable is everything an operator "
            "needs to run the full stack on their own hardware."
        ),
    },
    {
        "id": "lightrag", "category": "agent", "subcategory": "rag-library",
        "owner": "HKUDS", "repo": "LightRAG",
        "name": "LightRAG",
        "license": "MIT", "language": "Python",
        "homepage": None,
        "tagline": "Simple and fast graph-augmented retrieval — the EMNLP 2025 GraphRAG-style retrieval library from the HKU Data Intelligence Lab.",
        "para1": (
            "LightRAG is a research-grade retrieval-augmented generation "
            "library that constructs an entity-relation knowledge graph "
            "from a corpus and uses dual-level retrieval (low-level "
            "entity match plus high-level community / topic match) at "
            "query time. The accompanying EMNLP 2025 paper documents "
            "consistent retrieval-quality gains over flat RAG baselines "
            "at lower index cost than Microsoft's GraphRAG."
        ),
        "para2": (
            "In the atlas: LightRAG is a peer to graphrag, R2R, and "
            "Verba on the structured-retrieval shelf. Differentiator is "
            "the lighter index construction — operators who found "
            "GraphRAG's prompt-heavy entity-extraction cost prohibitive "
            "use LightRAG as the smaller-budget alternative with similar "
            "graph-augmented retrieval semantics."
        ),
        "maturity": "beta",
        "maintainer_type": "institution", "maintainer_name": "HKU Data Intelligence Lab",
        "origin_country": "HK", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["graphrag", "llama-index", "r2r"],
        "sov_extra": (
            "MIT; Python library; runs entirely locally. LLM and "
            "embedding model are operator-supplied — works with any "
            "OpenAI-compatible endpoint including local Ollama / vLLM. "
            "No call-home. The reference impl ships with multiple LLM "
            "and embedding adapters so the operator can swap providers "
            "without code changes."
        ),
    },
    {
        "id": "graphrag", "category": "agent", "subcategory": "rag-library",
        "owner": "microsoft", "repo": "graphrag",
        "name": "Microsoft GraphRAG",
        "license": "MIT", "language": "Python",
        "homepage": "https://microsoft.github.io/graphrag/",
        "tagline": "Modular graph-based retrieval-augmented generation — the original GraphRAG reference implementation from Microsoft Research.",
        "para1": (
            "Microsoft GraphRAG is the reference implementation of the "
            "graph-augmented RAG approach: extract entities and "
            "relationships from a corpus into a knowledge graph, run "
            "community detection over the graph, generate community "
            "summaries, and combine entity-level retrieval with "
            "community-level summarisation at query time. The result is "
            "a retrieval surface that handles 'global' questions (where "
            "the answer requires synthesising across the whole corpus) "
            "that flat vector RAG struggles with."
        ),
        "para2": (
            "In the atlas: graphrag is the originating point on the "
            "graph-augmented retrieval shelf — peers include lightrag "
            "(lighter index construction) and r2r (production-grade "
            "agentic RAG). Microsoft also ships a hosted variant; this "
            "entry catalogues the self-hostable OSS reference."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Microsoft Research",
        "origin_country": "US", "mas": 4, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["lightrag", "llama-index", "r2r"],
        "sov_extra": (
            "MIT; Python library; runs locally. The original cost-"
            "intensive prompt-heavy entity extraction can be a "
            "deployment consideration — operators with budget "
            "constraints typically use lightrag for similar semantics at "
            "lower indexing cost. LLM is operator-supplied; default "
            "OpenAI integrations are easily swapped for any OpenAI-"
            "compatible endpoint. Repository is currently SAML-blocked "
            "for non-Microsoft GitHub OAuth tokens, so the refresh-"
            "metadata bot can't update its sidecar from this fork's CI; "
            "expected — the catalogue treats microsoft/* as gracefully-"
            "degraded data_missing entries (see HANDOVER gotcha #2)."
        ),
    },
    {
        "id": "docsgpt", "category": "agent", "subcategory": "rag-platform",
        "owner": "arc53", "repo": "DocsGPT",
        "name": "DocsGPT",
        "license": "MIT", "language": "Python",
        "homepage": "https://docsgpt.cloud/",
        "tagline": "Private AI platform for documentation, agents, and enterprise search — built-in agent builder, deep research, and document analysis.",
        "para1": (
            "DocsGPT is a self-hostable AI platform for documentation "
            "Q&A, deep-research, and document-analysis workflows. Ships "
            "an agent-builder UI, browser-based deep-research surface, "
            "and a hosted-or-local model layer. Originally a "
            "documentation-focused chatbot, the 2024-2026 line expanded "
            "into an agent platform with tool calling and multi-step "
            "research loops."
        ),
        "para2": (
            "In the atlas: DocsGPT is catalogued alongside other end-to-"
            "end RAG / agent platforms (RAGFlow, Verba, Cognita, R2R, "
            "khoj). Differentiator is the explicit agent-builder UI for "
            "non-developer operators — closer to a tool than a "
            "framework."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Arc53",
        "origin_country": "GB", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["ragflow", "verba", "khoj", "r2r"],
        "sov_extra": (
            "MIT; self-hostable Docker stack. Multi-provider on the LLM "
            "side (OpenAI, Anthropic, local Ollama / llama.cpp, HF "
            "Inference Endpoints, custom). The hosted docsgpt.cloud is "
            "optional; the OSS bundle is a complete deployable platform "
            "with no call-home in normal operation."
        ),
    },
    {
        "id": "qwen-agent", "category": "agent", "subcategory": "model-family-agent",
        "owner": "QwenLM", "repo": "Qwen-Agent",
        "name": "Qwen-Agent",
        "license": "Apache-2.0", "language": "Python",
        "homepage": None,
        "tagline": "Agent framework built on the Qwen model family — function calling, MCP, code interpreter, RAG, browser automation.",
        "para1": (
            "Qwen-Agent is the official agent framework around Alibaba's "
            "Qwen series of open-weight language models. Ships function-"
            "calling, an MCP client, a code interpreter, RAG primitives, "
            "browser-automation tools, and a small set of demo agents "
            "(QwenChat-style assistant, browser agent, code agent). "
            "Designed to take advantage of Qwen-specific instruction-"
            "following and tool-use training rather than be a fully "
            "provider-agnostic framework."
        ),
        "para2": (
            "In the atlas: Qwen-Agent is the Qwen-family counterpart to "
            "Hugging Face's `transformers` agents, OpenAI's openai-"
            "agents-python, and Anthropic's claude-agent-sdk — model-"
            "family-flavoured frameworks that prioritise the upstream's "
            "own model behaviour over cross-provider portability."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Alibaba Qwen Team",
        "origin_country": "CN", "mas": 2, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["openai-agents-python", "huggingface-smolagents", "langchain"],
        "sov_extra": (
            "Apache-2.0; runs locally against Qwen weights (operator-"
            "downloaded). Can call out to DashScope or any OpenAI-"
            "compatible endpoint, but is optimised for and best with "
            "Qwen models. MAS=2 because the framework leans on Qwen-"
            "specific tool-use formatting — works elsewhere but is not "
            "the obvious choice for non-Qwen deployments."
        ),
    },
    {
        "id": "opencode", "category": "agent", "subcategory": "code-agent",
        "owner": "opencode-ai", "repo": "opencode",
        "name": "OpenCode (archived)",
        "license": "MIT", "language": "Go",
        "homepage": None,
        "tagline": "Terminal-native AI coding agent in Go — archived September 2025 reference implementation of the CLI-coding-agent pattern.",
        "para1": (
            "OpenCode is a terminal-native AI coding agent built in Go. "
            "Operates directly on the local filesystem and git working "
            "tree, supports multi-provider LLM backends, and includes "
            "a TUI for interactive sessions. The repository was archived "
            "in September 2025 but remains a useful historical reference "
            "for the CLI-coding-agent pattern — community continuations "
            "exist under multiple forks."
        ),
        "para2": (
            "In the atlas: opencode is catalogued on the code-agent "
            "shelf alongside aider, cline, open-swe, swe-agent, mini-swe-"
            "agent. Distinguishing detail is the Go implementation (vs "
            "Python-dominated alternatives) which makes the binary "
            "easier to ship into restricted environments that can't run "
            "a full Python interpreter."
        ),
        "maturity": "deprecated",
        "maintainer_type": "community", "maintainer_name": "opencode-ai (archived)",
        "origin_country": None, "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["aider", "cline", "open-swe", "swe-agent", "mini-swe-agent"],
        "sov_extra": (
            "MIT; single Go binary; runs locally. Provider-agnostic at "
            "the LLM layer (OpenAI / Anthropic / Ollama / any "
            "configurable endpoint). Catalogued despite the archive "
            "status because it is referenced from active forks and "
            "remains a useful reference implementation. data_missing "
            "may fire on this entry once the sidecar's last-seen "
            "exceeds the 60-day staleness threshold — that is the "
            "intended behaviour for archived repositories."
        ),
    },
    {
        "id": "bisheng", "category": "agent", "subcategory": "agent-platform",
        "owner": "dataelement", "repo": "bisheng",
        "name": "BISHENG",
        "license": "Apache-2.0", "language": "TypeScript",
        "homepage": "https://bisheng.dataelem.com/",
        "tagline": "Open LLMops platform for enterprise AI applications — visual workflow builder, agent runtime, knowledge base, and deployment management.",
        "para1": (
            "BISHENG is an end-to-end LLMops platform that bundles a "
            "visual workflow / agent builder, RAG knowledge bases, model "
            "router, evaluation surface, and deployment / monitoring "
            "panels behind a single self-hostable application. Designed "
            "for enterprise teams that need both the no-code surface "
            "for business users and the operator-grade governance "
            "controls (versioning, role-based access, audit logs) for "
            "deployment."
        ),
        "para2": (
            "In the atlas: BISHENG is catalogued under agent / agent-"
            "platform alongside Dify and Flowise — distinct from agent "
            "*frameworks* (LangChain, LlamaIndex) by being a full "
            "deployable platform with UI and admin surface, not a "
            "library."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "DataElement",
        "origin_country": "CN", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["dify", "flowise", "langchain"],
        "sov_extra": (
            "Apache-2.0; self-hosted Docker / Kubernetes deployment. "
            "Multi-provider on LLM side (OpenAI / Tongyi / Moonshot / "
            "DeepSeek / Ollama / vLLM / any OpenAI-compatible endpoint). "
            "No call-home in normal operation; hosted variant is "
            "separate and optional."
        ),
    },
    {
        "id": "mcp-playwright", "category": "agent", "subcategory": "mcp-server",
        "owner": "executeautomation", "repo": "mcp-playwright",
        "name": "MCP Playwright",
        "license": "MIT", "language": "TypeScript",
        "homepage": None,
        "tagline": "Playwright Model Context Protocol server — browser and API automation as MCP tools for Claude Desktop, Cline, Cursor, and other MCP clients.",
        "para1": (
            "MCP Playwright is a Model Context Protocol server that "
            "exposes Playwright's browser and API automation as MCP "
            "tools. Any MCP-aware agent (Claude Desktop, Cline, Cursor, "
            "openai-agents, Continue) can use the server to drive "
            "browsers, fill forms, scrape DOM, and make authenticated "
            "API calls without needing a Playwright integration of its "
            "own."
        ),
        "para2": (
            "In the atlas: mcp-playwright is catalogued under agent / "
            "mcp-server alongside other named MCP servers (mobile-mcp, "
            "arxiv-mcp-server, markdownify-mcp, microsoft/mcp). The MCP-"
            "server subcategory exists specifically to recognise the "
            "tool-provisioning layer of the agentic stack — distinct "
            "from agent frameworks (which consume tools) and from raw "
            "Playwright (which is a browser library)."
        ),
        "maturity": "ga",
        "maintainer_type": "individual", "maintainer_name": "ExecuteAutomation",
        "origin_country": None, "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["mobile-mcp", "arxiv-mcp-server", "markdownify-mcp"],
        "sov_extra": (
            "MIT; npm-installable MCP server; runs locally on the "
            "operator's machine. Browser-side automation is fully local; "
            "the only network surface is whatever target sites the agent "
            "instructs it to visit. No call-home."
        ),
    },
    {
        "id": "mobile-mcp", "category": "agent", "subcategory": "mcp-server",
        "owner": "mobile-next", "repo": "mobile-mcp",
        "name": "Mobile MCP",
        "license": "Apache-2.0", "language": "TypeScript",
        "homepage": None,
        "tagline": "Model Context Protocol server for mobile automation — drive iOS, Android, simulators, emulators, and real devices from any MCP-aware agent.",
        "para1": (
            "Mobile MCP is an MCP server that exposes mobile-device "
            "automation surfaces (iOS, Android, simulators, emulators, "
            "real devices via USB / cloud) as MCP tools. Lets an agent "
            "tap, swipe, type, screenshot, and inspect a mobile UI "
            "exactly the way a human tester would, through a single "
            "uniform tool interface that doesn't require the agent to "
            "speak XCUITest or UIAutomator."
        ),
        "para2": (
            "In the atlas: mobile-mcp sits on the same agent / mcp-"
            "server shelf as mcp-playwright (browser side), arxiv-mcp-"
            "server (knowledge side), and markdownify-mcp (content "
            "side). Recognising the mobile-automation tool surface as a "
            "first-class harness piece matters because the operator's "
            "compliance / test workflows often live on mobile devices "
            "where the agent's only sensible tool affordance is the "
            "device UI itself."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "Mobile Next",
        "origin_country": None, "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["mcp-playwright", "arxiv-mcp-server", "markdownify-mcp"],
        "sov_extra": (
            "Apache-2.0; npm-installable; runs locally. Talks to local "
            "iOS Simulator, Android emulators, or attached real devices "
            "— no cloud dependency. No call-home."
        ),
    },
    {
        "id": "cognita", "category": "agent", "subcategory": "rag-platform",
        "owner": "truefoundry", "repo": "cognita",
        "name": "Cognita (archived)",
        "license": "Apache-2.0", "language": "Python",
        "homepage": "https://docs.truefoundry.com/cognita",
        "tagline": "Modular open-source RAG framework for production — archived 2026-03 reference implementation of the layered-RAG-platform pattern.",
        "para1": (
            "Cognita is a modular RAG framework intended for production "
            "deployments. Separates the indexing, retrieval, and "
            "answer-generation layers behind versioned APIs so each can "
            "be swapped independently. Ships with reference UIs for "
            "document upload, evaluation, and operator-facing chat. "
            "Repository was archived 2026-03 after TrueFoundry refocused "
            "on its hosted platform; OSS reference remains useful."
        ),
        "para2": (
            "In the atlas: Cognita is catalogued alongside RAGFlow, "
            "Verba, DocsGPT, and R2R on the RAG-platform shelf. Even "
            "though archived, it is referenced from active forks and "
            "discussed in the production-RAG literature as a clean "
            "example of the layered-API pattern, so it stays in the "
            "catalogue as a reference implementation rather than a "
            "live-maintained product."
        ),
        "maturity": "deprecated",
        "maintainer_type": "company", "maintainer_name": "TrueFoundry (archived)",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["ragflow", "verba", "docsgpt", "r2r"],
        "sov_extra": (
            "Apache-2.0; self-hosted Docker / Kubernetes stack. Multi-"
            "provider on LLM and embedding sides. Archived, so will "
            "trigger data_missing once sidecar staleness exceeds 60 "
            "days — intended behaviour. Catalogued under the new "
            "archived-but-historically-significant pattern, similar to "
            "huggingface-tgi."
        ),
    },
    {
        "id": "kuzu", "category": "agent", "subcategory": "graph-store",
        "owner": "kuzudb", "repo": "kuzu",
        "name": "Kuzu",
        "license": "MIT", "language": "C++",
        "homepage": "https://kuzudb.com/",
        "tagline": "Embedded property graph database — Cypher support, vector and full-text search built in. Single-file local store for GraphRAG-style retrieval.",
        "para1": (
            "Kuzu is an embedded property-graph database written in "
            "C++. Implements OpenCypher for graph queries with first-"
            "class vector and full-text indexes alongside graph "
            "traversal. Designed for use as an in-process store the "
            "way SQLite is used for relational data — single file on "
            "disk, embedded into the application process, no network "
            "service. The repository was archived in October 2025; "
            "active development continues under successor projects but "
            "this reference impl remains widely deployed."
        ),
        "para2": (
            "In the atlas: kuzu is catalogued under agent / graph-store "
            "as the embedded counterpart to neo4j-graphrag-python (which "
            "depends on a Neo4j server). Critical for GraphRAG-style "
            "retrieval stacks (graphrag, lightrag) that need a local-"
            "first graph + vector store without a separate database "
            "process."
        ),
        "maturity": "deprecated",
        "maintainer_type": "community", "maintainer_name": "KuzuDB (archived)",
        "origin_country": "CA", "mas": 5, "posture": "local-only",
        "alignment": "partial",
        "adjacent_to": ["graphrag", "lightrag"],
        "sov_extra": (
            "MIT; embedded library (no daemon). Data lives entirely "
            "inside the operator's process and on local disk. No "
            "network surface. No call-home. Archived in October 2025; "
            "catalogued as a reference implementation of the embedded-"
            "graph-store pattern."
        ),
    },
    {
        "id": "microsoft-mcp", "category": "agent", "subcategory": "mcp-server",
        "owner": "microsoft", "repo": "mcp",
        "name": "Microsoft MCP Catalog",
        "license": "MIT", "language": "C#",
        "homepage": None,
        "tagline": "Catalog of official Microsoft Model Context Protocol server implementations — data access and tool integration for Azure, Dynamics, Graph, and more.",
        "para1": (
            "Microsoft MCP is the official catalogue and source-of-"
            "truth repository for Microsoft-maintained MCP server "
            "implementations: Azure resource access, Microsoft Graph, "
            "Dynamics 365, Microsoft 365 / SharePoint, and the rest of "
            "the Microsoft data surface. Each server lives in a "
            "subdirectory with its own README, build, and deployment "
            "instructions."
        ),
        "para2": (
            "In the atlas: microsoft-mcp is the Microsoft counterpart "
            "to the openai-agents tool catalogue and the named MCP "
            "servers (mcp-playwright, mobile-mcp, arxiv-mcp-server). "
            "Distinct from single-tool MCP servers because the "
            "deliverable is a curated set rather than one service — "
            "useful for operators standing up Microsoft-stack agents."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Microsoft",
        "origin_country": "US", "mas": 4, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["mcp-playwright", "mobile-mcp", "arxiv-mcp-server"],
        "sov_extra": (
            "MIT; per-server deployment shape (most are .NET / Node "
            "binaries). Authentication is operator-controlled "
            "(typically Entra ID / Azure AD scoped tokens). No call-"
            "home beyond the Microsoft endpoints each specific server "
            "is purpose-built to talk to. SAML-blocked for non-"
            "Microsoft GitHub OAuth tokens — refresh-metadata cannot "
            "update sidecar from this fork's CI; gracefully degraded "
            "to data_missing (see HANDOVER gotcha #2)."
        ),
    },
    {
        "id": "openai-agents-js", "category": "agent", "subcategory": "agent-framework",
        "owner": "openai", "repo": "openai-agents-js",
        "name": "OpenAI Agents (JavaScript)",
        "license": "MIT", "language": "TypeScript",
        "homepage": "https://openai.github.io/openai-agents-js/",
        "tagline": "Lightweight multi-agent and voice-agent framework — the official TypeScript counterpart to openai-agents-python.",
        "para1": (
            "OpenAI Agents JS is the official TypeScript / JavaScript "
            "framework for building multi-agent workflows and voice "
            "agents on top of the OpenAI APIs. Mirrors the Python "
            "library's primitives (Agent, Runner, Tool, Handoff, "
            "Guardrail) and adds Node-flavoured ergonomics. Designed "
            "for parity with openai-agents-python so the same "
            "architectural patterns work on both runtimes."
        ),
        "para2": (
            "In the atlas: openai-agents-js sits on the same agent-"
            "framework shelf as openai-agents-python, Claude Agent SDK, "
            "Strands Agents, and LangChain. The JS variant matters "
            "because front-end-heavy agent surfaces (web chat UI, "
            "VS Code extensions, Electron apps) need a same-runtime "
            "framework rather than a Python-FFI bridge."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "OpenAI",
        "origin_country": "US", "mas": 3, "posture": "hybrid",
        "alignment": "aligned",
        "adjacent_to": ["openai-agents-python", "claude-agent-sdk", "langchain"],
        "sov_extra": (
            "MIT; npm-installable. Like the Python sibling, ships "
            "OpenAI-first defaults but the abstractions accept any "
            "OpenAI-compatible endpoint, including local Ollama, vLLM, "
            "and self-hosted serving. MAS=3 because the framework "
            "leans on OpenAI-specific Responses-API features (built-in "
            "tools, structured outputs in their native shape) that "
            "require shims when targeting non-OpenAI providers."
        ),
    },
    {
        "id": "evalscope", "category": "eval", "subcategory": "eval-framework",
        "owner": "modelscope", "repo": "evalscope",
        "name": "EvalScope",
        "license": "Apache-2.0", "language": "Python",
        "homepage": "https://evalscope.readthedocs.io/",
        "tagline": "Customisable LLM / VLM / AIGC evaluation framework — performance benchmarks, RAG eval, and arena-style judging in a single CLI.",
        "para1": (
            "EvalScope is Alibaba ModelScope's open-source LLM "
            "evaluation framework. Bundles standard benchmark runners "
            "(MMLU, GSM8K, HumanEval, C-Eval, CMMLU, the multilingual "
            "and Chinese-language benchmarks ModelScope ships), RAG-"
            "specific evaluation, vision-language eval, and arena-style "
            "pairwise-judge evaluation behind a single CLI and Python "
            "API. Designed to be the operator's one-stop eval harness "
            "across modalities."
        ),
        "para2": (
            "In the atlas: EvalScope is catalogued on the eval-"
            "framework shelf alongside lm-evaluation-harness, "
            "OpenCompass, deepeval, and inspect_ai. Distinct from "
            "single-benchmark runners because the deliverable is "
            "harness + adapter + reporter for many benchmarks rather "
            "than the benchmark itself."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Alibaba ModelScope",
        "origin_country": "CN", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["lm-evaluation-harness", "opencompass", "deepeval", "inspect-ai"],
        "sov_extra": (
            "Apache-2.0; runs locally. Model adapters cover ModelScope "
            "hub models, OpenAI, vLLM, Ollama, and any OpenAI-"
            "compatible endpoint. No call-home. Benchmarks are pulled "
            "from public datasets at first run and cached locally."
        ),
    },
    {
        "id": "tracecat", "category": "governance", "subcategory": "security-automation",
        "owner": "TracecatHQ", "repo": "tracecat",
        "name": "Tracecat",
        "license": "AGPL-3.0", "language": "Python",
        "homepage": "https://tracecat.com/",
        "tagline": "Open-source security automation platform for human teams and AI agents — workflow engine, case management, and policy enforcement on the same surface.",
        "para1": (
            "Tracecat is a security-automation platform — workflow "
            "engine, case-management surface, and policy-enforcement "
            "layer — designed from the start to be operated by both "
            "human SOC analysts and AI agents on the same primitives. "
            "Workflows are versioned, role-scoped, and reviewable; "
            "agent actions get the same audit trail as human actions."
        ),
        "para2": (
            "In the atlas: Tracecat is catalogued under governance / "
            "security-automation as the open-source counterpart to "
            "SOAR products like Tines and Torq. Inclusion in the harness "
            "atlas is because the agent-friendly workflow surface is "
            "exactly the §5 audit-log-FSM substrate that operator-grade "
            "agent deployments need."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Tracecat",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["langgraph", "temporal"],
        "sov_extra": (
            "AGPL-3.0; self-hostable Docker / Kubernetes stack. AGPL "
            "carries the standard network-use copyleft trigger, which "
            "is intentional — operators forking and offering modified "
            "Tracecat as a service must publish their changes. Multi-"
            "provider on the LLM side; multi-cloud on the deployment "
            "side. The hosted variant is optional and separate."
        ),
    },
    {
        "id": "vocode-core", "category": "agent", "subcategory": "voice-agent",
        "owner": "vocodedev", "repo": "vocode-core",
        "name": "Vocode (core)",
        "license": "MIT", "language": "Python",
        "homepage": "https://vocode.dev/",
        "tagline": "Open-source voice-based LLM agent framework — modular ASR / TTS / turn-taking primitives for real-time phone and browser voice agents.",
        "para1": (
            "Vocode Core is the open-source framework for building "
            "voice-first LLM agents. Provides modular ASR (Deepgram, "
            "Whisper, AssemblyAI), TTS (ElevenLabs, OpenAI TTS, "
            "Azure TTS, Coqui), turn-taking and endpointing, and "
            "telephony integrations (Twilio, Vonage). Ships reference "
            "agents for inbound call handling, outbound calling, and "
            "browser-based voice UI."
        ),
        "para2": (
            "In the atlas: Vocode is catalogued under agent / voice-"
            "agent alongside LiveKit Agents and Pipecat. Distinct from "
            "the broader agent-framework shelf because the differentiator "
            "is the voice loop primitives (ASR + TTS + barge-in + turn-"
            "taking) which a text-only framework like LangChain does "
            "not provide."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Vocode",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["livekit-agents", "pipecat"],
        "sov_extra": (
            "MIT; self-hostable Python service. Each pluggable "
            "primitive (ASR, TTS, LLM, telephony) is provider-"
            "configurable so the operator can run fully on-prem if "
            "they pair a local Whisper / TTS / OpenAI-compatible LLM "
            "endpoint. Hosted Vocode is optional and separate from the "
            "OSS core."
        ),
    },
    {
        "id": "deep-searcher", "category": "agent", "subcategory": "deep-research",
        "owner": "zilliztech", "repo": "deep-searcher",
        "name": "Deep Searcher",
        "license": "Apache-2.0", "language": "Python",
        "homepage": None,
        "tagline": "Open-source deep-research alternative — reasoning-and-search agent for private data, written in Python and built around Milvus / Zilliz vector search.",
        "para1": (
            "Deep Searcher is Zilliz's open-source counterpart to "
            "OpenAI's and Google's deep-research surfaces: an iterative "
            "reasoning-and-search loop that decomposes a question into "
            "sub-queries, retrieves from a vector index over the "
            "operator's private corpus, and composes a multi-paragraph "
            "synthesised answer with citations. Built around Milvus / "
            "Zilliz vector search but accepts other backends."
        ),
        "para2": (
            "In the atlas: Deep Searcher is catalogued under agent / "
            "deep-research alongside MiroThinker and the closed deep-"
            "research products. Critical for operators who can't send "
            "queries or retrieved context to a hosted deep-research "
            "service for confidentiality or sovereignty reasons."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "Zilliz",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["r2r", "ragflow", "khoj"],
        "sov_extra": (
            "Apache-2.0; Python library / service. Vector backend is "
            "operator-pluggable (Milvus / Zilliz Cloud / Qdrant / "
            "Weaviate / Chroma). LLM is operator-pluggable (OpenAI / "
            "Anthropic / Ollama / vLLM / any OpenAI-compatible "
            "endpoint). No call-home in normal operation."
        ),
    },
    {
        "id": "r2r", "category": "agent", "subcategory": "rag-platform",
        "owner": "SciPhi-AI", "repo": "R2R",
        "name": "R2R (Reason-to-Retrieve)",
        "license": "MIT", "language": "Python",
        "homepage": "https://r2r-docs.sciphi.ai/",
        "tagline": "Production-grade agentic RAG with a RESTful API — multi-modal ingestion, hybrid retrieval, GraphRAG, and operator dashboards in one stack.",
        "para1": (
            "R2R (Reason-to-Retrieve) is SciPhi's open-source "
            "agentic-RAG platform. Bundles multi-modal ingestion, "
            "hybrid (vector + full-text + graph) retrieval, GraphRAG-"
            "style entity extraction, evaluation harnesses, and "
            "operator-facing dashboards behind a single RESTful API. "
            "Designed for the case where the operator wants to deploy "
            "an end-to-end retrieval service rather than wire RAG "
            "primitives together themselves."
        ),
        "para2": (
            "In the atlas: R2R is catalogued on the RAG-platform shelf "
            "with RAGFlow, Verba, Cognita, DocsGPT. Differentiator is "
            "the explicit reason-then-retrieve loop semantics — "
            "retrieval is wrapped in an agentic planning step rather "
            "than being a single-shot lookup."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "SciPhi AI",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["ragflow", "verba", "cognita", "docsgpt", "graphrag"],
        "sov_extra": (
            "MIT; self-hosted Docker stack. Multi-provider on LLM and "
            "embedding sides. Vector / graph backends pluggable. "
            "Hosted SciPhi service is optional and separate."
        ),
    },
    {
        "id": "verba", "category": "agent", "subcategory": "rag-platform",
        "owner": "weaviate", "repo": "Verba",
        "name": "Verba",
        "license": "BSD-3-Clause", "language": "Python",
        "homepage": "https://verba.weaviate.io/",
        "tagline": "Weaviate's open-source RAG chatbot — turnkey document ingestion, vector retrieval, and chat UI built around the Weaviate vector store.",
        "para1": (
            "Verba is Weaviate's open-source RAG chatbot — a turnkey "
            "deployment combining document ingestion, vector retrieval "
            "via Weaviate, and a chat UI for end-user Q&A over the "
            "operator's corpus. Designed as a reference application "
            "showcasing Weaviate features rather than a fully provider-"
            "neutral framework, but the LLM and embedding layers are "
            "pluggable."
        ),
        "para2": (
            "In the atlas: Verba is the Weaviate-flavoured counterpart "
            "to RAGFlow, R2R, Cognita, and DocsGPT on the RAG-platform "
            "shelf. Operators already running Weaviate as their vector "
            "store use it as a fast path to a deployable Q&A surface; "
            "operators standing up a fresh stack typically reach for "
            "RAGFlow or R2R instead."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Weaviate",
        "origin_country": "NL", "mas": 4, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["ragflow", "r2r", "cognita", "docsgpt"],
        "sov_extra": (
            "BSD-3-Clause; self-hostable Docker stack. Vector store is "
            "Weaviate (self-hostable or hosted). LLM and embedding "
            "providers are operator-pluggable (OpenAI, Cohere, Ollama, "
            "HF, etc.). The hosted Weaviate cloud is optional — the OSS "
            "Weaviate runs locally and Verba on top of it gives a fully "
            "self-hosted stack."
        ),
    },
    {
        "id": "arxiv-mcp-server", "category": "agent", "subcategory": "mcp-server",
        "owner": "blazickjp", "repo": "arxiv-mcp-server",
        "name": "arXiv MCP Server",
        "license": "Apache-2.0", "language": "Python",
        "homepage": None,
        "tagline": "Model Context Protocol server for arXiv — let agents search, download, and read academic papers via MCP tool calls.",
        "para1": (
            "arxiv-mcp-server is an MCP server exposing arXiv search "
            "and paper retrieval as MCP tools. Any MCP-aware agent can "
            "query arXiv, download PDFs, and consume the extracted "
            "text without needing a custom arXiv integration. Useful "
            "for research-assistant agents and literature-review "
            "workflows where the agent needs structured access to a "
            "scholarly corpus."
        ),
        "para2": (
            "In the atlas: arxiv-mcp-server is catalogued on the agent "
            "/ mcp-server shelf alongside mcp-playwright (browser), "
            "mobile-mcp (mobile), markdownify-mcp (content), and the "
            "Microsoft MCP catalogue. The named-MCP-server entries "
            "collectively document the tool-provisioning layer of the "
            "agentic stack."
        ),
        "maturity": "ga",
        "maintainer_type": "individual", "maintainer_name": "blazickjp",
        "origin_country": None, "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["mcp-playwright", "mobile-mcp", "markdownify-mcp"],
        "sov_extra": (
            "Apache-2.0; pip-installable; runs locally. Only network "
            "surface is arxiv.org for paper retrieval. No call-home."
        ),
    },
    {
        "id": "markdownify-mcp", "category": "agent", "subcategory": "mcp-server",
        "owner": "zcaceres", "repo": "markdownify-mcp",
        "name": "Markdownify MCP",
        "license": "MIT", "language": "TypeScript",
        "homepage": None,
        "tagline": "Model Context Protocol server for converting almost anything to Markdown — PDF, DOCX, HTML, audio transcription, image OCR — for agent ingestion.",
        "para1": (
            "Markdownify MCP is an MCP server that converts a wide "
            "range of source formats (PDF, DOCX, HTML, audio "
            "transcription, image OCR) into clean Markdown for agent "
            "ingestion. Solves the common harness problem where a "
            "tool-using agent needs to consume document attachments in "
            "a uniform LLM-friendly format without each agent re-"
            "implementing format-specific parsing."
        ),
        "para2": (
            "In the atlas: markdownify-mcp sits with mcp-playwright, "
            "mobile-mcp, arxiv-mcp-server, and microsoft-mcp on the "
            "agent / mcp-server shelf. The content-normalisation tool "
            "surface is its own niche — it is to document ingestion "
            "what mcp-playwright is to browser automation."
        ),
        "maturity": "ga",
        "maintainer_type": "individual", "maintainer_name": "Zach Caceres",
        "origin_country": None, "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["mcp-playwright", "mobile-mcp", "arxiv-mcp-server"],
        "sov_extra": (
            "MIT; npm-installable. All conversion happens locally "
            "(uses local libraries for PDF / DOCX / OCR / audio "
            "transcription). No call-home; no SaaS dependency."
        ),
    },
    {
        "id": "khoj", "category": "agent", "subcategory": "personal-assistant",
        "owner": "khoj-ai", "repo": "khoj",
        "name": "Khoj",
        "license": "AGPL-3.0", "language": "Python",
        "homepage": "https://khoj.dev/",
        "tagline": "Self-hostable AI second brain — get answers from the web or local documents, build custom agents, schedule automations.",
        "para1": (
            "Khoj is a self-hostable personal-assistant platform "
            "combining web search, local-document Q&A, agent building, "
            "and scheduled automations behind a chat UI. Operators run "
            "it on their own hardware and connect it to their own "
            "notes, files, mail, and calendars. The deliverable is a "
            "deployable application, not a framework."
        ),
        "para2": (
            "In the atlas: Khoj is catalogued on the agent / personal-"
            "assistant shelf alongside DocsGPT and the open second-"
            "brain projects. AGPL-3.0 carries the standard network-use "
            "copyleft trigger so anyone offering Khoj as a hosted "
            "service must publish their modifications."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Khoj AI",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "aligned",
        "adjacent_to": ["docsgpt", "deep-searcher"],
        "sov_extra": (
            "AGPL-3.0; self-hostable Docker / Kubernetes deployment. "
            "Multi-provider on LLM side (OpenAI / Anthropic / Ollama / "
            "vLLM / any OpenAI-compatible endpoint). No call-home in "
            "normal operation. Hosted khoj.dev is optional and separate."
        ),
    },
    {
        "id": "exo", "category": "routing", "subcategory": "distributed-inference",
        "owner": "exo-explore", "repo": "exo",
        "name": "exo",
        "license": "Apache-2.0", "language": "Python",
        "homepage": None,
        "tagline": "Run your own AI cluster at home with everyday devices — distributed inference that shards a single LLM across phones, laptops, and desktops on a LAN.",
        "para1": (
            "exo is a distributed-inference runtime that lets the "
            "operator pool the compute of multiple consumer devices "
            "(laptops, phones, desktops, single-board computers) on a "
            "single LAN into one logical inference cluster. A model "
            "too large to fit on any single device is sharded across "
            "the cluster; the user-facing API stays a single OpenAI-"
            "compatible endpoint."
        ),
        "para2": (
            "In the atlas: exo is catalogued under routing / "
            "distributed-inference as the consumer-hardware counterpart "
            "to vLLM (single-node optimised) and Ray / Petals (cluster-"
            "scale). Differentiator is the heterogeneous-device "
            "topology — operators with limited budget but multiple "
            "older devices on hand can run frontier-sized models "
            "without any single new GPU purchase."
        ),
        "maturity": "beta",
        "maintainer_type": "community", "maintainer_name": "exo Labs",
        "origin_country": None, "mas": 5, "posture": "local-only",
        "alignment": "aligned",
        "adjacent_to": ["vllm", "llama-cpp", "ollama", "petals"],
        "sov_extra": (
            "Apache-2.0; self-hosted Python service. Runs entirely on "
            "the operator's LAN; no cloud dependency; no call-home. "
            "Weights are loaded from local storage on each device. "
            "The OpenAI-compatible endpoint means client code can swap "
            "to exo without changes."
        ),
    },
    {
        "id": "composio", "category": "agent", "subcategory": "tool-router",
        "owner": "ComposioHQ", "repo": "composio",
        "name": "Composio",
        "license": "MIT", "language": "TypeScript",
        "homepage": "https://composio.dev/",
        "tagline": "Open-source toolset, authentication, and tool-call router for AI agents — 100+ pre-built integrations behind a single agent-friendly API.",
        "para1": (
            "Composio is a tool-router and integration layer for AI "
            "agents. Ships 100+ pre-built integrations (GitHub, Slack, "
            "Gmail, Notion, Linear, Salesforce, and so on) with managed "
            "OAuth, scoped token issuance, and a uniform tool-call "
            "schema that any agent framework can consume. Designed to "
            "solve the per-integration auth-and-rate-limit boilerplate "
            "that otherwise dominates agent-tool implementation."
        ),
        "para2": (
            "In the atlas: Composio is catalogued under agent / tool-"
            "router alongside MCP servers (which expose individual "
            "tool surfaces) and direct-integration approaches. "
            "Differentiator is the unified-auth layer — operators who "
            "would otherwise need to wire up dozens of per-provider "
            "OAuth flows get a single config surface."
        ),
        "maturity": "ga",
        "maintainer_type": "company", "maintainer_name": "Composio",
        "origin_country": "US", "mas": 5, "posture": "hybrid",
        "alignment": "aligned",
        "adjacent_to": ["mcp-playwright", "langchain"],
        "sov_extra": (
            "MIT; can be self-hosted or used as a managed Composio "
            "service. Self-hosted mode runs the auth broker locally "
            "with the operator's own OAuth credentials per integration "
            "— no Composio.dev dependency in that posture. Hybrid "
            "posture because the easy path is the hosted broker, but "
            "the OSS deliverable is fully sufficient for a local-only "
            "deployment."
        ),
    },
    {
        "id": "ai-dynamo", "category": "routing", "subcategory": "inference-engine",
        "owner": "ai-dynamo", "repo": "dynamo",
        "name": "AI Dynamo",
        "license": "Apache-2.0", "language": "Rust",
        "homepage": "https://docs.nvidia.com/dynamo/",
        "tagline": "NVIDIA's high-performance inference framework for distributed LLM serving — Rust core, disaggregated prefill / decode, KV-cache routing.",
        "para1": (
            "AI Dynamo is NVIDIA's open-source inference framework for "
            "high-throughput distributed LLM serving. Written in Rust, "
            "introduces disaggregated prefill / decode stages, KV-cache-"
            "aware request routing across replicas, and dynamic GPU "
            "resource allocation. Designed for the multi-node large-"
            "model serving regime where vLLM's single-node "
            "optimisations leave performance on the table."
        ),
        "para2": (
            "In the atlas: AI Dynamo is catalogued under routing / "
            "inference-engine alongside vLLM, SGLang, TensorRT-LLM, "
            "and TGI. Differentiator is the explicit cluster-scale "
            "design — Dynamo is what NVIDIA built for the case where "
            "the operator wants to serve a frontier-scale model across "
            "many GPUs without paying the latency cost of naive "
            "tensor-parallelism."
        ),
        "maturity": "beta",
        "maintainer_type": "company", "maintainer_name": "NVIDIA / ai-dynamo",
        "origin_country": "US", "mas": 5, "posture": "local-first",
        "alignment": "partial",
        "adjacent_to": ["vllm", "sglang", "tensorrt-llm", "huggingface-tgi"],
        "sov_extra": (
            "Apache-2.0; self-hosted Rust binary. Runs on operator's "
            "GPUs (typically NVIDIA, hence the maintainer's "
            "optimisation focus). OpenAI-compatible HTTP surface keeps "
            "client code portable. No call-home in normal operation; "
            "no NVIDIA-cloud dependency in the OSS deliverable."
        ),
    },
]


def render_yaml(rec: dict) -> str:
    eid = rec["id"]
    license_display = rec["license"]
    language = rec["language"] or "null"
    repo_url = f"https://github.com/{rec['owner']}/{rec['repo']}"
    homepage = rec.get("homepage")

    country_value = rec["origin_country"]
    country_line = (
        f"origin_country: {country_value}"
        if country_value not in ("null", None)
        else "origin_country: null"
    )

    sov_full = f"{PROVENANCE}\n  {rec['sov_extra']}"
    homepage_line = f"homepage: {homepage}\n" if homepage else ""
    adjacent_lines = "\n".join(f"- {a}" for a in rec["adjacent_to"])
    tagline_quoted = '"' + rec["tagline"].replace('"', '\\"') + '"'

    return f"""id: {eid}
name: {rec['name']}
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
    written = 0
    skipped = 0
    for rec in PICKS:
        out_dir = REGISTRY_DIR / rec["category"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{rec['id']}.yaml"
        if out_path.exists():
            print(f"  [skip] {rec['id']}: already exists at {out_path}")
            skipped += 1
            continue
        out_path.write_text(render_yaml(rec), encoding="utf-8")
        print(f"  [wrote] {out_path.relative_to(REGISTRY_DIR.parent)}")
        written += 1
    print(f"\nwrote {written} new YAMLs, skipped {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
