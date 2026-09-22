"""Parallel expedition V2 - fish for gold with 8 models in parallel per request"""

import os
import sys
import json
import asyncio
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view

MODELS = [
    ("deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
    ("deepinfra", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
    ("deepinfra", "google/gemma-3-27b-it"),
    ("deepinfra", "mistralai/Mistral-Small-3.2-24B-Instruct-2506"),
    ("deepinfra", "google/gemini-3.1-flash-lite"),
    ("deepseek", "deepseek-chat"),
    ("deepinfra", "Qwen/Qwen2.5-72B-Instruct"),
    ("deepinfra", "Qwen/Qwen2.5-7B-Instruct"),
]


async def expedition(seed, x, y, angle):
    view, densities = render_view(seed, x, y, angle)
    score = score_view(view, densities)

    chars = set()
    for row in view:
        chars.update(c for c in row if c not in ' _')
    char_summary = ', '.join(sorted(chars))

    prompt = f"Cyberpunk noir one-liner (≤40 chars): seed {seed}, pos ({x:.1f}, {y:.1f}), chars: {char_summary}"

    calls = [
        {"provider": p, "messages": [{"role": "user", "content": prompt}],
         "model": m, "max_tokens": 60, "temperature": 0.9}
        for p, m in MODELS
    ]

    results = await parallel_chat(calls)
    valid = [r for r in results if not r.startswith("[") and len(r.strip()) > 5]

    best = max(valid, key=len) if valid else ""
    return {
        "seed": seed, "x": x, "y": y, "angle": angle,
        "score": score,
        "lore": best.strip().strip('"').strip("'"),
        "n_lores": len(valid),
    }


async def main(n=100):
    print(f"Parallel Expedition BIG — {n} expeditions, {len(MODELS)} models each")
    rng = random.Random(456)
    tasks = []
    for _ in range(n):
        seed = rng.randint(1000, 999999)
        x = rng.uniform(0, 32)
        y = rng.uniform(0, 32)
        angle = rng.uniform(0, 6.28)
        tasks.append(expedition(seed, x, y, angle))

    # Process in batches of 5 to avoid overwhelming
    batch_size = 5
    results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        for r in batch_results:
            if not isinstance(r, Exception):
                results.append(r)
        if (i // batch_size) % 4 == 0:
            print(f"  completed {min(i + batch_size, len(tasks))}/{len(tasks)}")

    results.sort(key=lambda r: -r["score"])
    print(f"\n=== Top 15 ===")
    for i, r in enumerate(results[:15], 1):
        print(f"{i:2}. seed={r['seed']:6} score={r['score']:.3f} (n_lores={r['n_lores']})")
        print(f"    lore: {r['lore'][:80]}")

    out_file = Path(__file__).parent / "parallel_expedition_big_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    asyncio.run(main(n))
