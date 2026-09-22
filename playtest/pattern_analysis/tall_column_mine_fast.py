"""Find tall_column seeds - no API calls, fast."""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view as base_score_view


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


def main():
    print("Fast tall_column discovery - 5000 seeds, no API calls")
    
    rng = random.Random(42)
    seeds_to_try = set()
    # Top from previous
    seeds_to_try.update([366025, 230889, 350464, 231361, 77841, 164836, 9901, 800330])
    # Random spread
    for _ in range(5000):
        seeds_to_try.add(rng.randint(10000, 999999))
    
    seeds_to_try = list(seeds_to_try)
    print(f"Testing {len(seeds_to_try)} seeds...")
    
    results = []
    for i, seed in enumerate(seeds_to_try):
        if i % 500 == 0:
            print(f"  {i}/{len(seeds_to_try)}")
        
        best_tall = 0
        best_pos = None
        best_score = 0
        
        for x in range(8, 28, 4):
            for y in range(8, 28, 4):
                view, densities = render_view(seed, x, y, 0)
                tall = count_tall_columns(view)
                score = base_score_view(view, densities)
                
                if tall > best_tall or (tall == best_tall and score > best_score):
                    best_tall = tall
                    best_pos = (x, y)
                    best_score = score
        
        results.append({
            "seed": seed,
            "tall_columns": best_tall,
            "base_score": best_score,
            "x": best_pos[0] if best_pos else 16,
            "y": best_pos[1] if best_pos else 16,
        })
    
    # Sort by tall_columns DESC
    results.sort(key=lambda r: (-r["tall_columns"], -r["base_score"]))
    
    print(f"\n=== Top 25 by tall_columns ===")
    for i, r in enumerate(results[:25], 1):
        print(f"{i:2}. seed {r['seed']:7} tall={r['tall_columns']} base={r['base_score']:.3f}")
    
    # Distribution
    from collections import Counter
    tall_dist = Counter(r["tall_columns"] for r in results)
    print(f"\nDistribution:")
    for k in sorted(tall_dist.keys()):
        print(f"  tall={k}: {tall_dist[k]}")
    
    out_file = Path(__file__).parent / "tall_column_mine_fast.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} to {out_file}")


if __name__ == "__main__":
    main()
