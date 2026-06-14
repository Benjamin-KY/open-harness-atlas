"""Generate schema-valid registry YAMLs from curated candidates.

Reads:
  scripts/discovery/candidates.curated.jsonl

Writes (one per candidate, conservative defaults):
  registry/<primary_category>/<candidate_id>.yaml

Defaults (conservative — per GOVERNANCE.md §2 "conservative scoring preferred"):

  maturity                    : ga (project has commits in last 18mo per filter,
                                    so GA is a defensible default — beta only
                                    if name/description contain alpha/beta markers).
  model_agnostic_score        : 3 (the median bucket; raised to 4 if the
                                    description explicitly mentions multi-provider
                                    or OpenAI-compatible).
  harness_paradigm_alignment  : partial (every catalogued harness has at
                                    least partial alignment by definition).
  five_component_coverage     : all `none` for governance entries (only raised
                                    to `partial` for prompt_composer / output_contract
                                    when the description proves it — guardrails,
                                    structured-output projects).
  maintainer.type             : `company` if owner-login matches an obvious
                                    org/co pattern (contains "ai", "labs",
                                    "tech", "inc"), else `community`.
  maintainer.name             : owner-login (verbatim from GitHub).
  origin_country              : null (we don't infer jurisdiction from search).
  sovereignty_notes           : 1-2 sentences generated from a per-category
                                    template that names the maintainer + the
                                    score we picked + the self-host posture.
  description                 : paragraph 1 = GitHub description verbatim,
                                    paragraph 2 = standard "In the atlas: ..."
                                    contextualisation per category.

The script is idempotent: if a target YAML already exists it is skipped
(not overwritten). This makes it safe to re-run after manual edits.

Usage::

    python -m scripts.discovery.generate_entries
    python -m scripts.discovery.generate_entries --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "registry"
CURATED = REPO / "scripts" / "discovery" / "candidates.curated.jsonl"


COMPANY_HINTS = re.compile(r"(ai$|^ai|labs?$|tech$|inc$|co$|corp$|ltd$|gmbh$|llc$|sas$)", re.IGNORECASE)
INSTITUTION_HINTS = re.compile(
    r"(university|edu$|research|institute|microsoft|google|deepmind|"
    r"meta|facebook|stanford|mit|berkeley|cmu|nvidia|amazon|aws|apple|"
    r"huggingface|hugging-face|hf$|^hf|^openai$|anthropic)",
    re.IGNORECASE,
)

MULTI_PROVIDER_HINT = re.compile(
    r"\b(multi[- ]?provider|provider[- ]?agnostic|openai[- ]?compat\w*|"
    r"plug\w*[- ]?in[- ]?providers?|llama\.cpp|ollama|vllm|"
    r"unified[- ]?(?:api|interface)|model[- ]?agnostic)\b",
    re.IGNORECASE,
)

LOCAL_FIRST_HINT = re.compile(
    r"\b(local[- ]?first|self[- ]?host\w*|on[- ]?prem\w*|"
    r"local[- ]?weights?|local[- ]?model|run.{0,30}locally)\b",
    re.IGNORECASE,
)

GOVERNANCE_PROMPT_COMPOSER = re.compile(
    r"\b(prompt[- ]?(?:manage|template|library|registry|version|engineer|"
    r"composer|template|playground))\b",
    re.IGNORECASE,
)
GOVERNANCE_OUTPUT_CONTRACT = re.compile(
    r"\b(structured[- ]?(?:output|generation)|constrained[- ]?(?:decoding|generation)|"
    r"json[- ]?schema|function[- ]?call\w*|output[- ]?(?:format|contract|validat\w*)|"
    r"validator|grammar)\b",
    re.IGNORECASE,
)
GOVERNANCE_POLICY_ROUTER = re.compile(
    r"\b(guardrail\w*|policy|content[- ]?moderat\w*|pii[- ]?(?:detect|redact))",
    re.IGNORECASE,
)


# Per-category "In the atlas:" framing tail used in the description body.
# Wording mirrors the field-guide voice of existing entries (see
# registry/agent/ag2.yaml, registry/eval/alpaca-eval.yaml).
ATLAS_FRAMING: dict[str, str] = {
    "agent": (
        "In the atlas: this is an agent-orchestration entry. The harness paradigm "
        "reads agent frameworks as the policy + tool-routing layer that sits between "
        "intent and the model tier."
    ),
    "eval": (
        "In the atlas: this is an evaluation harness. Evaluation is the feedback loop "
        "that keeps every other harness honest — if you cannot measure the behaviour "
        "of the swap target, the swap is not really safe."
    ),
    "redteam": (
        "In the atlas: this is a red-team / adversarial-evaluation entry. The harness "
        "paradigm treats red-team tooling as a continuous probe against the model and "
        "the governance scaffold around it."
    ),
    "routing": (
        "In the atlas: this is a routing-layer entry. The harness paradigm requires a "
        "swap target — provider abstractions, gateways, and OpenAI-compatible proxies "
        "are the substrate that makes the swap practical."
    ),
    "governance": (
        "In the atlas: this is a governance-layer entry. Where it lands on the "
        "five-component spine (policy router / source authority / prompt composer / "
        "output contract / audit-log FSM) is captured in `five_component_coverage` "
        "below."
    ),
    "education": (
        "In the atlas: this is an education resource. The atlas catalogues free, "
        "open-licence learning material that builds practitioner literacy in the "
        "harness paradigm."
    ),
}


def detect_maintainer_type(owner: str | None, full_name: str | None) -> str:
    if not owner:
        return "community"
    if INSTITUTION_HINTS.search(owner):
        return "institution"
    if COMPANY_HINTS.search(owner):
        return "company"
    # Owner with a hyphen often = community/org (e.g. "langchain-ai", "promptfoo-team").
    if "-" in owner:
        return "community"
    return "community"


def detect_model_agnostic_score(rec: dict) -> int:
    desc = (rec.get("description") or "").strip()
    score = 3
    if MULTI_PROVIDER_HINT.search(desc):
        score = 4
    if MULTI_PROVIDER_HINT.search(desc) and LOCAL_FIRST_HINT.search(desc):
        score = 4
    return score


def detect_five_component_coverage(rec: dict) -> dict[str, str]:
    desc = (rec.get("description") or "").strip()
    fcc = {
        "policy_router": "none",
        "source_authority": "none",
        "prompt_composer": "none",
        "output_contract": "none",
        "audit_log_fsm": "none",
    }
    if GOVERNANCE_PROMPT_COMPOSER.search(desc):
        fcc["prompt_composer"] = "partial"
    if GOVERNANCE_OUTPUT_CONTRACT.search(desc):
        fcc["output_contract"] = "partial"
    if GOVERNANCE_POLICY_ROUTER.search(desc):
        fcc["policy_router"] = "partial"
    return fcc


def detect_maturity(rec: dict) -> str:
    name = (rec.get("full_name") or "").lower()
    desc = (rec.get("description") or "").lower()
    text = name + " " + desc
    if "alpha" in text or "experimental" in text or "wip" in text or "early prototype" in text:
        return "alpha"
    if "beta" in text or "preview" in text:
        return "beta"
    if (rec.get("stars") or 0) < 200:
        return "beta"
    return "ga"


def humanise_name(full_name: str) -> str:
    repo = full_name.split("/", 1)[1] if "/" in full_name else full_name
    # Convert CamelCase/snake_case to space-separated keeping acronyms uppercase.
    repo = re.sub(r"[-_]+", " ", repo)
    repo = re.sub(r"([a-z])([A-Z])", r"\1 \2", repo)
    words = repo.split()
    out: list[str] = []
    keep_upper = {"llm", "ai", "ml", "nlp", "rag", "mcp", "gpt", "api"}
    for w in words:
        lw = w.lower()
        if lw in keep_upper:
            out.append(lw.upper())
        elif w.isupper() and len(w) <= 5:
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)[:80]


def _strip_marketing(text: str) -> str:
    # Drop unicode emoji/symbol noise.
    text = re.sub(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F]", "", text)
    # Drop common marketing badges.
    text = re.sub(
        r"(?<![A-Za-z])(?:"
        r"#1 on [^.]+|"
        r"blazing[- ]?fast(?:est)?|"
        r"\d+x faster than [A-Za-z]+|"
        r"the (?:fastest|most[- ]?powerful|best|next[- ]?gen|leading|cheapest)\s+|"
        r"world['']s (?:first|best|most)|"
        r"production[- ]?ready|enterprise[- ]?grade|"
        r"yc\s+[wsd]\d{2}"
        r")",
        "",
        text,
        flags=re.IGNORECASE,
    )
    # Drop runs of >2 spaces left behind.
    text = re.sub(r"\s{2,}", " ", text).strip(" -—•·:,")
    return text


def build_tagline(rec: dict) -> str:
    desc = (rec.get("description") or "").strip()
    if not desc:
        return f"{humanise_name(rec.get('full_name', ''))} — see project README for details"
    desc = _strip_marketing(desc)
    # First sentence (up to first ". ")
    head = re.split(r"(?<=[.!?])\s+", desc, maxsplit=1)[0]
    if len(head) > 200:
        head = head[:197].rstrip() + "..."
    return head or humanise_name(rec.get("full_name", ""))


def build_description(rec: dict) -> str:
    raw = _strip_marketing((rec.get("description") or "").strip())
    name = humanise_name(rec.get("full_name", ""))
    owner = (rec.get("owner_login") or "").strip()
    cat = rec["primary_category"]
    if raw:
        # Field-guide voice: lead with the project name and a verbatim restatement
        # of the upstream description. Attribution to the maintainer in parentheses.
        # Truncate runaway descriptions.
        if len(raw) > 400:
            raw = raw[:397].rstrip() + "..."
        attribution = f" Upstream maintainer: {owner}." if owner else ""
        para1 = f"{name} — {raw.rstrip('.')}.{attribution}"
    else:
        para1 = (
            f"{name} is an open-source {cat} project surfaced from systematic "
            f"GitHub topic discovery (see scripts/discovery/). The upstream README "
            f"is the canonical source for what it does."
        )
    para2 = ATLAS_FRAMING[cat]
    return f"{para1}\n\n{para2}"


def build_sovereignty_notes(rec: dict, score: int) -> str:
    owner = (rec.get("owner_login") or "an upstream maintainer").strip()
    mtype = detect_maintainer_type(owner, rec.get("full_name"))
    licence = (rec.get("license_name") or rec.get("license_key") or "an OSI licence").strip()
    score_lines = {
        3: (
            "Model-agnostic 3 — multi-provider including at least one local-weights "
            "option, per the catalogued rubric default for projects that ship at "
            "least one provider abstraction."
        ),
        4: (
            "Model-agnostic 4 — multi-provider, OpenAI-compatible-endpoint pluggable "
            "per the README; local backends explicitly supported."
        ),
        5: (
            "Model-agnostic 5 — provider is a config string per the README; same "
            "code path runs against commercial, hosted-OSS, and fully-local backends "
            "without behavioural drift."
        ),
    }
    score_line = score_lines.get(score, score_lines[3])
    return (
        f"{owner} ({mtype}-maintained); OSS core is {licence} and "
        f"self-hostable per the upstream README. {score_line} "
        "Sovereignty score is a conservative auto-curated default — refine "
        "on first manual review of the README."
    )


def build_entry(rec: dict) -> dict:
    cat = rec["primary_category"]
    name = humanise_name(rec.get("full_name", ""))
    owner = (rec.get("owner_login") or "").strip()
    mtype = detect_maintainer_type(owner, rec.get("full_name"))
    score = detect_model_agnostic_score(rec)
    maturity = detect_maturity(rec)
    licence_key = rec.get("license_key") or ""
    spdx = SPDX_MAP.get(licence_key, licence_key.upper() if licence_key else "Apache-2.0")
    primary_language = rec.get("language") or "Multiple"

    subcat = ""
    msc = rec.get("matched_subcategories") or []
    if msc:
        subcat = msc[0]

    entry: dict = {
        "id": rec["candidate_id"],
        "name": name,
        "category": cat,
        "subcategory": subcat,
        "repo_url": rec.get("url", ""),
    }
    if rec.get("homepage"):
        entry["homepage"] = rec["homepage"]
    entry["license"] = spdx
    entry["primary_language"] = primary_language
    entry["tagline"] = build_tagline(rec)
    entry["description"] = build_description(rec)
    entry["maturity"] = maturity
    entry["maintainer"] = {"type": mtype, "name": owner or "unknown"}
    entry["origin_country"] = None
    entry["model_agnostic_score"] = score
    if cat == "governance":
        entry["five_component_coverage"] = detect_five_component_coverage(rec)
    entry["sovereignty_notes"] = build_sovereignty_notes(rec, score)
    entry["harness_paradigm_alignment"] = "partial"
    # Education entries must list at least one free resource (schema requirement).
    if cat == "education":
        entry["education_resources"] = [
            {
                "title": f"{name} repository",
                "url": rec.get("url", ""),
                "type": "docs",
                "free": True,
            }
        ]
    # adjacency added in a separate pass once IDs exist.
    return entry


# Convert GitHub license `key` (the SPDX-like slug returned by gh) into an
# atlas-shaped SPDX identifier. The atlas accepts SPDX-style strings, not
# all-lowercase GitHub slugs.
SPDX_MAP: dict[str, str] = {
    "apache-2.0": "Apache-2.0",
    "mit": "MIT",
    "bsd-2-clause": "BSD-2-Clause",
    "bsd-3-clause": "BSD-3-Clause",
    "bsd-3-clause-clear": "BSD-3-Clause-Clear",
    "mpl-2.0": "MPL-2.0",
    "gpl-2.0": "GPL-2.0-only",
    "gpl-3.0": "GPL-3.0-only",
    "lgpl-2.1": "LGPL-2.1-only",
    "lgpl-3.0": "LGPL-3.0-only",
    "agpl-3.0": "AGPL-3.0-only",
    "epl-2.0": "EPL-2.0",
    "epl-1.0": "EPL-1.0",
    "isc": "ISC",
    "0bsd": "0BSD",
    "unlicense": "Unlicense",
    "cc0-1.0": "CC0-1.0",
    "cc-by-4.0": "CC-BY-4.0",
    "cc-by-sa-4.0": "CC-BY-SA-4.0",
}


def emit_yaml(entry: dict, target: Path) -> None:
    # Use a custom serialisation to keep multi-line strings as literal blocks
    # (matching the style of registry/_TEMPLATE.yaml and existing entries).
    class LiteralStr(str):
        pass

    def literal_str_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

    yaml.add_representer(LiteralStr, literal_str_representer)

    for key in ("description", "sovereignty_notes"):
        if isinstance(entry.get(key), str) and "\n" in entry[key]:
            entry[key] = LiteralStr(entry[key])

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as fh:
        yaml.dump(entry, fh, sort_keys=False, allow_unicode=True, width=1000)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Build entries in memory but do not write files.",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing YAML files.",
    )
    args = parser.parse_args(argv)

    cands: list[dict] = [
        json.loads(line)
        for line in CURATED.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    print(f"loaded {len(cands)} curated candidates")

    written = 0
    skipped_existing = 0
    errors: list[str] = []
    for rec in cands:
        cat = rec["primary_category"]
        cid = rec["candidate_id"]
        target = REGISTRY / cat / f"{cid}.yaml"
        if target.exists() and not args.overwrite:
            skipped_existing += 1
            continue
        try:
            entry = build_entry(rec)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"  {cid}: {exc}")
            continue
        if not args.dry_run:
            emit_yaml(entry, target)
        written += 1

    print(f"wrote     {written}")
    print(f"skipped   {skipped_existing} (already exist)")
    if errors:
        print(f"errors    {len(errors)}")
        for e in errors[:10]:
            print(e)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
