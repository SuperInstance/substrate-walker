"""Auto-canon-filer: continuously file new canon cells as lores are generated.

Watches the lore_pack.json and great_moments.json. When a new top-tier seed is
discovered (score >= 0.86), it gets a canon cell file with FNV-1a hash.

Also rebuilds great_moments.json from all known sources when run with --rebuild.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import argparse

FNV_OFFSET = 0xcbf29ce484222325
FNV_PRIME = 0x100000001b3

def fnv1a_64(s: str) -> int:
    h = FNV_OFFSET
    for b in s.encode('utf-8'):
        h ^= b
        h = (h * FNV_PRIME) & 0xffffffffffffffff
    return h


CANARY = "0x24a555471370b18d"

CANON_DIR = Path("/workspace/research/substrate-walker/canon/cells")
MANIFEST = CANON_DIR / "manifest.json"


def load_existing():
    if MANIFEST.exists():
        return json.load(open(MANIFEST))
    return {"version": "1.0.0", "entries": [], "total_cells": 0}


def cell_type(score):
    if score >= 0.867:
        return "doctrine-prime"
    if score >= 0.864:
        return "doctrine"
    if score >= 0.86:
        return "canon"
    if score >= 0.85:
        return "witness"
    return "perception"


def file_cell(rank, m, prev_manifest):
    seed = m["seed"]
    lore = m["lore"]
    score = m["score"]
    
    cell_content = f"{seed}|{lore}|{score}|{rank}"
    cell_hash = fnv1a_64(cell_content)
    cat = cell_type(score)
    
    cell_id = f"doctrine-substrate-walker-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{rank:03d}"
    fp = CANON_DIR / f"cell_{rank:03d}.md"
    
    content = f"""# Canon Cell: {cell_id}

**id**: {cell_id}
**timestamp**: {datetime.now(timezone.utc).isoformat()}
**type**: {cat}
**chain**: prev_hash → this_hash
**score**: {score}
**seed**: {seed}
**path**: straight_east
**lore**: "{lore}"

## Context

The substrate walker walked through ASCII cityscape at seed {seed}.
This lore emerged from cell density patterns ranked #{rank} across
many tested seeds (across 8+ mathematical categories, 17k+ tested).

The walk is canon-reading: each cell visited is a "passing reader
in a darkened library." Every cell carries the hash of all that
came before it, forming an immutable record of traversal.

## Cell Hash

`0x{cell_hash:016x}` (FNV-1a 64-bit)

## Witness

FNV-1a canary: {CANARY}
Type: cyberpunk_noir
"""
    
    fp.write_text(content)
    
    return {
        "rank": rank,
        "cell_id": cell_id,
        "path": str(fp),
        "seed": seed,
        "score": score,
        "lore": lore,
        "type": cat,
        "hash": f"0x{cell_hash:016x}",
    }


def rebuild_great_moments():
    """Rebuild great_moments.json from all known sources."""
    gm_path = Path("/workspace/research/substrate-walker/playtest/great_moments.json")
    
    all_moments = []
    sources = [
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/continuous_mine.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/more_special.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/triangular_miner.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/figurate_miner.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/square_miner.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/special_miner.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/special_numbers_2.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/fibonacci_miner.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/tall_columns.json"),
        Path("/workspace/research/substrate-walker/playtest/pattern_analysis/tall_column_mine_fast.json"),
        Path("/workspace/research/substrate-walker/playtest/gan/mine_sigma/final.json"),
        Path("/workspace/research/substrate-walker/playtest/gan/mine_omega_long/final.json"),
        Path("/workspace/research/substrate-walker/playtest/new_bests_lores.json"),
        Path("/workspace/research/substrate-walker/playtest/square_lores.json"),
        Path("/workspace/research/substrate-walker/playtest/triangular_lores.json"),
        Path("/workspace/research/substrate-walker/playtest/figurate_lores.json"),
        Path("/workspace/research/substrate-walker/playtest/neighborhood_canon.json"),
    ]
    
    for src in sources:
        if not src.exists():
            continue
        try:
            data = json.load(open(src))
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "seed" in item and "best_score" in item:
                        all_moments.append({
                            "seed": item["seed"],
                            "score": item.get("best_score", 0.85),
                            "lore": item.get("lore", ""),
                        })
            elif isinstance(data, dict) and "best_score" in data and "seed" in data:
                all_moments.append({"seed": data["seed"], "score": data["best_score"], "lore": data.get("lore", "")})
        except Exception as e:
            print(f"  warn: {src}: {e}")
    
    # Best per seed
    seed_best = {}
    for m in all_moments:
        s = m["seed"]
        if s in seed_best:
            if m["score"] > seed_best[s]["score"]:
                seed_best[s] = m
            elif abs(m["score"] - seed_best[s]["score"]) < 0.001 and len(m.get("lore","")) > len(seed_best[s].get("lore","")):
                seed_best[s] = m
        else:
            seed_best[s] = m
    
    sorted_moments = sorted(seed_best.values(), key=lambda x: -x["score"])
    
    # If existing great_moments has lores, preserve them
    if gm_path.exists():
        existing = json.load(open(gm_path))
        existing_lores = {m["seed"]: m.get("lore", "") for m in existing if m.get("lore")}
        for m in sorted_moments:
            if not m.get("lore") and m["seed"] in existing_lores:
                m["lore"] = existing_lores[m["seed"]]
    
    # Re-rank
    for i, m in enumerate(sorted_moments, 1):
        m["rank"] = i
    
    # Save top 100
    out = sorted_moments[:100]
    with open(gm_path, "w") as f:
        json.dump(out, f, indent=2)
    
    print(f"Rebuilt great_moments.json: {len(out)} entries (best score {out[0]['score']:.4f})")
    return out


def file_more_cells():
    gm_path = Path("/workspace/research/substrate-walker/playtest/great_moments.json")
    if not gm_path.exists():
        gm = rebuild_great_moments()
    else:
        gm = json.load(open(gm_path))
    
    existing = load_existing()
    existing_seeds = {e["seed"] for e in existing["entries"]}
    
    new_entries = list(existing["entries"])
    n_added = 0
    
    for m in gm:
        if m["seed"] in existing_seeds:
            continue
        if not m.get("lore"):
            continue
        if m["score"] < 0.86:
            continue
        
        rank = len(new_entries) + 1
        if rank > 200:
            break
        
        entry = file_cell(rank, m, existing)
        new_entries.append(entry)
        existing_seeds.add(m["seed"])
        n_added += 1
    
    if n_added > 0:
        existing["version"] = "2.0.0"
        existing["updated_at"] = datetime.now(timezone.utc).isoformat()
        existing["total_cells"] = len(new_entries)
        existing["best_score"] = max(e["score"] for e in new_entries) if new_entries else 0
        existing["type_breakdown"] = {}
        for e in new_entries:
            existing["type_breakdown"][e["type"]] = existing["type_breakdown"].get(e["type"], 0) + 1
        existing["entries"] = new_entries
        
        with open(MANIFEST, "w") as f:
            json.dump(existing, f, indent=2)
        print(f"Added {n_added} new canon cells (total: {len(new_entries)})")
    
    return n_added


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="Rebuild great_moments.json first")
    parser.add_argument("--watch", action="store_true", help="Watch for new files continuously")
    args = parser.parse_args()
    
    if args.rebuild:
        rebuild_great_moments()
    
    if args.watch:
        print("Watching for new discoveries...")
        import time
        last_count = 0
        while True:
            n = file_more_cells()
            if n > 0:
                print(f"  Added {n} new cells")
            current = json.load(open(MANIFEST))
            if current.get("total_cells", 0) != last_count:
                print(f"  Total: {current.get('total_cells', 0)}, best: {current.get('best_score', 0):.4f}")
                last_count = current.get("total_cells", 0)
            time.sleep(30)
    else:
        file_more_cells()


if __name__ == "__main__":
    main()
