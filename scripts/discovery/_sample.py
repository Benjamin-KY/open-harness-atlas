"""Sample every 10th curated candidate per problem category."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
recs = [
    json.loads(line)
    for line in (REPO / "scripts" / "discovery" / "candidates.curated.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
for cat in ("redteam", "governance", "routing", "agent", "eval"):
    print(f"--- {cat} (every 10th by stars) ---")
    cs = sorted([r for r in recs if r["primary_category"] == cat], key=lambda r: -(r.get("stars") or 0))
    for i, r in enumerate(cs):
        if i % 10 == 0:
            d = (r.get("description") or "")[:90]
            cid = r["candidate_id"]
            st = r["stars"]
            print(f"  {cid:30s} ({st:>5}*)  {d}")
