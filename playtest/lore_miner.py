"""
Lore Miner — generates thousands of lore snippets for the substrate-walker lore cache.

Each snippet:
- Different city position
- Different camera angle
- Multiple models in parallel
- Stored as JSON for fast loading

Use case: pre-generate lore so players get instant results on first visit.
"""

import os
import sys
import json
import asyncio
import random
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import parallel_chat


async def mine_one(seed: int, x: float, y: float, angle: float) -> Dict:
    """Generate lore for one position."""
    prompt = f"""Cyberpunk noir one-liner (≤40 chars) for ASCII city view at ({x:.1f}, {y:.1f}) angle {angle:.1f}, seed {seed}."""

    calls = [
        {"provider": "deepinfra", "messages": [{"role": "user", "content": prompt}],
         "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "max_tokens": 60, "temperature": 0.95},
        {"provider": "deepseek", "messages": [{"role": "user", "content": prompt}],
         "model": "deepseek-chat", "max_tokens": 60, "temperature": 0.95},
    ]
    results = await parallel_chat(calls)

    return {
        "seed": seed, "x": x, "y": y, "angle": angle,
        "lores": [r.strip().strip('"').strip("'") for r in results],
        "best_lore": max(results, key=len).strip().strip('"').strip("'"),
    }


async def main(n=200):
    print(f"Lore Miner — {n} snippets")
    rng = random.Random(42)

    tasks = []
    for _ in range(n):
        seed = rng.randint(1000, 999999)
        x = rng.uniform(0, 32)
        y = rng.uniform(0, 32)
        angle = rng.uniform(0, 6.28)
        tasks.append(mine_one(seed, x, y, angle))

    # Process in batches
    batch_size = 20
    results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        for r in batch_results:
            if not isinstance(r, Exception):
                results.append(r)
        if (i // batch_size) % 5 == 0:
            print(f"  completed {min(i + batch_size, len(tasks))}/{len(tasks)}")

    print(f"Generated {len(results)} lore snippets")

    # Save
    out_file = Path(__file__).parent / "lore_cache.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_file}")

    # Show samples
    print("\n=== Sample Lore ===")
    for r in results[:10]:
        print(f"  seed {r['seed']}: {r['best_lore'][:80]}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    asyncio.run(main(n))
