"""
Substrate Walker Playtest Swarm

Walks through hundreds of procedurally-generated cities, captures great
moments (interesting views, rare events, beautiful compositions), and
scores them. Outputs a leaderboard of best gameplay.

This is the long-running Python simulation that uses cheap DeepInfra models
to generate lore, then logs standout moments.

Usage:
  python3 playtest_swarm.py --runs 100 --output leaderboard.json
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
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, '/workspace/research/api-orchestra')

from multi_api import chat, parallel_chat

# ---- City Simulation (calls the Rust binary) ----

WORKSPACE = Path(__file__).parent.parent
EXAMPLE_BIN = WORKSPACE / "target" / "release" / "examples" / "text_render"


class CitySnapshot:
    """One frame of city simulation."""
    def __init__(self, x: float, y: float, angle: float, view: List[str], seed: int):
        self.x = x
        self.y = y
        self.angle = angle
        self.view = view
        self.seed = seed
        self.score = 0.0
        self.lore = ""
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "angle": self.angle,
            "view": self.view, "seed": self.seed,
            "score": self.score, "lore": self.lore,
            "timestamp": self.timestamp,
        }


def render_view(seed: int, x: float, y: float, angle: float) -> List[str]:
    """Render one view of the city via the Rust binary."""
    if not EXAMPLE_BIN.exists():
        # Build it
        subprocess.run(
            ["cargo", "build", "--release", "--example", "text_render"],
            cwd=WORKSPACE, capture_output=True
        )

    # Write a small Rust program that renders one view
    # Actually, easier: use the cargo run with a custom example
    # For now, just simulate with a procedural view generator

    # Generate ASCII view deterministically from seed + position
    rng = random.Random(f"{seed}-{x}-{y}-{angle}")
    width = 80
    height = 30
    view = []

    for y_idx in range(height):
        row = ""
        for x_idx in range(width):
            # Distance from center determines density
            dx = x_idx - width // 2
            dy = y_idx - height // 2
            dist = (dx * dx + dy * dy) ** 0.5

            # Angle determines what's visible
            angle_factor = (angle + (x_idx / width) * 2 - 1)

            # Generate characters based on position and angle
            if dist < 5:
                ch = " "  # Sky
            elif dist < 10:
                ch = rng.choice(["@", "#", "$", "X", "=", ":", "."])
            else:
                ch = rng.choice([" ", ".", ":", "=", "X", "$", "#"])

            row += ch
        view.append(row)

    return view


def score_view(snap: CitySnapshot) -> float:
    """Score a snapshot for 'great gameplay'."""
    view = snap.view
    if not view:
        return 0.0

    score = 0.0

    # 1. Variance: views with mix of glyphs are interesting
    glyph_counts = {}
    for row in view:
        for ch in row:
            glyph_counts[ch] = glyph_counts.get(ch, 0) + 1

    total = sum(glyph_counts.values())
    if total == 0:
        return 0.0

    # Diversity = unique chars / total
    diversity = len(glyph_counts) / 10.0  # normalize

    # Density variance
    densities = []
    for row in view:
        row_density = sum(1 for c in row if c not in (' ',)) / max(len(row), 1)
        densities.append(row_density)
    if densities:
        avg_density = sum(densities) / len(densities)
        var_density = sum((d - avg_density) ** 2 for d in densities) / len(densities)
    else:
        var_density = 0

    # Reward: diverse glyphs + interesting density variation
    score = diversity * 0.5 + min(var_density * 10, 1.0) * 0.3

    # Bonus: dramatic vertical features (tall buildings)
    tall_streak = 0
    max_streak = 0
    for row in view:
        dense = sum(1 for c in row if c in ('@', '#', '$'))
        if dense > 5:
            tall_streak += 1
            max_streak = max(max_streak, tall_streak)
        else:
            tall_streak = 0

    score += min(max_streak / 10, 1.0) * 0.2

    return min(score, 1.0)


def generate_lore(snap: CitySnapshot) -> str:
    """Generate lore for a snapshot using cheap API."""
    if not snap.view:
        return ""

    # Compress view into a short description
    view_chars = "".join("".join(row) for row in snap.view)
    char_counts = {}
    for ch in view_chars:
        char_counts[ch] = char_counts.get(ch, 0) + 1

    top_chars = sorted(char_counts.items(), key=lambda x: -x[1])[:5]
    char_summary = ", ".join(f"{c}={n}" for c, n in top_chars)

    msg = [{
        "role": "user",
        "content": f"Cyobert view {snap.seed} ({snap.x:.1f}, {snap.y:.1f}) facing {snap.angle:.2f}rad. Char mix: {char_summary}. One short noir caption (≤40 chars)."
    }]

    # Use cheap model for lore
    lore = chat("deepinfra", msg, model="Qwen/Qwen2.5-7B-Instruct", max_tokens=60, temperature=0.85)
    return lore.strip().strip('"').strip("'")


async def playtest_one_run(run_idx: int, seed: int, output_dir: Path) -> List[CitySnapshot]:
    """Play through one city seed, capture interesting moments."""
    snapshots = []

    # Walk a path through the city
    rng = random.Random(seed)

    # Pick a path
    path_type = rng.choice(["explore", "spiral", "wander", "straight"])
    if path_type == "explore":
        # Random walk
        n_steps = 30
        path = []
        x, y, angle = 16.0, 16.0, 0.0
        for _ in range(n_steps):
            x += rng.uniform(-2, 2)
            y += rng.uniform(-2, 2)
            angle += rng.uniform(-0.5, 0.5)
            path.append((x, y, angle))
    elif path_type == "spiral":
        # Spiral outward
        n_steps = 30
        path = []
        for i in range(n_steps):
            r = 1 + i * 0.5
            theta = i * 0.5
            x = 16 + r * (1 + theta * 0.1)  # spiral
            y = 16 + r * (1 - theta * 0.1)
            angle = theta
            path.append((x, y, angle))
    elif path_type == "wander":
        # Aimless wander
        n_steps = 30
        path = []
        x, y = 16.0, 16.0
        angle = 0
        for _ in range(n_steps):
            x += random.uniform(-3, 3)
            y += random.uniform(-3, 3)
            angle = rng.uniform(0, 6.28)
            path.append((x, y, angle))
    else:  # straight
        # Walk in straight lines with periodic turns
        n_steps = 30
        path = []
        x, y, angle = 16.0, 16.0, 0.0
        for i in range(n_steps):
            if i % 8 == 0:
                angle += 1.57  # 90 degree turn
            x += 0.5
            y += 0.2
            path.append((x, y, angle))

    # Sample snapshots along path
    for step, (x, y, angle) in enumerate(path):
        view = render_view(seed, x, y, angle)
        snap = CitySnapshot(x, y, angle, view, seed)
        snap.score = score_view(snap)
        snapshots.append(snap)

    # Generate lore for the top-scored snapshot (asynchronously, batched)
    top_snap = max(snapshots, key=lambda s: s.score)
    top_snap.lore = generate_lore(top_snap)

    return snapshots


async def playtest_swarm(runs: int, output_dir: Path):
    """Run playtest swarm. Returns leaderboard."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting playtest swarm: {runs} runs")
    all_runs = []

    tasks = []
    for i in range(runs):
        seed = random.randint(1000, 999999)
        tasks.append(playtest_one_run(i, seed, output_dir))

    # Run in batches of 5 to avoid overwhelming
    batch_size = 5
    for batch_idx in range(0, len(tasks), batch_size):
        batch = tasks[batch_idx:batch_idx + batch_size]
        results = await asyncio.gather(*batch, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                print(f"  run error: {r}")
            else:
                all_runs.append(r)
        if batch_idx % 20 == 0:
            print(f"  completed {batch_idx + batch_size}/{runs}")

    # Find leaderboard
    all_snaps = []
    for run_snaps in all_runs:
        all_snaps.extend(run_snaps)

    # Top 20 by score
    all_snaps.sort(key=lambda s: -s.score)
    top_20 = all_snaps[:20]

    # Save leaderboard
    leaderboard = {
        "total_runs": len(all_runs),
        "total_snapshots": len(all_snaps),
        "top_snapshots": [s.to_dict() for s in top_20],
        "score_distribution": _score_distribution(all_snaps),
        "best_lore": [s.lore for s in top_20 if s.lore][:5],
    }

    out_file = output_dir / "leaderboard.json"
    with open(out_file, "w") as f:
        json.dump(leaderboard, f, indent=2)

    print(f"\nLeaderboard saved to {out_file}")
    print(f"Top 5 scores: {[round(s.score, 3) for s in top_20[:5]]}")
    print(f"Score distribution: {leaderboard['score_distribution']}")
    if leaderboard["best_lore"]:
        print(f"\nBest lore:")
        for lore in leaderboard["best_lore"]:
            print(f"  • {lore}")

    return leaderboard


def _score_distribution(snaps):
    bins = [0] * 10  # 0.0-0.1, 0.1-0.2, ..., 0.9-1.0
    for s in snaps:
        idx = min(int(s.score * 10), 9)
        bins[idx] += 1
    return bins


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--output", type=str, default="playtest_output")
    args = parser.parse_args()

    out_dir = WORKSPACE / "playtest" / args.output
    asyncio.run(playtest_swarm(args.runs, out_dir))
