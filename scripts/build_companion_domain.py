"""Emit a `create-context-graph` custom domain YAML from the atlas registry.

This is a **stub for v0.1.0**. The full v0.3.0 implementation will read
every entry in `registry/`, generate Cypher-ready node + relationship
definitions for `create-context-graph`'s domain schema, and emit
`companion/domain/open-harnesses.yaml` from real data.

For v0.1.0 the file already on disk under `companion/domain/` is a
hand-authored placeholder that describes the intended node and
relationship types but does not yet enumerate the registry. This script
is the slot for the v0.3.0 work; running it today refreshes the
``# updated_at`` line in the placeholder and returns 0.

Usage::

    python scripts/build_companion_domain.py        # touch domain timestamp
    python scripts/build_companion_domain.py --check  # exit 1 if missing
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_PATH = REPO_ROOT / "companion" / "domain" / "open-harnesses.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if the domain stub is missing.")
    args = parser.parse_args(argv)

    if not DOMAIN_PATH.exists():
        sys.stderr.write(f"missing companion domain stub: {DOMAIN_PATH}\n")
        return 1

    if args.check:
        return 0

    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = DOMAIN_PATH.read_text(encoding="utf-8")
    out_lines: list[str] = []
    touched = False
    for line in text.splitlines():
        if line.startswith("# updated_at:"):
            out_lines.append(f"# updated_at: {now}")
            touched = True
        else:
            out_lines.append(line)
    if not touched:
        out_lines.append(f"# updated_at: {now}")
    DOMAIN_PATH.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"refreshed timestamp in {DOMAIN_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
