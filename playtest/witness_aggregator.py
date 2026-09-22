"""Witness Log Aggregator - combines all expedition data into a witness log."""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/workspace/research/api-orchestra')

def fnv1a_64(s):
    """FNV-1a 64-bit hash."""
    FNV_OFFSET = 0xcbf29ce484222325
    FNV_PRIME = 0x100000001b3
    h = FNV_OFFSET
    for b in s.encode('utf-8'):
        h ^= b
        h = (h * FNV_PRIME) & 0xffffffffffffffff
    return h


def main():
    """Build witness log from all expedition data."""
    witness_entries = []
    
    # Source 1: Great moments (top 50)
    gm_file = Path("playtest/great_moments.json")
    if gm_file.exists():
        for moment in json.load(open(gm_file))[:50]:
            witness_entries.append({
                "source": "great_moments",
                "type": "canon_witness",
                "seed": moment["seed"],
                "score": moment["score"],
                "lore": moment["lore"],
                "rank": moment["rank"],
            })
    
    # Source 2: All-time bests from each mine
    for f in Path("playtest/gan").rglob("final.json"):
        try:
            data = json.load(open(f))
            witness_entries.append({
                "source": f"{f.parent.name}_final",
                "type": "mine_witness",
                "seed": data.get("seed"),
                "score": data.get("best_score") or data.get("score"),
                "lore": data.get("lore"),
                "path": data.get("path"),
            })
        except:
            continue
    
    # Source 3: Parallel expedition results
    for f in Path("playtest").rglob("parallel_expedition*.json"):
        try:
            data = json.load(open(f))
            if isinstance(data, list):
                for r in data[:10]:  # top 10 of each
                    witness_entries.append({
                        "source": f.name,
                        "type": "expedition_witness",
                        "seed": r["seed"],
                        "score": r.get("score"),
                        "lore": r.get("lore"),
                    })
        except:
            continue
    
    # Source 4: Negative space results
    ns_file = Path("playtest/negative_space_results.json")
    if ns_file.exists():
        data = json.load(open(ns_file))
        if isinstance(data, list):
            for r in data[:10]:  # top 10
                witness_entries.append({
                    "source": "negative_space",
                    "type": "discovery_witness",
                    "seed": r["seed"],
                    "score": r["best_score"],
                    "lore": None,  # Will fill in later
                })
    
    # Sort by source then score
    witness_entries.sort(key=lambda e: (-(e.get("score") or 0), e.get("source", "")))
    
    # Add chain hashes
    prev_hash = 0xcbf29ce484222325
    for entry in witness_entries:
        entry["prev_hash"] = f"0x{prev_hash:016x}"
        content = json.dumps({k: v for k, v in entry.items() if k not in ["prev_hash", "this_hash"]}, sort_keys=True)
        h = fnv1a_64(content)
        entry["this_hash"] = f"0x{h:016x}"
        prev_hash = h
    
    # Stats
    print(f"Total witness entries: {len(witness_entries)}")
    print(f"Sources:")
    sources = {}
    for e in witness_entries:
        s = e.get("source", "?")
        sources[s] = sources.get(s, 0) + 1
    for s, c in sources.items():
        print(f"  {s}: {c}")
    
    # Save
    out_file = Path("canon/witness_log/witness_log.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump({
            "created_at": datetime.now().isoformat(),
            "entry_count": len(witness_entries),
            "entries": witness_entries,
        }, f, indent=2)
    print(f"\nSaved to {out_file}")
    
    # Build manifest
    manifest = {
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "fnv_canary": "0x24a555471370b18d",
        "total_entries": len(witness_entries),
        "sources": list(sources.keys()),
        "min_score": min((e.get("score") or 0) for e in witness_entries if e.get("score")),
        "max_score": max((e.get("score") or 0) for e in witness_entries if e.get("score")),
    }
    
    with open(out_file.parent / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved manifest")


if __name__ == "__main__":
    main()
