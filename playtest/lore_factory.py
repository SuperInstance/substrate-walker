"""
Lore Factory — bulk generation of lore snippets for the cache.

Generates 1000+ snippets across multiple models and styles.
"""

import os
import sys
import json
import asyncio
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import parallel_chat


PROMPT_TEMPLATES = [
    "Cyberpunk noir one-liner (≤40 chars) for ASCII city at ({x:.1f}, {y:.1f}), seed {seed}.",
    "Dark moody description (≤50 chars) of cyberpunk city at ({x:.1f}, {y:.1f}), seed {seed}.",
    "Atmospheric tagline (≤40 chars) for cyberpunk noir scene at ({x:.1f}, {y:.1f}).",
    "Spoken dialogue (≤40 chars) by a stranger in a rain-soaked cyberpunk alley, seed {seed}.",
    "Witness log entry (≤50 chars) for cell ({x:.1f}, {y:.1f}), seed {seed}.",
    "Canon quote (≤40 chars) about a cyberpunk city block, seed {seed}.",
    "Doctrinal note (≤50 chars) about cyberpunk substrate at ({x:.1f}, {y:.1f}), seed {seed}.",
    "Cyberpunk street name (≤30 chars), seed {seed}.",
    "Cyberpunk building name (≤30 chars), seed {seed}.",
    "Cyberpunk character name (≤30 chars), seed {seed}.",
]

MODELS = [
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "Qwen/Qwen2.5-7B-Instruct",
    "deepseek-chat",
    "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
    "google/gemma-3-27b-it",
]


async def make_one(seed, x, y, style_idx):
    prompt = PROMPT_TEMPLATES[style_idx % len(PROMPT_TEMPLATES)].format(seed=seed, x=x, y=y)

    calls = []
    for model in MODELS:
        provider = "deepseek" if "deepseek" in model else "deepinfra"
        calls.append({
            "provider": provider,
            "messages": [{"role": "user", "content": prompt}],
            "model": model,
            "max_tokens": 60,
            "temperature": 0.95,
        })

    results = await parallel_chat(calls)
    valid = [r.strip().strip('"').strip("'") for r in results
             if not r.startswith("[") and len(r.strip()) > 5]
    return {
        "seed": seed,
        "x": x,
        "y": y,
        "style_idx": style_idx,
        "lores": valid,
        "best_lore": max(valid, key=len) if valid else "",
    }


async def main(n=500):
    print(f"Lore Factory — generating {n} snippets")
    rng = random.Random(789)
    tasks = []
    for i in range(n):
        seed = rng.randint(1000, 999999)
        x = rng.uniform(0, 32)
        y = rng.uniform(0, 32)
        style_idx = rng.randint(0, len(PROMPT_TEMPLATES) - 1)
        tasks.append(make_one(seed, x, y, style_idx))

    # Process in batches of 10
    batch_size = 10
    results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        for r in batch_results:
            if not isinstance(r, Exception):
                results.append(r)
        if (i // batch_size) % 10 == 0:
            print(f"  completed {min(i + batch_size, len(tasks))}/{len(tasks)}")

    print(f"Generated {len(results)} lore snippets")

    # Build pack
    pack = {}
    for entry in results:
        lore = entry["best_lore"]
        # Clean preambles
        if lore.startswith("**") and lore.endswith("**"):
            lore = lore.strip("*").strip()
        if lore.startswith("*") and lore.endswith("*"):
            lore = lore.strip("*").strip()
        if "Here are" in lore or "Here's" in lore or "cyberpunk" in lore.lower()[:30]:
            # Try to find first quote
            quote_start = lore.find('"')
            if quote_start >= 0:
                quote_end = lore.find('"', quote_start + 1)
                if quote_end > quote_start:
                    lore = lore[quote_start + 1:quote_end]

        if 10 < len(lore) < 200:
            if entry["seed"] not in pack:
                pack[entry["seed"]] = lore

    print(f"Built pack with {len(pack)} unique lores")

    # Save
    out_file = Path(__file__).parent / "lore_pack_factory.json"
    with open(out_file, "w") as f:
        json.dump(pack, f, indent=2)
    print(f"Saved to {out_file}")

    # Show samples
    print("\n=== Sample Lore ===")
    for seed, lore in list(pack.items())[:15]:
        print(f"  seed {seed}: {lore[:80]}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    asyncio.run(main(n))
