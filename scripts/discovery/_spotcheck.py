"""Quick QA spotcheck for the curated candidate list (read-only)."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "scripts" / "discovery" / "candidates.curated.jsonl"
recs = [
    json.loads(line)
    for line in SRC.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
for cat in ["agent", "eval", "redteam", "routing", "governance", "education"]:
    total = sum(1 for r in recs if r["primary_category"] == cat)
    print(f"--- {cat} (top 8 of {total}) ---")
    cs = sorted(
        [r for r in recs if r["primary_category"] == cat],
        key=lambda r: -(r.get("stars") or 0),
    )
    for r in cs[:8]:
        desc = (r.get("description") or "")[:80]
        cid = r["candidate_id"]
        st = r["stars"]
        print(f"  {cid:35s} ({st:>6}*)  {desc}")
