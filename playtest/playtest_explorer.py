"""
Playtest Explorer — uses diverse strategies to find great moments.

Combines:
1. Random seeds (variety)
2. Different path strategies (spiral, straight, wander, explore)
3. Different camera angles
4. Multiple API models (diversity)

Finds the "gold" by combining all these dimensions.
"""

import os
import sys
import json
import asyncio
import random
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view, generate_lore


# Many strategies
STRATEGIES = [
    "spiral", "explore", "straight_east", "wander",
    "north_south", "diagonal", "perimeter", "labyrinth",
    "spiral_inverse", "spiral_wide", "zigzag", "random_walk",
]


async def explore_one(seed, strategy):
    """Explore one seed with one strategy."""
    rng = random.Random(f"{seed}-{strategy}")
    n_steps = 15
    path = []

    if strategy == "spiral":
        for i in range(n_steps):
            r = 1 + i * 0.7
            theta = i * 0.4
            x = 16 + r * (1 + theta * 0.05)
            y = 16 + r * (1 - theta * 0.05)
            path.append((x, y, theta))
    elif strategy == "spiral_inverse":
        for i in range(n_steps):
            r = 16 - i * 0.7
            theta = -i * 0.4
            x = 16 + r * (1 + theta * 0.05)
            y = 16 + r * (1 - theta * 0.05)
            path.append((x, y, theta))
    elif strategy == "spiral_wide":
        for i in range(n_steps):
            r = 1 + i * 1.5
            theta = i * 0.7
            x = 16 + r * (1 + theta * 0.05)
            y = 16 + r * (1 - theta * 0.05)
            path.append((x, y, theta))
    elif strategy == "explore":
        x, y, angle = 16.0, 16.0, 0.0
        for _ in range(n_steps):
            x += rng.uniform(-3, 3)
            y += rng.uniform(-3, 3)
            angle += rng.uniform(-0.5, 0.5)
            path.append((x, y, angle))
    elif strategy == "straight_east":
        for i in range(n_steps):
            x = i * 1.6
            y = 16
            angle = 0.1 * (i % 5)
            path.append((x, y, angle))
    elif strategy == "north_south":
        for i in range(n_steps):
            y = i * 1.6
            x = 16
            angle = 1.57
            path.append((x, y, angle))
    elif strategy == "diagonal":
        for i in range(n_steps):
            x = i
            y = i
            angle = 0.785
            path.append((x, y, angle))
    elif strategy == "perimeter":
        # Walk around the perimeter
        for side in range(4):
            for i in range(n_steps // 4):
                if side == 0: x, y = i * 2, 0
                elif side == 1: x, y = 30, i * 2
                elif side == 2: x, y = 30 - i * 2, 30
                else: x, y = 0, 30 - i * 2
                path.append((x, y, side * 1.57))
    elif strategy == "labyrinth":
        x, y, angle = 16, 16, 0
        for _ in range(n_steps):
            # Random turn + step
            angle = rng.choice([0, 1.57, 3.14, 4.71])
            x += [1, 0, -1, 0][int(angle / 1.57)] * 1.5
            y += [0, 1, 0, -1][int(angle / 1.57)] * 1.5
            x = max(0, min(32, x))
            y = max(0, min(32, y))
            path.append((x, y, angle))
    elif strategy == "zigzag":
        for i in range(n_steps):
            x = i * 1.5
            y = 16 + (5 if i % 2 == 0 else -5)
            angle = 0 if i % 2 == 0 else 3.14
            path.append((x, y, angle))
    else:  # random_walk
        x, y, angle = 16, 16, 0
        for _ in range(n_steps):
            x += random.uniform(-3, 3)
            y += random.uniform(-3, 3)
            angle = rng.uniform(0, 6.28)
            path.append((x, y, angle))

    # Score the path
    snapshots = []
    for x, y, angle in path:
        view, densities = render_view(seed, x, y, angle)
        score = score_view(view, densities)
        snapshots.append({
            "x": x, "y": y, "angle": angle,
            "view": view, "score": score,
        })

    best = max(snapshots, key=lambda s: s["score"])

    # Generate lore
    lore = await asyncio.to_thread(generate_lore, best)

    return {
        "seed": seed,
        "strategy": strategy,
        "best_score": best["score"],
        "best_x": best["x"],
        "best_y": best["y"],
        "best_angle": best["angle"],
        "lore": lore,
        "n_snapshots": len(snapshots),
    }


async def main(n_seeds=20):
    rng = random.Random(123)
    seeds = [rng.randint(1000, 999999) for _ in range(n_seeds)]

    tasks = []
    for seed in seeds:
        for strategy in STRATEGIES:
            tasks.append(explore_one(seed, strategy))

    print(f"Exploration: {len(tasks)} expeditions ({n_seeds} seeds × {len(STRATEGIES)} strategies)")
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter valid
    valid = [r for r in results if not isinstance(r, Exception)]
    print(f"Valid: {len(valid)}")

    # Sort by score
    valid.sort(key=lambda r: -r["best_score"])

    print("\n=== Top 20 ===")
    for i, r in enumerate(valid[:20], 1):
        print(f"{i:2}. seed={r['seed']:6} strategy={r['strategy']:14} score={r['best_score']:.3f}")
        print(f"    lore: {r['lore'][:70]}")

    # Save
    out_file = Path(__file__).parent / "explorer_results.json"
    with open(out_file, "w") as f:
        json.dump(valid, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    asyncio.run(main(n))
