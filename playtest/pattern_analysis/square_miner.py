"""Mine PERFECT SQUARES - the structural feature we discovered dominates."""

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
    print("Mining PERFECT SQUARES — 5000 squares from 50² to 9999²")
    
    seeds = []
    for i in range(50, 9999):
        seeds.append(i * i)
    print(f"Testing {len(seeds)} perfect squares...")
    
    results = []
    for i, seed in enumerate(seeds):
        if i % 500 == 0:
            print(f"  {i}/{len(seeds)}")
        
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
            "sqrt": int(seed ** 0.5),
            "tall_columns": best_tall,
            "base_score": best_score,
            "x": best_pos[0] if best_pos else 16,
            "y": best_pos[1] if best_pos else 16,
        })
    
    results.sort(key=lambda r: (-r["tall_columns"], -r["base_score"]))
    
    print(f"\n=== Top 20 perfect squares by tall_columns ===")
    for i, r in enumerate(results[:20], 1):
        print(f"{i:2}. seed {r['seed']:9} sqrt={r['sqrt']:4} tall={r['tall_columns']} base={r['base_score']:.3f}")
    
    out_file = Path(__file__).parent / "square_miner.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} to {out_file}")


if __name__ == "__main__":
    main()
