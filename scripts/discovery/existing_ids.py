"""Dump every registry entry id (one per line) into discovery/existing-ids.txt.

The candidate-discovery search uses this list as a dedupe filter so we
never propose adding a project that is already catalogued.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "registry"
OUT = REPO / "scripts" / "discovery" / "existing-ids.txt"


def main() -> int:
    ids: list[str] = []
    for path in sorted(REGISTRY.rglob("*.yaml")):
        if path.name.startswith("_"):
            continue
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict):
            eid = data.get("id")
            if isinstance(eid, str):
                ids.append(eid)

    OUT.write_text("\n".join(sorted(set(ids))) + "\n", encoding="utf-8")
    print(f"wrote {len(set(ids))} ids to {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
