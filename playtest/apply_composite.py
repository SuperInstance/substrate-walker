"""Apply composite MAX scoring to ALL top seeds."""

import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '.')
from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view as base_score_view


def score_atmospheric(view, densities):
    h = len(view)
    w = len(view[0]) if view else 0
    density = sum(sum(1 for c in row if c != ' ') for row in view) / (h * w)
    variety = len(set(c for row in view for c in row if c != ' ')) / 12
    horizon = sum(1 for d in densities[h//2-3:h//2+3] if d > 3)
    return min(1.0, density * 0.3 + variety * 0.4 + horizon / 6 * 0.3)


def score_vertical(view, densities):
    h = len(view)
    center_x = h // 2
    vertical = sum(1 for i in range(center_x - 4, center_x + 5) if 0 <= i < h and densities[i] > 2)
    variety = len(set(c for row in view for c in row if c != ' ')) / 12
    return min(1.0, vertical / 8 * 0.5 + variety * 0.5)


def score_dense(view, densities):
    h = len(view)
    w = len(view[0]) if view else 0
    return sum(sum(1 for c in row if c != ' ') for row in view) / (h * w)


def score_sharpness(view, densities):
    """Sharp edges - high contrast between filled/empty areas."""
    h = len(view)
    w = len(view[0]) if view else 0
    edges = 0
    for y in range(h-1):
        for x in range(w-1):
            if (view[y][x] != ' ' and view[y+1][x+1] == ' ') or (view[y][x] == ' ' and view[y+1][x+1] != ' '):
                edges += 1
    return min(1.0, edges / 100)


VARIANTS = [
    ("base", base_score_view),
    ("atmospheric", score_atmospheric),
    ("vertical", score_vertical),
    ("dense", score_dense),
    ("sharpness", score_sharpness),
]


def composite_max(view, densities):
    scores = [v(view, densities) for _, v in VARIANTS]
    return max(scores), scores


def composite_mean(view, densities):
    scores = [v(view, densities) for _, v in VARIANTS]
    return sum(scores) / len(scores), scores


def main():
    print("Applying composite scoring to top seeds...")
    
    # Top seeds from great moments
    gm = json.load(open("great_moments.json"))
    seeds = [m["seed"] for m in gm[:50]]
    
    results = []
    for seed in seeds:
        # Find best position
        best_max = 0
        best_pos = None
        best_scores = None
        best_lore = ""
        
        for x in range(8, 28, 4):
            for y in range(8, 28, 4):
                for angle_deg in [0, 90, 180]:
                    view, densities = render_view(seed, x, y, angle_deg * 3.14 / 180)
                    cmax, scores = composite_max(view, densities)
                    if cmax > best_max:
                        best_max = cmax
                        best_pos = (x, y, angle_deg)
                        best_scores = scores
        
        # Generate lore at best position
        from playtest_v2 import generate_lore
        view, densities = render_view(seed, best_pos[0], best_pos[1], best_pos[2])
        lore = generate_lore({"view": view, "x": best_pos[0], "y": best_pos[1], "angle": best_pos[2], "score": best_max, "seed": seed})
        best_lore = lore
        
        results.append({
            "seed": seed,
            "best_max": best_max,
            "best_pos": best_pos,
            "scores": best_scores,
            "lore": best_lore,
        })
        print(f"  seed {seed:7}: max={best_max:.3f} at {best_pos} - {lore[:50]}")
    
    results.sort(key=lambda r: -r["best_max"])
    
    print(f"\n=== Top 10 by composite MAX ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:2}. seed {r['seed']:7} {r['best_max']:.3f} - {r['lore'][:60]}")
    
    # Stats
    above_087 = sum(1 for r in results if r["best_max"] >= 0.87)
    above_090 = sum(1 for r in results if r["best_max"] >= 0.90)
    print(f"\nSeeds >= 0.87: {above_087}/{len(results)}")
    print(f"Seeds >= 0.90: {above_090}/{len(results)}")
    
    out_file = Path(__file__).parent / "composite_max_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    main()
