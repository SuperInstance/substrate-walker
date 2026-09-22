"""Honest Composite Score — require balance across all variants.

Composite score = ∏(variants)^(1/n) — the geometric mean.
This requires ALL variants to score well, not just one.
"""

import sys
import json
import asyncio
import random
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
    return min(1.0, sum(sum(1 for c in row if c != ' ') for row in view) / (h * w) * 2)


def score_sharpness(view, densities):
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


def composite_geomean(view, densities):
    """Geometric mean - requires all variants to be good."""
    import math
    scores = [max(0.01, v(view, densities)) for _, v in VARIANTS]
    if any(s <= 0 for s in scores):
        return 0, scores
    return math.prod(scores) ** (1.0 / len(scores)), scores


def main():
    print("Honest Composite (geometric mean) - requires balance across all variants")
    
    # Top seeds
    seeds = [164836, 9901, 7001, 4073, 18381, 310249, 690561, 970225, 800330, 654321]
    seeds.extend([random.randint(100000, 999999) for _ in range(40)])  # Add random
    
    results = []
    for seed in seeds:
        best_score = 0
        best_pos = None
        best_lore = ""
        best_scores = None
        
        for x in range(8, 28, 4):
            for y in range(8, 28, 4):
                for angle_deg in [0, 90]:
                    view, densities = render_view(seed, x, y, angle_deg * 3.14 / 180)
                    cscore, scores = composite_geomean(view, densities)
                    if cscore > best_score:
                        best_score = cscore
                        best_pos = (x, y, angle_deg)
                        best_scores = scores
        
        # Generate lore at best
        from playtest_v2 import generate_lore
        view, densities = render_view(seed, best_pos[0], best_pos[1], best_pos[2])
        lore = generate_lore({"view": view, "x": best_pos[0], "y": best_pos[1], "angle": best_pos[2], "score": best_score, "seed": seed})
        
        results.append({
            "seed": seed,
            "composite": best_score,
            "best_pos": best_pos,
            "scores": best_scores,
            "lore": lore,
        })
        print(f"  seed {seed:7}: composite={best_score:.3f} - {lore[:50]}")
    
    results.sort(key=lambda r: -r["composite"])
    
    print(f"\n=== Top 10 by honest composite ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:2}. seed {r['seed']:7} {r['composite']:.3f} - {r['lore'][:60]}")
    
    out_file = Path(__file__).parent / "honest_composite.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    main()
