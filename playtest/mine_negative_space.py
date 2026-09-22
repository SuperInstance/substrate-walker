"""Mine the negative-space seeds (1328 of them)."""

import os
import sys
import json
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view


def quick_score(seed):
    """Quick scoring: try one path and one position."""
    best_score = 0
    best_x, best_y, best_angle = 16, 16, 0
    
    # Try a few positions
    for offset in [0, 4, 8, 12, -4, -8]:
        for yoff in [0, 4, 8, 12, -4, -8]:
            try:
                x = 16 + offset
                y = 16 + yoff
                view, densities = render_view(seed, x, y, 0)
                score = score_view(view, densities)
                if score > best_score:
                    best_score = score
                    best_x, best_y = x, y
            except:
                pass
    
    return {"seed": seed, "best_score": best_score, "x": best_x, "y": best_y}


def main():
    # Load negative space seeds
    seeds_data = json.load(open("negative_space_seeds.json"))
    seeds = [s for s in seeds_data if isinstance(s, int)]
    print(f"Mining {len(seeds)} negative-space seeds")

    results = []
    for i, seed in enumerate(seeds):
        if i % 100 == 0:
            print(f"  {i}/{len(seeds)}")
        try:
            r = quick_score(seed)
            results.append(r)
        except Exception as e:
            print(f"  error at {seed}: {e}")

    results.sort(key=lambda r: -r["best_score"])

    print(f"\nTotal: {len(results)}")
    print("\n=== Top 20 ===")
    for i, r in enumerate(results[:20], 1):
        print(f"{i:2}. seed {r['seed']:12} score {r['best_score']:.3f} at ({r['x']}, {r['y']})")

    # Check for new all-time bests
    new_bests = [r for r in results if r["best_score"] >= 0.87]
    print(f"\nSeeds scoring >= 0.87: {len(new_bests)}")
    for r in new_bests:
        print(f"  seed {r['seed']:12} score {r['best_score']:.3f}")

    # Save all
    out_file = Path(__file__).parent / "negative_space_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    main()
