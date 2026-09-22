"""
Composite Lore Generator
Uses 3 different models to generate complementary lore perspectives,
then combines them into a richer single output.

Like the JEV composite voting but for creative generation.
"""

import os
import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat, parallel_chat

CONTEXT_PROMPT = """You are generating lore for a cyberpunk noir 3D ASCII city game.

Snapshot:
- Seed: {seed}
- Position: ({x:.1f}, {y:.1f})
- Angle: {angle:.2f} rad
- Score: {score:.3f}

Three perspectives to generate:

1. **VISUAL** (meta-llama-3.1-8b): Describe what you see in 1 short sentence.
2. **NARRATIVE** (deepseek-chat): Tell what's happening in 1 short sentence.
3. **CELLULAR** (gemma-3-27b): Describe the substrate cell quality in 1 short sentence.

Each returns their perspective. We combine them into a composite lore line.
"""


async def composite_lore(snapshot: dict) -> str:
    """Generate composite lore from 3 different models."""
    prompt = CONTEXT_PROMPT.format(
        seed=snapshot.get("seed", 0),
        x=snapshot.get("x", 0),
        y=snapshot.get("y", 0),
        angle=snapshot.get("angle", 0),
        score=snapshot.get("score", 0),
    )

    calls = [
        {"provider": "deepinfra", "messages": [{"role": "user", "content": prompt}],
         "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "max_tokens": 60, "temperature": 0.85},
        {"provider": "deepseek", "messages": [{"role": "user", "content": prompt}],
         "model": "deepseek-chat", "max_tokens": 60, "temperature": 0.85},
        {"provider": "deepinfra", "messages": [{"role": "user", "content": prompt}],
         "model": "google/gemma-3-27b-it", "max_tokens": 60, "temperature": 0.85},
    ]

    results = await parallel_chat(calls)
    return combine_perspectives(results)


def combine_perspectives(perspectives: list) -> str:
    """Combine 3 perspectives into one composite lore."""
    # Clean up
    cleaned = []
    for p in perspectives:
        if not p.startswith("["):
            cleaned.append(p.strip().strip('"').strip("'"))
        else:
            cleaned.append("(failed)")

    # Find best parts
    if len(cleaned) >= 3:
        # Take first 15 chars of each
        composite = f"{cleaned[0][:20]} | {cleaned[1][:20]} | {cleaned[2][:20]}"
    else:
        composite = " | ".join(cleaned)

    return composite[:80]


async def demo():
    """Demo: generate composite lore for 5 mock snapshots."""
    snapshots = [
        {"seed": 294689, "x": 16.9, "y": 11.1, "angle": 0.0, "score": 0.859},
        {"seed": 426053, "x": 8.0, "y": 16.0, "angle": 1.5, "score": 0.857},
        {"seed": 269010, "x": 24.0, "y": 8.0, "angle": 3.0, "score": 0.851},
        {"seed": 555555, "x": 12.0, "y": 20.0, "angle": 0.5, "score": 0.843},
        {"seed": 999999, "x": 4.0, "y": 28.0, "angle": 2.0, "score": 0.835},
    ]

    print("=== Composite Lore Demo ===")
    for snap in snapshots:
        lore = await composite_lore(snap)
        print(f"\nSeed {snap['seed']} @ ({snap['x']:.1f}, {snap['y']:.1f}):")
        print(f"  → {lore}")


if __name__ == "__main__":
    asyncio.run(demo())
