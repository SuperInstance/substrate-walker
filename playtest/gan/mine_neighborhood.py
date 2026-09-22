"""Mine around seed 800340 - the all-time best."""

import os
import sys
import json
import random
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view, generate_lore


def explore_seed(seed):
    """Comprehensive exploration of one seed."""
    # Try many positions/angles
    positions = []
    for x in range(0, 32, 4):
        for y in range(0, 32, 4):
            for angle_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
                positions.append((x + random.uniform(-2, 2),
                                  y + random.uniform(-2, 2),
                                  angle_deg * 3.14 / 180))

    best_score = 0
    best_pos = None
    best_lore = ""

    for x, y, angle in positions:
        view, densities = render_view(seed, x, y, angle)
        score = score_view(view, densities)

        if score > best_score:
            best_score = score
            best_pos = (x, y, angle)
            best_lore = generate_lore({"view": view, "x": x, "y": y, "angle": angle, "score": score, "seed": seed})

    return {
        "seed": seed,
        "best_score": best_score,
        "best_pos": best_pos,
        "lore": best_lore,
    }


def main():
    base_seed = 800340
    print(f"Mining neighborhood of seed {base_seed}")
    print("Trying ±50,000 variations...")

    seeds = [base_seed + offset for offset in [-50000, -25000, -10000, -5000, -1000, -500,
                                                  -100, -50, -10, 0, 10, 50, 100, 500,
                                                  1000, 5000, 10000, 25000, 50000]]

    results = []
    for seed in seeds:
        result = explore_seed(seed)
        results.append(result)
        print(f"  seed {seed:7}: score {result['best_score']:.3f} - {result['lore'][:60]}")

    # Sort by score
    results.sort(key=lambda r: -r["best_score"])

    print(f"\n=== Top 10 Variations ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:2}. seed {r['seed']:7}: {r['best_score']:.3f} - {r['lore'][:70]}")

    out_file = Path(__file__).parent / "neighborhood_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    main()
