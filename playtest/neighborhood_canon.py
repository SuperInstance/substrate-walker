"""Neighborhood Canon - explore cells ADJACENT to top-scoring seeds.

The negative space: not the seeds themselves, but their neighbors.
"""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view, generate_lore


def neighborhood(seed, radius):
    """Generate seeds in the neighborhood of `seed`."""
    neighbors = []
    for offset in range(-radius, radius + 1):
        neighbors.append(seed + offset)
    # Also multiplicative
    for mult in [2, 3, 5]:
        neighbors.append(seed * mult)
        neighbors.append(seed // mult if seed > 0 else seed)
    return list(set(neighbors))


def main():
    print("Building Neighborhood Canon — explore cells adjacent to top seeds")
    
    # Top known seeds
    top_seeds = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))
    top_20 = [m["seed"] for m in top_seeds[:20]]
    
    # Generate neighborhoods of top seeds
    neighbor_seeds = set()
    for seed in top_20:
        for radius in [10, 100, 1000]:
            neighbors = neighborhood(seed, radius)
            neighbor_seeds.update(neighbors)
    
    print(f"Neighborhood seed count: {len(neighbor_seeds)}")
    
    # Sample 200 of them
    rng = random.Random(42)
    sampled = rng.sample(list(neighbor_seeds), min(200, len(neighbor_seeds)))
    
    results = []
    for i, seed in enumerate(sampled):
        if i % 20 == 0:
            print(f"  {i}/{len(sampled)}")
        
        best_score = 0
        best_x, best_y = 16, 16
        for x in range(8, 28, 4):
            for y in range(8, 28, 4):
                view, densities = render_view(seed, x, y, 0)
                score = score_view(view, densities)
                if score > best_score:
                    best_score = score
                    best_x, best_y = x, y
        
        # Find which top seed this is a neighbor of
        closest_top = None
        closest_dist = float('inf')
        for ts in top_20:
            d = abs(seed - ts)
            if d < closest_dist:
                closest_dist = d
                closest_top = ts
        
        view, densities = render_view(seed, best_x, best_y, 0)
        lore = generate_lore({"view": view, "x": best_x, "y": best_y, "angle": 0, "score": best_score, "seed": seed})
        
        results.append({
            "seed": seed,
            "best_score": best_score,
            "x": best_x, "y": best_y,
            "lore": lore,
            "closest_top_seed": closest_top,
            "distance_from_top": closest_dist,
        })
    
    results.sort(key=lambda r: -r["best_score"])
    
    print(f"\n=== Top 15 ===")
    for i, r in enumerate(results[:15], 1):
        print(f"{i:2}. seed {r['seed']:9} score {r['best_score']:.3f} (Δ{r['distance_from_top']} from {r['closest_top_seed']}) - {r['lore'][:50]}")
    
    out_file = Path(__file__).parent / "neighborhood_canon.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} to {out_file}")


if __name__ == "__main__":
    main()
