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

    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
