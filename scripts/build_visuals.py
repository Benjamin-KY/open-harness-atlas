"""Generate data-driven SVG visuals from the registry.

For v0.1.0 the two front-door visuals (``taxonomy.svg`` and
``five-component-overlay.svg``) are committed under ``visuals/`` as
hand-authored SVGs — they are reviewed for narrative correctness on every
release rather than auto-regenerated.

This script is the slot for the **v0.2.0+ data-driven visuals**
(``model-agnostic-spectrum.svg`` and ``sovereignty-radial.svg``). They are
emitted directly from the curated YAML so the visuals can never silently
drift from the registry numbers.

Usage::

    python scripts/build_visuals.py               # write visuals
    python scripts/build_visuals.py --check       # exit 1 on drift
    python scripts/build_visuals.py --skip-spectrum  # incremental
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
    "routing": "#1f3a5f",
    "education": "#7d3c98",
}
SPECTRUM_FILE = VISUALS_DIR / "model-agnostic-spectrum.svg"
HERO_FILE = VISUALS_DIR / "hero.svg"

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
    """SVG bar chart: each entry plotted as a coloured tile at its model-agnostic score."""
    rows: list[tuple[str, str, int]] = []
    for category in CATEGORY_ORDER:
        for entry in _iter_yaml(category):
            score = entry.get("model_agnostic_score")
            if isinstance(score, int) and 0 <= score <= 5:
                rows.append((entry["name"], category, score))

    if not rows:
        return _empty_svg("model-agnostic spectrum — no entries to plot")

    rows.sort(key=lambda r: (-r[2], r[1], r[0]))

    cell_height = 18
    label_width = 250
    score_axis_width = 360
    padding_top = 84
    padding_bottom = 56
    width = label_width + score_axis_width + 60
    height = padding_top + cell_height * len(rows) + padding_bottom

    parts: list[str] = []
    parts.append(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-labelledby="title desc">'
    )
    parts.append('<title id="title">Model-agnostic spectrum across the open-harness-atlas registry</title>')
    parts.append(
        '<desc id="desc">A horizontal bar chart where each open-source harness in the registry '
        'is plotted at its model-agnostic score from 0 (provider-locked) to 5 (fully portable). '
        'Colour encodes category.</desc>'
    )
    parts.append('<style>'
                 '.body{font-family:"Inter","Helvetica Neue",Arial,sans-serif;}'
                 '.title{font-size:18px;font-weight:700;fill:#1f3a5f;}'
                 '.sub{font-size:11px;font-weight:400;fill:#4a5d75;}'
                 '.axis{font-size:11px;font-weight:600;fill:#1f3a5f;text-anchor:middle;}'
                 '.row-label{font-size:11px;fill:#1f3a5f;text-anchor:end;}'
                 '.footer{font-size:10px;fill:#6b7a8c;text-anchor:middle;}'
                 '</style>')
    parts.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
    parts.append('<text x="30" y="36" class="body title">Model-agnostic spectrum</text>')
    parts.append(
        '<text x="30" y="54" class="body sub">'
        'Per-entry score 0 (provider-locked) → 5 (fully portable). '
        'Auto-generated from registry/*/*.yaml — do not hand-edit.</text>'
    )

    axis_y = padding_top - 12
    axis_x0 = label_width + 20
    axis_x5 = axis_x0 + score_axis_width
    parts.append(f'<line x1="{axis_x0}" y1="{axis_y}" x2="{axis_x5}" y2="{axis_y}" '
                 f'stroke="#1f3a5f" stroke-width="1" opacity="0.4"/>')
    for score in range(6):
        x = axis_x0 + score * (score_axis_width / 5)
        parts.append(
            f'<line x1="{x:.1f}" y1="{axis_y - 4}" x2="{x:.1f}" y2="{axis_y + 4}" '
            f'stroke="#1f3a5f" stroke-width="1"/>'
        )
        parts.append(f'<text x="{x:.1f}" y="{axis_y - 8}" class="body axis">{score}</text>')

    for i, (name, category, score) in enumerate(rows):
        y = padding_top + i * cell_height
        text_y = y + cell_height * 0.7
        parts.append(
            f'<text x="{label_width + 12}" y="{text_y:.1f}" class="body row-label">'
            f'{_xml_escape(name)} '
            f'<tspan class="sub">[{category}]</tspan></text>'
        )
        x = axis_x0
        bar_w = score * (score_axis_width / 5)
        if bar_w > 0:
            parts.append(f'<rect x="{x:.1f}" y="{y + 2}" width="{bar_w:.1f}" height="{cell_height - 6}" '
                         f'rx="3" fill="{CATEGORY_COLOUR[category]}"/>')
        else:
            parts.append(f'<rect x="{x:.1f}" y="{y + 2}" width="6" height="{cell_height - 6}" '
                         f'rx="2" fill="#c0392b"/>')

    legend_y = height - 32
    legend_x = 30
    for category in CATEGORY_ORDER:
        parts.append(f'<rect x="{legend_x}" y="{legend_y - 10}" width="14" height="14" rx="3" '
                     f'fill="{CATEGORY_COLOUR[category]}"/>')
        parts.append(f'<text x="{legend_x + 20}" y="{legend_y}" class="body sub">{category}</text>')
        legend_x += 110

    parts.append(f'<text x="{width / 2:.0f}" y="{height - 10}" class="body footer">'
                 f'CC BY-SA 4.0 — open-harness-atlas. Generated by scripts/build_visuals.py.</text>')
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

    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
