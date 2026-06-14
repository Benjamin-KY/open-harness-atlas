"""Generate data-driven SVG visuals from the registry.

Every front-door visual is emitted from the curated registry YAML so that
no committed SVG can silently drift from the catalogue. This module owns:

* ``hero.svg`` — 1200x630 LinkedIn-social-card banner (header counts +
  six category tiles with tier-stacked bars + featured landmark names).
* ``five-component-overlay.svg`` — six-project x five-component coverage
  grid, sourced from the ``five_component_coverage`` field of each
  reference governance YAML.
* ``model-agnostic-spectrum.svg`` — distribution of the registry over the
  0-5 ``model_agnostic_score`` axis.

Usage::

    python scripts/build_visuals.py                 # write visuals
    python scripts/build_visuals.py --check         # exit 1 on drift
    python scripts/build_visuals.py --skip-hero     # incremental
    python scripts/build_visuals.py --skip-overlay  # incremental
    python scripts/build_visuals.py --skip-spectrum # incremental
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO_ROOT / "registry"
VISUALS_DIR = REPO_ROOT / "visuals"

CATEGORY_ORDER = ["governance", "agent", "eval", "redteam", "routing", "education"]
CATEGORY_COLOUR = {
    "governance": "#1f3a5f",
    "agent": "#d68910",
    "eval": "#28a745",
    "redteam": "#c0392b",
    "routing": "#3498db",
    "education": "#7d3c98",
}
SPECTRUM_FILE = VISUALS_DIR / "model-agnostic-spectrum.svg"
HERO_FILE = VISUALS_DIR / "hero.svg"
OVERLAY_FILE = VISUALS_DIR / "five-component-overlay.svg"

# ---------------------------------------------------------------------------
# Hero banner — curator-vetted landmark picks per category.
#
# Counts (total + per-tier) are read DYNAMICALLY from the live registry on
# every build so the banner can never silently drift from the catalogue.
# Featured names are an explicit curator allowlist (well-known projects
# that act as visual anchors for each cluster); these stay stable
# across pushes unless the curator updates this block.
# ---------------------------------------------------------------------------
HERO_CATEGORIES = [
    {
        "key": "governance",
        "label": "Governance harnesses",
        "icon": "🛡",
        "blurb": "Output-contract · citation · refusal · audit",
        "featured": ["Langfuse", "Guidance", "Outlines", "Instructor"],
    },
    {
        "key": "agent",
        "label": "Agent frameworks",
        "icon": "🤖",
        "blurb": "Tool-using multi-turn agent runtimes",
        "featured": ["LangChain", "Langflow", "AutoGen", "smolagents"],
    },
    {
        "key": "eval",
        "label": "Eval harnesses",
        "icon": "📏",
        "blurb": "Benchmarks · regression · LLM-as-judge",
        "featured": ["lm-evaluation-harness", "promptfoo", "DeepEval", "OpenCompass"],
    },
    {
        "key": "redteam",
        "label": "Red-team & safety",
        "icon": "🎯",
        "blurb": "Adversarial probes · jailbreak suites · agent attacks",
        "featured": ["garak", "Giskard", "PyRIT", "AgentDojo"],
    },
    {
        "key": "routing",
        "label": "Routing / model-agnostic",
        "icon": "🔀",
        "blurb": "Gateways · inference runtimes · swappable backends",
        "featured": ["vLLM", "Ollama", "LiteLLM", "llama.cpp"],
    },
    {
        "key": "education",
        "label": "Free education",
        "icon": "🎓",
        "blurb": "Courses · tutorials · cookbooks at zero cost",
        "featured": ["OpenAI Cookbook", "Prompt Engineering Guide",
                     "LLM Course", "Build an LLM From Scratch"],
    },
]
TIER_ORDER = ["landmark", "established", "emerging", "frontier", "unknown"]
TIER_COLOUR = {
    "landmark": "#1f3a5f",
    "established": "#4a6fa5",
    "emerging": "#8aa6c8",
    "frontier": "#c8d3e0",
    "unknown": "#e8ecf0",
}


def _iter_yaml(category: str) -> Iterable[dict]:
    folder = REGISTRY_DIR / category
    if not folder.is_dir():
        return
    for path in sorted(folder.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict):
            yield data


def _build_spectrum() -> str:
    """SVG distribution chart: macro stacked histogram + per-category small-multiples.

    Reports the registry's distribution across model_agnostic_score (0..5).
    Top panel = combined stacked histogram, bars at each score, segments
    coloured by category. Bottom panel = a 2x3 grid of per-category mini
    histograms so the reader can compare each category's posture.

    Replaces the old vertical-line-of-816-bars layout which was readable
    only as a wall of colour, not as a distribution.
    """
    import collections

    SCORES = list(range(6))
    counts: dict[tuple[str, int], int] = collections.Counter()
    for category in CATEGORY_ORDER:
        for entry in _iter_yaml(category):
            score = entry.get("model_agnostic_score")
            if isinstance(score, int) and 0 <= score <= 5:
                counts[(category, score)] += 1

    if not counts:
        return _empty_svg("model-agnostic spectrum — no entries to plot")

    total_by_score = {s: sum(counts.get((c, s), 0) for c in CATEGORY_ORDER) for s in SCORES}
    total_by_cat = {c: sum(counts.get((c, s), 0) for s in SCORES) for c in CATEGORY_ORDER}
    grand_total = sum(total_by_score.values())
    macro_max = max(total_by_score.values()) if total_by_score else 1

    W, H = 1200, 720
    parts: list[str] = []
    parts.append(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="title desc">'
    )
    parts.append(
        '<title id="title">Model-agnostic spectrum across the open-harness-atlas registry</title>'
    )
    parts.append(
        '<desc id="desc">A stacked histogram showing how '
        f'{grand_total} open-source harnesses distribute across the model_agnostic_score axis '
        '(0 = provider-locked through 5 = fully portable), with a six-category small-multiples grid '
        'below comparing each category\'s distribution.</desc>'
    )
    parts.append(
        '<style>'
        '.body{font-family:"Inter","Helvetica Neue",Arial,sans-serif;}'
        '.title{font-size:20px;font-weight:700;fill:#1f3a5f;}'
        '.sub{font-size:12px;font-weight:400;fill:#4a5d75;}'
        '.h2{font-size:13px;font-weight:600;fill:#1f3a5f;}'
        '.axis{font-size:11px;fill:#4a5d75;}'
        '.axis-bold{font-size:11px;font-weight:600;fill:#1f3a5f;text-anchor:middle;}'
        '.bar-total{font-size:11px;font-weight:700;fill:#1f3a5f;text-anchor:middle;}'
        '.seg-label{font-size:10px;font-weight:600;fill:#ffffff;text-anchor:middle;}'
        '.mini-title{font-size:11px;font-weight:600;fill:#1f3a5f;}'
        '.mini-count{font-size:10px;fill:#6b7a8c;}'
        '.mini-axis{font-size:9px;fill:#6b7a8c;text-anchor:middle;}'
        '.mini-bar-label{font-size:9px;font-weight:600;fill:#1f3a5f;text-anchor:middle;}'
        '.legend-text{font-size:11px;fill:#1f3a5f;}'
        '.footer{font-size:10px;fill:#6b7a8c;text-anchor:middle;}'
        '</style>'
    )
    parts.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

    parts.append('<text x="40" y="38" class="body title">Model-agnostic spectrum</text>')
    parts.append(
        f'<text x="40" y="58" class="body sub">'
        f'{grand_total} open-source harnesses scored 0 (provider-locked) through 5 (fully portable). '
        'Auto-generated from registry/*/*.yaml. '
        'Conservative defaults (3) reflect entries pending manual review.'
        '</text>'
    )

    px_left, px_right, py_top, py_bot = 140, 1160, 110, 330
    plot_w = px_right - px_left
    plot_h = py_bot - py_top
    bar_w = 100
    slot_w = plot_w / 6
    y_max = ((macro_max // 100) + 1) * 100

    for tick in range(0, y_max + 1, 100):
        ty = py_bot - (tick / y_max) * plot_h
        parts.append(
            f'<line x1="{px_left}" y1="{ty:.1f}" x2="{px_right}" y2="{ty:.1f}" '
            f'stroke="#e6e9ee" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{px_left - 10}" y="{ty + 4:.1f}" class="body axis" text-anchor="end">{tick}</text>'
        )

    parts.append(
        f'<text x="{px_left - 50}" y="{py_top + plot_h / 2:.1f}" class="body sub" '
        f'transform="rotate(-90 {px_left - 50},{py_top + plot_h / 2:.1f})" '
        f'text-anchor="middle">entries</text>'
    )

    for s in SCORES:
        bx = px_left + s * slot_w + (slot_w - bar_w) / 2
        running_y = py_bot
        for cat in CATEGORY_ORDER:
            n = counts.get((cat, s), 0)
            if n == 0:
                continue
            seg_h = (n / y_max) * plot_h
            running_y -= seg_h
            parts.append(
                f'<rect x="{bx:.1f}" y="{running_y:.1f}" width="{bar_w}" height="{seg_h:.2f}" '
                f'fill="{CATEGORY_COLOUR[cat]}"/>'
            )
            if seg_h >= 18:
                parts.append(
                    f'<text x="{bx + bar_w / 2:.1f}" y="{running_y + seg_h / 2 + 4:.1f}" '
                    f'class="body seg-label">{n}</text>'
                )

        total = total_by_score[s]
        if total > 0:
            top_y = py_bot - (total / y_max) * plot_h
            parts.append(
                f'<text x="{bx + bar_w / 2:.1f}" y="{top_y - 6:.1f}" class="body bar-total">{total}</text>'
            )
        parts.append(
            f'<text x="{bx + bar_w / 2:.1f}" y="{py_bot + 18:.1f}" class="body axis-bold">{s}</text>'
        )

    score_descriptors = {
        0: "locked",
        1: "single primary",
        2: "multi-API",
        3: "+ local opt",
        4: "swap by config",
        5: "config-only",
    }
    for s in SCORES:
        bx = px_left + s * slot_w + slot_w / 2
        parts.append(
            f'<text x="{bx:.1f}" y="{py_bot + 32:.1f}" class="body axis" text-anchor="middle">'
            f'{score_descriptors[s]}</text>'
        )

    parts.append(
        '<text x="40" y="380" class="body h2">Per-category distribution '
        '<tspan class="sub">(each chart\'s y-axis is independently scaled '
        '\u2014 read shape, not height)</tspan></text>'
    )

    grid_cols = 3
    cell_w = 360
    cell_h = 130
    cell_gap_x = 20
    cell_gap_y = 30
    grid_left = 40
    grid_top = 400
    mini_bar_w = 36
    mini_plot_h = 76
    mini_plot_top_pad = 28

    for idx, cat in enumerate(CATEGORY_ORDER):
        row = idx // grid_cols
        col = idx % grid_cols
        cx = grid_left + col * (cell_w + cell_gap_x)
        cy = grid_top + row * (cell_h + cell_gap_y)

        cat_total = total_by_cat[cat]
        cat_max = max((counts.get((cat, s), 0) for s in SCORES), default=1) or 1

        parts.append(
            f'<rect x="{cx}" y="{cy}" width="{cell_w}" height="{cell_h}" rx="6" '
            f'fill="#f7f9fc" stroke="#e6e9ee" stroke-width="1"/>'
        )
        parts.append(
            f'<rect x="{cx}" y="{cy}" width="6" height="{cell_h}" rx="3" '
            f'fill="{CATEGORY_COLOUR[cat]}"/>'
        )
        parts.append(
            f'<text x="{cx + 16}" y="{cy + 18}" class="body mini-title">{cat}</text>'
        )
        parts.append(
            f'<text x="{cx + cell_w - 12}" y="{cy + 18}" class="body mini-count" '
            f'text-anchor="end">{cat_total} entries</text>'
        )

        mini_left = cx + 24
        mini_right = cx + cell_w - 16
        mini_plot_w = mini_right - mini_left
        mini_slot = mini_plot_w / 6
        mini_bottom = cy + mini_plot_top_pad + mini_plot_h

        for s in SCORES:
            n = counts.get((cat, s), 0)
            bx = mini_left + s * mini_slot + (mini_slot - mini_bar_w) / 2
            if n > 0:
                bh = (n / cat_max) * mini_plot_h
                parts.append(
                    f'<rect x="{bx:.1f}" y="{mini_bottom - bh:.2f}" width="{mini_bar_w}" '
                    f'height="{bh:.2f}" rx="2" fill="{CATEGORY_COLOUR[cat]}" opacity="0.85"/>'
                )
                parts.append(
                    f'<text x="{bx + mini_bar_w / 2:.1f}" y="{mini_bottom - bh - 4:.1f}" '
                    f'class="body mini-bar-label">{n}</text>'
                )
            else:
                parts.append(
                    f'<line x1="{bx:.1f}" y1="{mini_bottom - 1}" x2="{bx + mini_bar_w:.1f}" '
                    f'y2="{mini_bottom - 1}" stroke="#cfd6df" stroke-width="2"/>'
                )
            parts.append(
                f'<text x="{bx + mini_bar_w / 2:.1f}" y="{mini_bottom + 12:.1f}" '
                f'class="body mini-axis">{s}</text>'
            )

    parts.append(
        f'<text x="{W / 2:.0f}" y="{H - 16}" class="body footer">'
        f'CC BY-SA 4.0 \u2014 open-harness-atlas \u00b7 '
        f'generated by scripts/build_visuals.py::_build_spectrum'
        f'</text>'
    )

    parts.append('</svg>\n')
    return "\n".join(parts)


def _category_data() -> dict[str, dict]:
    """Walk registry → per-category total + tier breakdown.

    Tier is read from ``registry/_metadata/_tiers.json`` (a single
    ``{id: tier}`` map written by ``compute_tier.py``).
    """
    import json
    tier_path = REGISTRY_DIR / "_metadata" / "_tiers.json"
    tier_by_id: dict[str, str] = {}
    if tier_path.exists():
        try:
            tier_by_id = json.loads(tier_path.read_text(encoding="utf-8"))
        except Exception:
            tier_by_id = {}
    out: dict[str, dict] = {}
    for cat in CATEGORY_ORDER:
        entries = list(_iter_yaml(cat))
        tier_counts: dict[str, int] = dict.fromkeys(TIER_ORDER, 0)
        for entry in entries:
            tier = tier_by_id.get(entry["id"]) or "unknown"
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        out[cat] = {"total": len(entries), "tiers": tier_counts}
    return out


def _build_hero() -> str:
    """Build the LinkedIn/README banner — clean tier infographic.

    1200x630 (LinkedIn social-card preview ratio). Six category tiles
    arranged 3x2; per tile: icon, label, total, horizontal tier-stacked
    bar, four curator-vetted landmark names. Total at top, project URL +
    tier legend at bottom. White background. Targets <50KB.
    """
    data = _category_data()
    grand_total = sum(d["total"] for d in data.values())

    W, H = 1200, 630
    PAD = 32
    HEADER_H = 96
    FOOTER_H = 64
    GRID_TOP = PAD + HEADER_H
    GRID_BOTTOM = H - PAD - FOOTER_H
    COLS, ROWS = 3, 2
    GAP = 18
    TILE_W = (W - PAD * 2 - GAP * (COLS - 1)) / COLS
    TILE_H = (GRID_BOTTOM - GRID_TOP - GAP * (ROWS - 1)) / ROWS

    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-labelledby="hero-title hero-desc">'
    )
    parts.append('<title id="hero-title">open-harness-atlas — '
                 f'{grand_total} OSS harnesses across six categories</title>')
    parts.append('<desc id="hero-desc">Six labelled category tiles showing '
                 'total entries and tier breakdown (landmark, established, '
                 'emerging, frontier) with four representative projects per '
                 'category.</desc>')

    parts.append(
        '<style>'
        '.bg{fill:#ffffff}'
        '.brand{fill:#1f3a5f;font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.muted{fill:#555;font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.tile{fill:#fafbfd;stroke:#e2e7ee;stroke-width:1.2}'
        '.tile-label{font-size:18px;font-weight:700;fill:#1f3a5f;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.tile-blurb{font-size:11px;fill:#6b7a8c;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.tile-count{font-size:36px;font-weight:800;fill:#1f3a5f;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.tile-count-label{font-size:11px;fill:#6b7a8c;letter-spacing:0.06em;'
        'text-transform:uppercase;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.featured{font-size:12px;fill:#222;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.title{font-size:34px;font-weight:800;fill:#1f3a5f;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.tag{font-size:14px;fill:#4a5d75;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.total{font-size:13px;font-weight:600;fill:#1f3a5f;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '.url{font-size:12px;fill:#4a5d75;'
        'font-family:"JetBrains Mono",Consolas,monospace}'
        '.legend{font-size:11px;fill:#555;'
        'font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
        '</style>'
    )
    parts.append(f'<rect class="bg" width="{W}" height="{H}"/>')

    # Header
    parts.append(f'<text class="title" x="{PAD}" y="{PAD + 36}">'
                 'open-harness-atlas</text>')
    parts.append(f'<text class="tag" x="{PAD}" y="{PAD + 62}">'
                 'The OSS layer that makes model-agnostic AI workloads possible — '
                 f'{grand_total} curated, OSI-licensed harnesses + free education.</text>')
    parts.append(f'<text class="tag" x="{PAD}" y="{PAD + 84}" fill="#7a8a9e">'
                 'Live 3D knowledge graph · 6 categories · tier overlay · '
                 'entry-point lenses · supply chains.</text>')

    # Tiles
    for idx, cat in enumerate(HERO_CATEGORIES):
        row, col = divmod(idx, COLS)
        x = PAD + col * (TILE_W + GAP)
        y = GRID_TOP + row * (TILE_H + GAP)
        cat_data = data[cat["key"]]
        total = cat_data["total"]
        tiers = cat_data["tiers"]

        parts.append(
            f'<rect class="tile" x="{x:.1f}" y="{y:.1f}" '
            f'width="{TILE_W:.1f}" height="{TILE_H:.1f}" rx="10"/>'
        )

        # Header: icon + label, count on the right
        parts.append(
            f'<text x="{x + 18:.1f}" y="{y + 30:.1f}" '
            f'class="tile-label"><tspan style="font-size:18px">'
            f'{_xml_escape(cat["icon"])}</tspan>'
            f'<tspan dx="10">{_xml_escape(cat["label"])}</tspan></text>'
        )
        parts.append(
            f'<text x="{x + 18:.1f}" y="{y + 48:.1f}" class="tile-blurb">'
            f'{_xml_escape(cat["blurb"])}</text>'
        )
        parts.append(
            f'<text x="{x + TILE_W - 18:.1f}" y="{y + 36:.1f}" '
            f'class="tile-count" text-anchor="end">{total}</text>'
        )
        parts.append(
            f'<text x="{x + TILE_W - 18:.1f}" y="{y + 52:.1f}" '
            f'class="tile-count-label" text-anchor="end">entries</text>'
        )

        # Tier-stacked horizontal bar
        bar_x = x + 18
        bar_y = y + 68
        bar_w = TILE_W - 36
        bar_h = 8
        if total > 0:
            cursor = 0.0
            for tier in TIER_ORDER:
                n = tiers.get(tier, 0)
                if n == 0:
                    continue
                seg_w = bar_w * n / total
                parts.append(
                    f'<rect x="{bar_x + cursor:.1f}" y="{bar_y}" '
                    f'width="{seg_w:.1f}" height="{bar_h}" rx="2" '
                    f'fill="{TIER_COLOUR[tier]}"/>'
                )
                cursor += seg_w
        else:
            parts.append(
                f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w:.1f}" '
                f'height="{bar_h}" rx="2" fill="#e8ecf0"/>'
            )

        # Tier-count micro-legend under bar (just numbers)
        landmark_n = tiers.get("landmark", 0)
        established_n = tiers.get("established", 0)
        emerging_n = tiers.get("emerging", 0)
        frontier_n = tiers.get("frontier", 0)
        parts.append(
            f'<text x="{bar_x}" y="{bar_y + 24}" class="tile-blurb">'
            f'<tspan fill="{TIER_COLOUR["landmark"]}" font-weight="700">'
            f'{landmark_n}</tspan> landmark · '
            f'<tspan fill="{TIER_COLOUR["established"]}" font-weight="700">'
            f'{established_n}</tspan> established · '
            f'<tspan fill="{TIER_COLOUR["emerging"]}" font-weight="700">'
            f'{emerging_n}</tspan> emerging · '
            f'<tspan fill="{TIER_COLOUR["frontier"]}" font-weight="700">'
            f'{frontier_n}</tspan> frontier</text>'
        )

        # Four featured landmark names
        featured = cat.get("featured", [])[:4]
        feat_y_start = y + TILE_H - 18 - (len(featured) - 1) * 16
        for i, name in enumerate(featured):
            parts.append(
                f'<text x="{x + 18:.1f}" y="{feat_y_start + i * 16:.1f}" '
                f'class="featured">› {_xml_escape(name)}</text>'
            )

    # Footer: URL + legend
    footer_y = H - PAD - 12
    parts.append(
        f'<text class="url" x="{PAD}" y="{footer_y}">'
        'github.com/Benjamin-KY/open-harness-atlas  ·  '
        'benjamin-ky.github.io/open-harness-atlas</text>'
    )
    parts.append(
        f'<text class="legend" x="{W - PAD}" y="{footer_y}" text-anchor="end">'
        'Tier = stars + age + commit recency · ‹ darker = more adopted ›</text>'
    )

    parts.append('</svg>\n')
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Five-component overlay — auto-built from the six reference governance YAMLs.
#
# Replaces the old hand-authored visuals/five-component-overlay.svg which
# drifted from the YAML truth (e.g. guardrails-ai.policy_router was rendered
# as "partial" while the YAML says "none"). Now the SVG is one rebuild away
# from the underlying registry data and cannot silently disagree with it.
# ---------------------------------------------------------------------------
OVERLAY_PROJECTS = [
    "guardrails-ai",
    "nemo-guardrails",
    "presidio",
    "granite-guardian",
    "rebuff",
    "harmless-harnesses",
]
OVERLAY_COMPONENTS = [
    ("policy_router", "policy router"),
    ("source_authority", "source authority"),
    ("prompt_composer", "prompt composer"),
    ("output_contract", "output contract"),
    ("audit_log_fsm", "audit-log FSM"),
]
OVERLAY_LEVELS = ["native", "aligned", "partial", "none"]
OVERLAY_FILL = {
    "native":  "#28a745",
    "aligned": "#4a6fa5",
    "partial": "#d68910",
    "none":    "#e6e9ee",
}
OVERLAY_TEXT = {
    "native":  "#ffffff",
    "aligned": "#ffffff",
    "partial": "#ffffff",
    "none":    "#6b7a8c",
}
OVERLAY_BLURB = {
    "native":  "component is the project's core abstraction",
    "aligned": "project implements the component substantively",
    "partial": "project covers the component for a narrow case only",
    "none":    "component is out of scope for this project",
}


def _overlay_data() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for pid in OVERLAY_PROJECTS:
        path = REGISTRY_DIR / "governance" / f"{pid}.yaml"
        coverage = {k: "none" for k, _ in OVERLAY_COMPONENTS}
        if path.exists():
            with path.open(encoding="utf-8") as fh:
                doc = yaml.safe_load(fh) or {}
            fcc = doc.get("five_component_coverage") or {}
            for ck, _ in OVERLAY_COMPONENTS:
                val = fcc.get(ck, "none")
                if val not in OVERLAY_LEVELS:
                    val = "none"
                coverage[ck] = val
        out[pid] = coverage
    return out


def _build_overlay() -> str:
    data = _overlay_data()

    W, H = 1200, 720
    PAD = 36
    HEADER_BOTTOM = 96
    COL_HEADER_Y = HEADER_BOTTOM + 28
    GRID_TOP = COL_HEADER_Y + 28
    LEGEND_TOP = H - 130
    FOOTER_Y = H - 16
    LABEL_COL_W = 188
    GRID_LEFT = PAD + LABEL_COL_W
    GRID_RIGHT = W - PAD
    GRID_W = GRID_RIGHT - GRID_LEFT
    GRID_BOTTOM = LEGEND_TOP - 24
    GRID_H = GRID_BOTTOM - GRID_TOP
    n_cols = len(OVERLAY_PROJECTS)
    n_rows = len(OVERLAY_COMPONENTS)
    cell_w = GRID_W / n_cols
    cell_h = GRID_H / n_rows
    cell_gap = 8

    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        'role="img" aria-labelledby="ovTitle ovDesc">'
    )
    parts.append(
        '<title id="ovTitle">Five-component coverage — which OSS governance '
        'harnesses cover which Harmless Harnesses components</title>'
    )
    parts.append(
        '<desc id="ovDesc">A 5-row by 6-column matrix mapping the five Harmless '
        'Harnesses components (policy router, source authority, prompt composer, '
        'output contract, audit-log FSM) to six representative open-source '
        'governance projects (guardrails-ai, nemo-guardrails, presidio, '
        'granite-guardian, rebuff, harmless-harnesses). Each cell is one of '
        'native, aligned, partial, or none — colour-coded and labelled.</desc>'
    )
    parts.append('<style>')
    parts.append(
        '.body { font-family: "Inter", "Helvetica Neue", Arial, sans-serif; }'
    )
    parts.append('.h1 { font-size: 26px; font-weight: 700; fill: #1f3a5f; }')
    parts.append('.h2 { font-size: 13px; font-weight: 400; fill: #4a5d75; }')
    parts.append(
        '.col-header { font-size: 14px; font-weight: 600; fill: #1f3a5f; '
        'text-anchor: middle; }'
    )
    parts.append(
        '.col-sub { font-size: 10px; font-weight: 400; fill: #6b7a8c; '
        'text-anchor: middle; font-style: italic; }'
    )
    parts.append(
        '.row-label { font-size: 14px; font-weight: 600; fill: #1f3a5f; '
        'text-anchor: end; }'
    )
    parts.append(
        '.cell-label { font-size: 13px; font-weight: 700; text-anchor: middle; }'
    )
    parts.append(
        '.legend-blurb { font-size: 12px; font-weight: 500; fill: #1f3a5f; }'
    )
    parts.append(
        '.footer { font-size: 11px; fill: #6b7a8c; text-anchor: middle; }'
    )
    parts.append('</style>')

    parts.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

    # Header block
    parts.append(
        f'<text x="{PAD}" y="42" class="body h1">Five-component coverage</text>'
    )
    parts.append(
        f'<text x="{PAD}" y="68" class="body h2">'
        'Which open-source governance harnesses cover which Harmless Harnesses '
        'components. Capability axis only — not a ranking.</text>'
    )
    parts.append(
        f'<text x="{PAD}" y="86" class="body h2">'
        'Cells are auto-generated from '
        '<tspan font-family="ui-monospace, SFMono-Regular, Menlo, monospace" '
        'fill="#1f3a5f">registry/governance/*.yaml</tspan> '
        '· five_component_coverage fields.</text>'
    )

    # Column headers
    for ci, pid in enumerate(OVERLAY_PROJECTS):
        cx = GRID_LEFT + ci * cell_w + cell_w / 2
        parts.append(
            f'<text x="{cx:.1f}" y="{COL_HEADER_Y}" class="body col-header">'
            f'{_xml_escape(pid)}</text>'
        )
        if pid == "harmless-harnesses":
            parts.append(
                f'<text x="{cx:.1f}" y="{COL_HEADER_Y + 14}" class="body col-sub">'
                'reference impl — COI noted</text>'
            )

    # Grid cells + row labels
    for ri, (ckey, clabel) in enumerate(OVERLAY_COMPONENTS):
        row_centre_y = GRID_TOP + ri * cell_h + cell_h / 2
        parts.append(
            f'<text x="{GRID_LEFT - 16:.1f}" y="{row_centre_y + 5:.1f}" '
            f'class="body row-label">{_xml_escape(clabel)}</text>'
        )
        for ci, pid in enumerate(OVERLAY_PROJECTS):
            cx = GRID_LEFT + ci * cell_w + cell_gap / 2
            cy = GRID_TOP + ri * cell_h + cell_gap / 2
            cw = cell_w - cell_gap
            ch = cell_h - cell_gap
            level = data[pid].get(ckey, "none")
            fill = OVERLAY_FILL[level]
            text_fill = OVERLAY_TEXT[level]
            parts.append(
                f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" '
                f'height="{ch:.1f}" rx="10" fill="{fill}"/>'
            )
            parts.append(
                f'<text x="{cx + cw / 2:.1f}" y="{cy + ch / 2 + 5:.1f}" '
                f'class="body cell-label" fill="{text_fill}">{level}</text>'
            )

    # Legend — 2x2 grid beneath the data grid; each cell = chip + blurb.
    # Avoid using .row-label class (its CSS text-anchor:end clips left-aligned
    # text) — set anchor with `style=` so it beats the class selector.
    parts.append(
        f'<text x="{PAD}" y="{LEGEND_TOP + 16}" class="body" '
        'style="font-size:14px;font-weight:600;fill:#1f3a5f;text-anchor:start">'
        'Coverage legend</text>'
    )
    col_w = (W - 2 * PAD) / 2
    row_h = 36
    chip_w, chip_h = 76, 26
    for i, level in enumerate(OVERLAY_LEVELS):
        col = i % 2
        row = i // 2
        cx = PAD + col * col_w
        cy = LEGEND_TOP + 40 + row * row_h
        fill = OVERLAY_FILL[level]
        text_fill = OVERLAY_TEXT[level]
        parts.append(
            f'<rect x="{cx:.1f}" y="{cy - 18}" width="{chip_w}" '
            f'height="{chip_h}" rx="6" fill="{fill}"/>'
        )
        parts.append(
            f'<text x="{cx + chip_w / 2:.1f}" y="{cy - 1}" '
            f'class="body cell-label" fill="{text_fill}">{level}</text>'
        )
        parts.append(
            f'<text x="{cx + chip_w + 12:.1f}" y="{cy - 1}" '
            f'class="body legend-blurb">{_xml_escape(OVERLAY_BLURB[level])}</text>'
        )

    parts.append(
        f'<text x="{W / 2:.1f}" y="{FOOTER_Y}" class="body footer">'
        'CC BY-SA 4.0 — open-harness-atlas · '
        'auto-generated from registry/governance/*.yaml five_component_coverage'
        '</text>'
    )

    parts.append('</svg>\n')
    return "\n".join(parts)


def _empty_svg(message: str) -> str:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 80" role="img">'
        f'<title>{_xml_escape(message)}</title>'
        f'<rect width="600" height="80" fill="#ffffff"/>'
        f'<text x="300" y="46" text-anchor="middle" font-family="Inter, sans-serif" '
        f'font-size="13" fill="#1f3a5f">{_xml_escape(message)}</text>'
        f'</svg>\n'
    )


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any data-driven SVG on disk differs from rendered output.",
    )
    parser.add_argument("--skip-spectrum", action="store_true",
                        help="Do not rebuild model-agnostic-spectrum.svg.")
    parser.add_argument("--skip-hero", action="store_true",
                        help="Do not rebuild hero.svg.")
    parser.add_argument("--skip-overlay", action="store_true",
                        help="Do not rebuild five-component-overlay.svg.")
    args = parser.parse_args(argv)

    VISUALS_DIR.mkdir(parents=True, exist_ok=True)
    drift = False

    if not args.skip_spectrum:
        rendered = _build_spectrum()
        if args.check:
            existing = SPECTRUM_FILE.read_text(encoding="utf-8") if SPECTRUM_FILE.exists() else ""
            if existing != rendered:
                sys.stderr.write(f"DRIFT: {SPECTRUM_FILE.relative_to(REPO_ROOT)}\n")
                drift = True
        else:
            SPECTRUM_FILE.write_text(rendered, encoding="utf-8")
            print(f"wrote {SPECTRUM_FILE.relative_to(REPO_ROOT)}")

    if not args.skip_hero:
        rendered = _build_hero()
        if args.check:
            existing = HERO_FILE.read_text(encoding="utf-8") if HERO_FILE.exists() else ""
            if existing != rendered:
                sys.stderr.write(f"DRIFT: {HERO_FILE.relative_to(REPO_ROOT)}\n")
                drift = True
        else:
            HERO_FILE.write_text(rendered, encoding="utf-8")
            print(f"wrote {HERO_FILE.relative_to(REPO_ROOT)}")

    if not args.skip_overlay:
        rendered = _build_overlay()
        if args.check:
            existing = OVERLAY_FILE.read_text(encoding="utf-8") if OVERLAY_FILE.exists() else ""
            if existing != rendered:
                sys.stderr.write(f"DRIFT: {OVERLAY_FILE.relative_to(REPO_ROOT)}\n")
                drift = True
        else:
            OVERLAY_FILE.write_text(rendered, encoding="utf-8")
            print(f"wrote {OVERLAY_FILE.relative_to(REPO_ROOT)}")

    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
