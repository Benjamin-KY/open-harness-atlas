"""Pin the social-card (Open Graph) contract for the viewers.

Social platforms (LinkedIn, X/Twitter, Slack, Facebook, Bluesky, …) reject
SVG ``og:image`` values, so the share card must be a 1200x630 PNG and the
viewers must reference *that*, not the SVG banner. These tests guard against
a regression back to ``hero.svg`` as og:image and against the PNG losing its
1200x630 dimension contract (the size every major platform expects).

The PNG dimensions are read from the IHDR header via stdlib ``struct`` — no
image library needed — matching ``build_visuals._png_dimensions``.
"""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
VISUALS = REPO_ROOT / "visuals"
VIEWERS = [VISUALS / "index.html", VISUALS / "2d.html"]


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    head = path.read_bytes()[:24]
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", head[16:24])
    return int(width), int(height)


def test_hero_png_renders_at_1200x630(tmp_path):
    """The OG-card renderer must emit a 1200x630 PNG (the universal
    large-summary-card size). Rendered into a tmp dir so the test does not
    depend on a committed binary — hero.png is gitignored and regenerated at
    deploy (like graph.png), because matplotlib PNG bytes are not
    cross-platform deterministic."""
    import importlib
    import sys
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    build_visuals = importlib.import_module("build_visuals")
    out = tmp_path / "hero.png"
    if not build_visuals._build_hero_png(out):
        pytest.skip("matplotlib not installed — cannot render hero.png")
    assert _png_dimensions(out) == (1200, 630)


@pytest.mark.parametrize("viewer", VIEWERS, ids=lambda p: p.name)
def test_viewer_og_image_is_png_not_svg(viewer: Path):
    """og:image (and twitter:image) must point at hero.png. An SVG og:image
    renders as a blank/broken card on every major platform except Discord."""
    html = viewer.read_text(encoding="utf-8")
    png_url = "https://benjamin-ky.github.io/open-harness-atlas/hero.png"
    assert f'property="og:image" content="{png_url}"' in html, (
        f"{viewer.name}: og:image must be hero.png, not an SVG"
    )
    assert "hero.svg" not in html.split("</head>")[0], (
        f"{viewer.name}: hero.svg must not appear in the OG meta block"
    )
    assert 'name="twitter:image"' in html, f"{viewer.name}: missing twitter:image"


@pytest.mark.parametrize("viewer", VIEWERS, ids=lambda p: p.name)
def test_viewer_declares_og_image_dimensions(viewer: Path):
    """Explicit og:image:width/height help platforms render the card without
    a pre-fetch round-trip and must match the 1200x630 PNG."""
    html = viewer.read_text(encoding="utf-8")
    assert 'property="og:image:width" content="1200"' in html
    assert 'property="og:image:height" content="630"' in html
