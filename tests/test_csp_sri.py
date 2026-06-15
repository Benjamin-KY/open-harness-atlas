"""Pin Content-Security-Policy + Subresource-Integrity invariants for the viewers.

The 3D viewer (visuals/index.html) and 2D viewer (visuals/2d.html) each
load exactly one CDN-hosted JavaScript bundle. Both are pinned at a
specific version and protected with SRI (sha384) so that a future
supply-chain compromise of unpkg.com or d3js.org — even if the same
URL serves different bytes — cannot inject code into the published
Pages site. The CSP meta tag is the second layer: it constrains
script-src to only the trusted origins so an attacker can't even
inject a new <script src=...> tag pointing at an unrelated CDN.

These tests pin all four invariants (CSP exists + sane directives,
script tag has integrity, script tag has crossorigin, the SRI value
itself isn't tampered with) so any future PR that strips one of them
fails the suite rather than introducing a silent regression.

Hash verification against the live CDN payload is intentionally NOT
done here — that's a network-dependent check and would flake every
time unpkg / d3.org has a hiccup. To spot-check manually before a
version bump::

    python -c "import hashlib, base64; from urllib.request import Request, urlopen; \\
        data = urlopen(Request('<URL>', headers={'User-Agent':'Mozilla/5.0'})).read(); \\
        print('sha384-' + base64.b64encode(hashlib.sha384(data).digest()).decode())"
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "visuals" / "index.html"
TWODE_HTML = REPO_ROOT / "visuals" / "2d.html"

# Pinned versions + their expected SRI values. If a maintainer bumps a
# version they must also bump the SRI hash here in the same commit.
EXPECTED = {
    INDEX_HTML: {
        "url": "https://unpkg.com/3d-force-graph@1.73.4/dist/3d-force-graph.min.js",
        "sri": "sha384-GNPicn8pBA2/PGSyPTpxIlPurgLUYcNYJ2zskIq782dE9+gp5E32WSyuxZqA7J+u",
        "csp_origin": "https://unpkg.com",
    },
    TWODE_HTML: {
        "url": "https://d3js.org/d3.v7.min.js",
        "sri": "sha384-CjloA8y00+1SDAUkjs099PVfnY2KmDC2BZnws9kh8D/lX1s46w6EPhpXdqMfjK6i",
        "csp_origin": "https://d3js.org",
    },
}


@pytest.mark.parametrize("html_path", list(EXPECTED.keys()), ids=lambda p: p.name)
def test_csp_meta_tag_present_and_restrictive(html_path):
    html = html_path.read_text(encoding="utf-8")
    expected = EXPECTED[html_path]

    m = re.search(
        r'<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]+)"',
        html,
        re.IGNORECASE,
    )
    assert m, f"{html_path.name}: missing Content-Security-Policy meta tag"
    csp = m.group(1)

    # Defence-in-depth requires each of these explicit constraints.
    required_directives = [
        ("default-src 'self'", "default-src must be self-only"),
        (f"script-src 'self' 'unsafe-inline' {expected['csp_origin']}",
         f"script-src must allow only self + {expected['csp_origin']}"),
        ("base-uri 'none'", "base-uri must be locked to prevent base-tag hijack"),
        ("form-action 'none'", "form-action must be locked"),
        ("object-src 'none'", "object-src must be locked"),
    ]
    for directive, why in required_directives:
        assert directive in csp, (
            f"{html_path.name}: CSP missing `{directive}` ({why}). "
            f"Got: {csp!r}"
        )


@pytest.mark.parametrize("html_path", list(EXPECTED.keys()), ids=lambda p: p.name)
def test_cdn_script_tag_has_sri_and_crossorigin(html_path):
    html = html_path.read_text(encoding="utf-8")
    expected = EXPECTED[html_path]

    # Locate the script tag for the pinned CDN URL (multi-line attr layout).
    pattern = (
        r'<script\s+src="' + re.escape(expected["url"]) + r'"'
        r'\s+integrity="' + re.escape(expected["sri"]) + r'"'
        r'\s+crossorigin="anonymous"'
    )
    assert re.search(pattern, html, re.DOTALL), (
        f"{html_path.name}: pinned CDN script tag must have exact "
        f"src + integrity={expected['sri']!r} + crossorigin=\"anonymous\". "
        f"If the version was bumped, also recompute the SRI hash and update "
        f"this regression pin in the same commit."
    )


@pytest.mark.parametrize("html_path", list(EXPECTED.keys()), ids=lambda p: p.name)
def test_no_unpinned_external_scripts(html_path):
    """Block accidental introduction of any other CDN script.

    If a future PR adds a second CDN script without SRI, this test trips.
    Self-hosted relative URLs and inline scripts (which CSP allows via
    'unsafe-inline') are fine; the restriction is specifically on
    additional http(s)://… external scripts.
    """
    html = html_path.read_text(encoding="utf-8")
    expected_url = EXPECTED[html_path]["url"]
    external = re.findall(
        r'<script[^>]*\ssrc="(https?://[^"]+)"', html, re.IGNORECASE
    )
    unexpected = [u for u in external if u != expected_url]
    assert not unexpected, (
        f"{html_path.name}: unexpected external script(s) {unexpected!r}. "
        f"Only {expected_url!r} is allowed; add new ones with SRI + CSP "
        f"updates and extend the EXPECTED dict in this test."
    )
