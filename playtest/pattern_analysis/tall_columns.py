"""Find seeds with HIGH tall_columns score - they have tall buildings (the
defining feature of substrate-walker's best lores).
"""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view as base_score_view


def count_tall_columns(view):
    """Number of columns with >70% density."""
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
        if count / h > 0.7:
            tall += 1
    return tall


def main():
    print("Finding seeds with many tall columns (the best-scoring feature)...")
    
    # Search broader seed space
    rng = random.Random(42)
    seeds_to_try = []
    # Top known good
    seeds_to_try.extend([164836, 9901, 7001, 4073, 800330, 654321])
    # Negative space patterns
    seeds_to_try.extend([i*i for i in range(100, 1000)])  # Perfect squares
    # Random
    for _ in range(100):
        seeds_to_try.append(rng.randint(100000, 999999))
    
    results = []
    for seed in seeds_to_try:
        best_tall = 0
        best_pos = None
        best_base = 0
        for x in range(8, 28, 4):
            for y in range(8, 28, 4):
                view, densities = render_view(seed, x, y, 0)
                tall = count_tall_columns(view)
                if tall > best_tall:
                    best_tall = tall
                    best_pos = (x, y)
                    best_base = base_score_view(view, densities)
        
        results.append({
            "seed": seed,
            "tall_columns": best_tall,
            "base_score": best_base,
            "x": best_pos[0] if best_pos else 16,
            "y": best_pos[1] if best_pos else 16,
        })
    
    results.sort(key=lambda r: (-r["tall_columns"], -r["base_score"]))
    
    print(f"Top 10 by tall_columns:")
    for r in results[:10]:
        print(f"  seed {r['seed']:7}: tall={r['tall_columns']}, base={r['base_score']:.3f}")
    
    # Distribution
    from collections import Counter
    tall_dist = Counter(r["tall_columns"] for r in results)
    print(f"\nDistribution:")
    for k in sorted(tall_dist.keys()):
        print(f"  tall={k}: {tall_dist[k]}")
    
    out_file = Path(__file__).parent / "tall_columns.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} to {out_file}")


if __name__ == "__main__":
    main()
