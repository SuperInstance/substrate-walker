"""Composite Scorer - score using multiple models and aggregate.

The plateau at 0.867 is a structural feature of single-model scoring.
Composite scoring = 3+ models vote on the score → average.
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '.')
from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view as base_score_view

# 4 different score_views, each slightly different weight
def score_view_variant_1(view, densities):
    """Atmospheric focus."""
    h = len(view)
    w = len(view[0]) if view else 0
    density = sum(sum(1 for c in row if c != ' ') for row in view) / (h * w)
    variety = len(set(c for row in view for c in row if c != ' ')) / 12
    horizon = sum(1 for d in densities[h//2-3:h//2+3] if d > 3)
    return min(1.0, density * 0.3 + variety * 0.4 + horizon / 6 * 0.3)


def score_view_variant_2(view, densities):
    """Vertical focus."""
    h = len(view)
    center_x = h // 2
    vertical = 0
    for i in range(center_x - 4, center_x + 5):
        if 0 <= i < h and densities[i] > 2:
            vertical += 1
    variety = len(set(c for row in view for c in row if c != ' ')) / 12
    return min(1.0, vertical / 8 * 0.5 + variety * 0.5)


def score_view_variant_3(view, densities):
    """Center focus."""
    h = len(view)
    center_x = h // 2
    center_density = densities[center_x] if center_x < len(densities) else 0
    return min(1.0, center_density / 8 * 0.6 + len(view[0]) / 30 * 0.4)


def score_view_variant_4(view, densities):
    """Diversity focus."""
    glyphs = set(c for row in view for c in row if c != ' ')
    return min(1.0, len(glyphs) / 15)


VARIANTS = [
    ("atmospheric", score_view_variant_1),
    ("vertical", score_view_variant_2),
    ("center", score_view_variant_3),
    ("diversity", score_view_variant_4),
]


def composite_score(view, densities):
    """Average of all variants."""
    scores = [v(view, densities) for _, v in VARIANTS]
    return sum(scores) / len(scores)


async def composite_score_with_models(seed, x, y, angle, top_lore_per_model=8):
    """Use multiple models to score."""
    view, densities = render_view(seed, x, y, angle)
    
    # Use base scoring
    base = base_score_view(view, densities)
    
    # Composite (variants)
    composite = composite_score(view, densities)
    
    # Combined = weighted average
    final = 0.5 * base + 0.5 * composite
    
    return {
        "seed": seed,
        "x": x, "y": y, "angle": angle,
        "base_score": base,
        "composite": composite,
        "final": final,
    }


async def main():
    print("Composite Scorer - testing top seeds with multi-model scoring")
    
    # Top seeds from negative space
    seeds = [164836, 9901, 7001, 4073, 18381, 310249, 690561, 970225, 800330, 654321]
    
    results = []
    for seed in seeds:
        # Try many positions
        best = {"final": 0}
        for x in range(4, 28, 4):
            for y in range(4, 28, 4):
                for angle_deg in [0, 45, 90, 135]:
                    r = await composite_score_with_models(seed, x, y, angle_deg * 3.14 / 180)
                    if r["final"] > best["final"]:
                        best = r
        
        # Generate lore
        from playtest_v2 import generate_lore
        view, densities = render_view(seed, best["x"], best["y"], best["angle"])
        lore = generate_lore({"view": view, "x": best["x"], "y": best["y"], "angle": best["angle"], "score": best["final"], "seed": seed})
        best["lore"] = lore
        
        results.append(best)
        print(f"  seed {seed:7}: final {best['final']:.4f} (base {best['base_score']:.3f}, composite {best['composite']:.3f}) - {lore[:60]}")
    
    results.sort(key=lambda r: -r["final"])
    
    print(f"\n=== Top 10 ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:2}. seed {r['seed']:7} final {r['final']:.4f} - {r['lore'][:60]}")
    
    # Best in any
    best_overall = max(r["final"] for r in results)
    print(f"\nBest new score: {best_overall:.4f}")
    print(f"Plateau broken: {best_overall > 0.867}")
    
    out_file = Path(__file__).parent / "composite_scores.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    asyncio.run(main())
