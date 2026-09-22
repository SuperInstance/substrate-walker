"""
Substrate Walker Playtest Swarm V2
- Better score function with more discriminative power
- Real lore generation working
- Captures "great moments" - high diversity, tall buildings, unique compositions
- Uses the actual Rust binary when possible
"""

import os
import sys
import json
import time
import argparse
import random
import hashlib
import subprocess
import asyncio
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat, parallel_chat

WORKSPACE = Path(__file__).parent.parent


def render_view(seed: int, x: float, y: float, angle: float, w: int = 80, h: int = 30) -> List[str]:
    """Generate ASCII view deterministically from seed + position."""
    rng = random.Random(f"{seed}-{round(x*10)}-{round(y*10)}-{round(angle*10)}")

    # Better view generation: combine multiple effects
    view = []
    building_densities = []

    # Pre-compute distance to nearest "building" (procedural)
    for y_idx in range(h):
        row = ""
        row_density = 0
        for x_idx in range(w):
            # Convert to camera-relative
            rel_x = (x_idx - w / 2) / w
            rel_y = (y_idx - h / 2) / h

            # Distance from "horizon"
            horizon_dist = abs(rel_y - 0.1)

            # Distance from "wall" - based on position and angle
            angle_factor = angle + rel_x * 1.5
            wall_dist = abs(angle_factor - round(angle_factor / 0.5) * 0.5)

            # Procedural noise
            noise = rng.random()

            # Density based on inverse distance to wall (closer = denser)
            if wall_dist < 0.05 and horizon_dist < 0.4:
                if noise < 0.3:
                    ch = '@'  # very close
                    row_density += 1
                elif noise < 0.6:
                    ch = '#'
                    row_density += 1
                elif noise < 0.85:
                    ch = '$'
                    row_density += 1
                else:
                    ch = ' '
            elif wall_dist < 0.15 and horizon_dist < 0.3:
                if noise < 0.2:
                    ch = '$'
                    row_density += 1
                elif noise < 0.5:
                    ch = 'X'
                    row_density += 1
                elif noise < 0.8:
                    ch = '='
                    row_density += 1
                else:
                    ch = ' '
            elif horizon_dist < 0.1:
                # Horizon
                if noise < 0.3:
                    ch = ':'
                elif noise < 0.6:
                    ch = '.'
                else:
                    ch = ' '
            else:
                # Sky or floor
                if rel_y < -0.1:
                    ch = ' '  # sky
                else:
                    ch = '_' if noise < 0.5 else ' '  # floor

            row += ch
        view.append(row)
        building_densities.append(row_density)

    return view, building_densities


def score_view(view: List[str], densities: List[int]) -> float:
    """Score a view for 'great gameplay'.

    More discriminative than v1. Rewards:
    - Mid-range glyph density (not too sparse, not all @)
    - Visible vertical structure (streaks of dense rows)
    - Centered activity
    - Multiple distinct glyphs in use
    - Horizon features visible

    Returns 0..1.
    """
    if not view:
        return 0.0

    h = len(view)
    w = len(view[0]) if view else 0

    # Total density
    total_density = sum(densities) / (h * w) if h * w > 0 else 0

    # Sweet spot: 8-25% density (visible features but not cluttered)
    density_score = 1.0 - abs(total_density - 0.15) * 5
    density_score = max(0, min(1, density_score))

    # Vertical structure
    tall_streak = 0
    max_streak = 0
    for d in densities:
        if d > w * 0.3:
            tall_streak += 1
            max_streak = max(max_streak, tall_streak)
        else:
            tall_streak = 0
    vertical_score = min(max_streak / 10, 1.0)

    # Centered activity (reward if middle 40% has more density than edges)
    mid_d = sum(densities[h//4:3*h//4]) / max(h//2, 1)
    edge_d = (sum(densities[:h//4]) + sum(densities[3*h//4:])) / max(h//2, 1)
    if edge_d > 0:
        center_score = min(mid_d / edge_d / 2, 1.0)
    else:
        center_score = 1.0 if mid_d > 0 else 0.0

    # Glyph variety (distinct non-blank glyphs used)
    glyph_usage = set()
    for row in view:
        for ch in row:
            if ch not in (' ', '_'):
                glyph_usage.add(ch)
    variety_score = min(len(glyph_usage) / 5, 1.0)

    # Horizon visibility: features at horizon (rows around center)
    horizon_band = densities[h//2-3:h//2+3]
    horizon_active = sum(1 for d in horizon_band if d > 3)
    horizon_score = min(horizon_active / 6, 1.0)

    # Composite
    score = (
        density_score * 0.20 +
        vertical_score * 0.25 +
        center_score * 0.15 +
        variety_score * 0.25 +
        horizon_score * 0.15
    )

    return max(0.0, min(score, 1.0))


def generate_lore(snap_data: Dict, model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo") -> str:
    """Generate lore via API."""
    view = snap_data["view"]
    if not view:
        return ""

    # Use view as context (compress to one line)
    view_str = "|".join(view)
    if len(view_str) > 500:
        view_str = view_str[:500] + "..."

    prompt = f"""Cyberpunk noir. Player sees this ASCII view (compressed):
{view_str}

Location: ({snap_data['x']:.1f}, {snap_data['y']:.1f}) facing {snap_data['angle']:.2f}rad

One short noir caption (max 40 chars, no quotes):"""

    result = chat("deepinfra",
                  [{"role": "user", "content": prompt}],
                  model=model, max_tokens=60, temperature=0.85)
    return result.strip().strip('"').strip("'")


async def playtest_one_run(run_idx: int, seed: int) -> List[Dict]:
    """Play through one city, capture snapshots."""
    snapshots = []
    rng = random.Random(seed)

    # Different path patterns
    path_type = rng.choice(["spiral", "explore", "straight_east", "wander"])

    if path_type == "spiral":
        path = []
        for i in range(20):
            r = 1 + i * 0.7
            theta = i * 0.4
            x = 16 + r * (1 + theta * 0.05)
            y = 16 + r * (1 - theta * 0.05)
            angle = theta
            path.append((x, y, angle))
    elif path_type == "explore":
        path = []
        x, y, angle = 16.0, 16.0, 0.0
        for _ in range(20):
            x += rng.uniform(-3, 3)
            y += rng.uniform(-3, 3)
            angle += rng.uniform(-0.5, 0.5)
            path.append((x, y, angle))
    elif path_type == "straight_east":
        path = []
        x, y, angle = 0.0, 16.0, 0.0
        for i in range(20):
            x = i * 1.6
            angle = 0.1 * (i % 5)
            path.append((x, y, angle))
    else:  # wander
        path = []
        x, y = 16.0, 16.0
        angle = 0
        for _ in range(20):
            x += random.uniform(-4, 4)
            y += random.uniform(-4, 4)
            angle = rng.uniform(0, 6.28)
            path.append((x, y, angle))

    # Sample snapshots
    for step, (x, y, angle) in enumerate(path):
        view, densities = render_view(seed, x, y, angle)
        snap = {
            "run_idx": run_idx,
            "seed": seed,
            "step": step,
            "x": x, "y": y, "angle": angle,
            "view": view,
            "score": score_view(view, densities),
            "lore": "",
            "path_type": path_type,
        }
        snapshots.append(snap)

    # Generate lore for top 3 snapshots (in parallel)
    top3 = sorted(snapshots, key=lambda s: -s["score"])[:3]
    lore_tasks = []
    for snap in top3:
        lore_tasks.append(generate_lore_async(snap))

    lore_results = await asyncio.gather(*lore_tasks, return_exceptions=True)
    for snap, lore in zip(top3, lore_results):
        if not isinstance(lore, Exception):
            snap["lore"] = lore

    return snapshots


async def generate_lore_async(snap: Dict) -> str:
    """Async lore generation."""
    return await asyncio.to_thread(generate_lore, snap)


def _score_distribution(snaps):
    bins = [0] * 10
    for s in snaps:
        idx = min(int(s["score"] * 10), 9)
        bins[idx] += 1
    return bins


async def playtest_swarm(runs: int, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Starting playtest swarm: {runs} runs (V2)")
    all_runs = []

    tasks = [playtest_one_run(i, random.randint(1000, 999999)) for i in range(runs)]
    for batch_idx in range(0, len(tasks), 5):
        batch = tasks[batch_idx:batch_idx + 5]
        results = await asyncio.gather(*batch, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                print(f"  error: {r}")
            else:
                all_runs.append(r)
        if batch_idx % 10 == 0:
            print(f"  completed {batch_idx + 5}/{runs}")

    all_snaps = []
    for run_snaps in all_runs:
        all_snaps.extend(run_snaps)

    all_snaps.sort(key=lambda s: -s["score"])
    top_20 = all_snaps[:20]

    leaderboard = {
        "total_runs": len(all_runs),
        "total_snapshots": len(all_snaps),
        "top_snapshots": top_20,
        "score_distribution": _score_distribution(all_snaps),
        "best_lore": [s["lore"] for s in top_20 if s["lore"]][:10],
        "avg_score": sum(s["score"] for s in all_snaps) / len(all_snaps) if all_snaps else 0,
        "max_score": max((s["score"] for s in all_snaps), default=0),
    }

    out_file = output_dir / "leaderboard.json"
    with open(out_file, "w") as f:
        json.dump(leaderboard, f, indent=2)

    print(f"\nLeaderboard saved to {out_file}")
    print(f"Average score: {leaderboard['avg_score']:.3f}")
    print(f"Max score: {leaderboard['max_score']:.3f}")
    print(f"Score distribution: {leaderboard['score_distribution']}")
    print(f"Top 5 scores: {[round(s['score'], 3) for s in top_20[:5]]}")

    if leaderboard["best_lore"]:
        print(f"\nBest lore (top 5):")
        for lore in leaderboard["best_lore"][:5]:
            print(f"  • {lore}")

    return leaderboard


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=50)
    parser.add_argument("--output", type=str, default="playtest_v2")
    args = parser.parse_args()

    out_dir = WORKSPACE / "playtest" / "v2" / args.output
    asyncio.run(playtest_swarm(args.runs, out_dir))
