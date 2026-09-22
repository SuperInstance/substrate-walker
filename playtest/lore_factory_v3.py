"""Lore Factory v3 - sequential, saves to v3 file."""

import os
import sys
import json
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat

PROMPT_TEMPLATES = [
    "Cyberpunk noir one-liner (≤40 chars) for ASCII city at ({x:.1f}, {y:.1f}), seed {seed}.",
    "Atmospheric tagline (≤40 chars) for cyberpunk noir scene at ({x:.1f}, {y:.1f}).",
    "Witness log entry (≤50 chars) for cell ({x:.1f}, {y:.1f}), seed {seed}.",
    "Cyberpunk street name (≤30 chars), seed {seed}.",
    "Cyberpunk building name (≤30 chars), seed {seed}.",
    "Cyberpunk character name (≤30 chars), seed {seed}.",
    "Cyberpunk district name (≤30 chars), seed {seed}.",
    "Spoken dialogue (≤40 chars) by a stranger in cyberpunk alley, seed {seed}.",
]


def make_one(seed, x, y, style_idx):
    prompt = PROMPT_TEMPLATES[style_idx % len(PROMPT_TEMPLATES)].format(seed=seed, x=x, y=y)
    try:
        lore = chat("deepseek", [{"role": "user", "content": prompt}], model="deepseek-chat", max_tokens=60, temperature=0.95)
        lore = lore.strip().strip('"').strip("'")
        if "Here are" in lore or "Here's" in lore or "cyberpunk noir" in lore.lower()[:30]:
            quote_start = lore.find('"')
            if quote_start >= 0:
                quote_end = lore.find('"', quote_start + 1)
                if quote_end > quote_start:
                    lore = lore[quote_start + 1:quote_end]
        if 10 < len(lore) < 200:
            return lore
    except Exception as e:
        pass
    return None


def main(n=300):
    print(f"Lore Factory v3 — {n} snippets")
    rng = random.Random(101)
    pack = {}
    success = 0
    for i in range(n):
        seed = rng.randint(1000, 999999)
        x = rng.uniform(0, 32)
        y = rng.uniform(0, 32)
        style_idx = rng.randint(0, len(PROMPT_TEMPLATES) - 1)
        lore = make_one(seed, x, y, style_idx)
        if lore:
            if seed not in pack:
                pack[seed] = lore
                success += 1
        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{n}, pack size: {success}")

    print(f"\nBuilt pack with {len(pack)} unique lores")
    out_file = Path(__file__).parent / "lore_pack_v3.json"
    with open(out_file, "w") as f:
        json.dump(pack, f, indent=2)
    print(f"Saved to {out_file}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    main(n)
