"""Super Explorer v2 - uses NEW top seeds discovered."""

import os
import sys
import json
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view, generate_lore


STRATEGIES = [
    "spiral", "zigzag", "perimeter", "straight_east", "spiral_wide",
    "north_south", "diagonal",
]


def explore_seed_strategy(seed, strategy):
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
    elif strategy == "spiral_wide":
        for i in range(n_steps):
            r = 1 + i * 1.5
            theta = i * 0.7
            x = 16 + r * (1 + theta * 0.05)
            y = 16 + r * (1 - theta * 0.05)
            path.append((x, y, theta))
    elif strategy == "straight_east":
        for i in range(n_steps):
            x = i * 1.6
            y = 16
            angle = 0.1 * (i % 5)
            path.append((x, y, angle))
    elif strategy == "perimeter":
        for side in range(4):
            for i in range(n_steps // 4):
                if side == 0: x, y = i * 2, 0
                elif side == 1: x, y = 30, i * 2
                elif side == 2: x, y = 30 - i * 2, 30
                else: x, y = 0, 30 - i * 2
                path.append((x, y, side * 1.57))
    elif strategy == "zigzag":
        for i in range(n_steps):
            x = i * 1.5
            y = 16 + (5 if i % 2 == 0 else -5)
            angle = 0 if i % 2 == 0 else 3.14
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

    best_score = 0
    best_pos = None
    best_lore = ""

    for x, y, angle in path:
        view, densities = render_view(seed, x, y, angle)
        score = score_view(view, densities)

        if score > best_score:
            best_score = score
            best_pos = (x, y, angle)
            best_lore = generate_lore({"view": view, "x": x, "y": y, "angle": angle, "score": score, "seed": seed})

    return {
        "seed": seed,
        "strategy": strategy,
        "best_score": best_score,
        "best_pos": best_pos,
        "lore": best_lore,
    }


def main():
    # NEW top seeds discovered
    seeds = [
        # Best from all runs
        800330, 654321, 390172, 272801, 270801,
        800340, 271791, 777777, 221801, 644321,
        997878, 704321, 389722, 281679, 799840,
        415222, 790340, 801340, 271801, 991990,
        # Plus systematic exploration around best
        800330 + 1, 800330 - 1,
        654321 + 1, 654321 - 1,
        800330 + 100, 800330 - 100,
        654321 + 100, 654321 - 100,
        # Plus some random
        555555, 222222, 333333, 444444, 666666,
        888888, 999999,
    ]

    print(f"Super Explorer v2 — {len(seeds)} seeds × {len(STRATEGIES)} strategies")
    print(f"Total expeditions: {len(seeds) * len(STRATEGIES)}")

    tasks = []
    for seed in seeds:
        for strategy in STRATEGIES:
            tasks.append((seed, strategy))

    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(explore_seed_strategy, s, st): (s, st) for s, st in tasks}
        for i, f in enumerate(as_completed(futures), 1):
            try:
                r = f.result()
                results.append(r)
                if i % 30 == 0:
                    print(f"  completed {i}/{len(tasks)}")
            except Exception as e:
                print(f"  error: {e}")

    results.sort(key=lambda r: -r["best_score"])

    print(f"\n=== Top 10 ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:2}. seed {r['seed']:7} strategy={r['strategy']:14} score={r['best_score']:.3f}")
        print(f"    {r['lore'][:80]}")

    out_file = Path(__file__).parent / "super_explorer_v2_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} results to {out_file}")


if __name__ == "__main__":
    main()
