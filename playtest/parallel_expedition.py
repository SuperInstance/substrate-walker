"""
Parallel Expedition — fish for gold with 4 parallel API calls at once
Sends 4 lore generation requests in parallel for the same view
Then composites them into a richer output
"""

import os
import sys
import json
import asyncio
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view


async def expedition_parallel(seed, x, y, angle):
    """One expedition with 4 parallel lore calls."""
    view, densities = render_view(seed, x, y, angle)
    score = score_view(view, densities)

    # Compress view for prompt
    view_chars = set()
    for row in view:
        view_chars.update(c for c in row if c not in ' _')
    char_summary = ', '.join(sorted(view_chars))

    prompt = f"""Cyberpunk noir. Player sees ASCII view at ({x:.1f}, {y:.1f}) facing {angle:.2f}rad in city seed {seed}. Chars visible: {char_summary}.

One short noir caption (≤40 chars):"""

    # Parallel calls with different models for variety
    calls = [
        {"provider": "deepinfra", "messages": [{"role": "user", "content": prompt}],
         "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "max_tokens": 60, "temperature": 0.9},
        {"provider": "deepseek", "messages": [{"role": "user", "content": prompt}],
         "model": "deepseek-chat", "max_tokens": 60, "temperature": 0.9},
        {"provider": "deepinfra", "messages": [{"role": "user", "content": prompt}],
         "model": "google/gemma-3-27b-it", "max_tokens": 60, "temperature": 0.9},
        {"provider": "deepinfra", "messages": [{"role": "user", "content": prompt}],
         "model": "mistralai/Mistral-Small-3.2-24B-Instruct-2506", "max_tokens": 60, "temperature": 0.9},
    ]

    results = await parallel_chat(calls)

    # Pick the best (longest, most descriptive)
    best_lore = max(results, key=lambda r: len(r.strip())) if results else ""

    return {
        "seed": seed, "x": x, "y": y, "angle": angle,
        "score": score,
        "lore": best_lore.strip().strip('"').strip("'"),
        "all_lores": results,
    }


async def main(n_seeds: int = 50):
    print(f"Parallel Expedition — {n_seeds} seeds, 4 parallel models each")

    rng = random.Random(42)
    tasks = []
    for _ in range(n_seeds):
        seed = rng.randint(1000, 999999)
        x = rng.uniform(0, 32)
        y = rng.uniform(0, 32)
        angle = rng.uniform(0, 6.28)
        tasks.append(expedition_parallel(seed, x, y, angle))

    # Process in batches of 10 to avoid overwhelming
    batch_size = 10
    results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        for r in batch_results:
            if isinstance(r, Exception):
                print(f"  Error: {r}")
            else:
                results.append(r)
        print(f"  completed {min(i + batch_size, len(tasks))}/{len(tasks)}")

    # Sort by score
    results.sort(key=lambda r: -r["score"])

    print(f"\n=== Top 10 Expeditions ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i}. seed={r['seed']} ({r['x']:.1f}, {r['y']:.1f}) score={r['score']:.3f}")
        print(f"   lore: {r['lore']}")

    # Save
    out_file = Path(__file__).parent / "parallel_expedition_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    asyncio.run(main(n))
