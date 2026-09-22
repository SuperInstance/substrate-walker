"""Mine specifically for tall_columns feature - the highest-correlation score feature."""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view, generate_lore


def count_tall_columns(view, threshold=0.7):
    h = len(view)
    w = len(view[0]) if view else 0
    if h == 0 or w == 0:
        return 0
    
    tall = 0
    for x in range(w):
        count = 0
        for y in range(h):
            if view[y] and x < len(view[y]) and view[y][x] != ' ':
                count += 1
        if count / h > threshold:
            tall += 1
    return tall


def comprehensive_score(view, densities):
    """Score that REWARDS tall columns."""
    base = score_view(view, densities)
    tall = count_tall_columns(view)
    return base + tall * 0.05  # Bonus per tall column


def main():
    print("Mining for tall_columns cities...")
    
    # Search wide seed range
    rng = random.Random(42)
    seeds_to_try = []
    # Top from previous runs
    seeds_to_try.extend([366025, 230889, 350464, 231361, 77841, 164836, 9901, 800330])
    # Random spread
    for _ in range(2000):
        seeds_to_try.append(rng.randint(10000, 999999))
    seeds_to_try = list(set(seeds_to_try))
    
    print(f"Testing {len(seeds_to_try)} seeds...")
    
    results = []
    for i, seed in enumerate(seeds_to_try):
        if i % 200 == 0:
            print(f"  {i}/{len(seeds_to_try)}")
        
        best_tall = 0
        best_pos = None
        best_score = 0
        best_lore = ""
        
        for x in range(8, 28, 4):
            for y in range(8, 28, 4):
                view, densities = render_view(seed, x, y, 0)
                tall = count_tall_columns(view)
                score = score_view(view, densities)
                
                if tall > best_tall or (tall == best_tall and score > best_score):
                    best_tall = tall
                    best_pos = (x, y)
                    best_score = score
                    best_lore = generate_lore({"view": view, "x": x, "y": y, "angle": 0, "score": score, "seed": seed})
        
        results.append({
            "seed": seed,
            "tall_columns": best_tall,
            "base_score": best_score,
            "comprehensive": best_score + best_tall * 0.05,
            "x": best_pos[0] if best_pos else 16,
            "y": best_pos[1] if best_pos else 16,
            "lore": best_lore,
        })
    
    # Sort by tall_columns DESC, then base_score
    results.sort(key=lambda r: (-r["tall_columns"], -r["base_score"]))
    
    print(f"\n=== Top 20 by tall_columns ===")
    for i, r in enumerate(results[:20], 1):
        print(f"{i:2}. seed {r['seed']:7} tall={r['tall_columns']}, base={r['base_score']:.3f}, comp={r['comprehensive']:.3f}")
        print(f"      '{r['lore'][:70]}'")
    
    # Top by composite (combined)
    results.sort(key=lambda r: -r["comprehensive"])
    print(f"\n=== Top 10 by composite (score + 0.05*tall) ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:2}. seed {r['seed']:7} comp={r['comprehensive']:.3f} tall={r['tall_columns']} - {r['lore'][:60]}")
    
    out_file = Path(__file__).parent / "tall_column_mine.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} to {out_file}")


if __name__ == "__main__":
    main()
