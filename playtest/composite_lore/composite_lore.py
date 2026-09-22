"""Composite Lore Generation - 8 models in parallel per position, pick the best.

This is the lore equivalent of the honest composite scorer we built.
Each model has its own voice; the city speaks in the voice most 
canon-worthy to each position.
"""

import os
import sys
import json
import asyncio
import random
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import parallel_chat
from playtest_v2 import render_view, score_view, generate_lore


# 8 models - different voices
MODELS = [
    ("deepseek", "deepseek-chat"),  # DeepSeek V3 - narrative
    ("deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),  # Cheap/fast
    ("deepinfra", "Qwen/Qwen2.5-7B-Instruct"),  # Qwen 2.5 non-reasoning
    ("deepinfra", "google/gemma-3-27b-it"),  # Atmospheric
    ("deepinfra", "mistralai/Mistral-Small-3.2-24B-Instruct-2506"),  # Balanced
    ("deepinfra", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),  # Deep/Llama70
    ("deepseek", "deepseek-reasoner"),  # R1 reasoning
    ("deepinfra", "Qwen/Qwen2.5-72B-Instruct"),  # Qwen 72B
]

# Prompt styles for variety
PROMPTS = [
    "Cyberpunk noir one-liner (≤40 chars): seed {seed}, position ({x:.1f}, {y:.1f}).",
    "Atmospheric tagline (≤40 chars) for cyberpunk noir scene at ({x:.1f}, {y:.1f}).",
    "Spoken dialogue (≤40 chars) by a stranger in cyberpunk alley, seed {seed}.",
    "Cyberpunk character observation (≤40 chars) at ({x:.1f}, {y:.1f}), seed {seed}.",
    "Witness log entry (≤40 chars) for cell ({x:.1f}, {y:.1f}), seed {seed}.",
    "Cyberpunk noir propaganda broadcast (≤40 chars), seed {seed}.",
    "Old memory fragment (≤40 chars), a cyberpunk sentinel at ({x:.1f}, {y:.1f}):",
    "Building name + tagline (≤50 chars) for cell ({x:.1f}, {y:.1f}), seed {seed}.",
]


def score_lore(lore: str) -> float:
    """Score a lore line (composite of multiple criteria)."""
    if not lore or len(lore) < 5 or len(lore) > 200:
        return 0.0

    score = 0.0
    lore_lower = lore.lower()

    # Cyberpunk keywords (positive)
    cyber = sum(1 for w in ["rain", "neon", "shadow", "dark", "night", "lone",
                            "chrome", "blood", "alley", "sprawl", "cyber",
                            "noir", "corp", "matrix"] if w in lore_lower)
    score += cyber * 0.5

    # Avoid fillers
    if "here are" in lore_lower or "here's a" in lore_lower:
        score -= 2.0
    if "what would you" in lore_lower or "what do you" in lore_lower:
        score -= 1.0
    if lore.startswith("**") or lore.startswith("*"):
        score -= 1.0

    # Substrate words bonus
    sub = sum(1 for w in ["cell", "scar", "chain", "witness", "substrate",
                          "canon", "doctrine"] if w in lore_lower)
    score += sub * 1.0

    # Brevity bonus
    n = len(lore)
    if n <= 40:
        score += 3.0
    elif n <= 60:
        score += 2.0
    elif n <= 100:
        score += 1.0

    # Specificity
    if any(c.isupper() for c in lore):
        score += 0.5

    # Has punctuation
    if lore.endswith((".", "!", "?")):
        score += 0.5

    return max(0.0, score)


async def composite_lore(seed: int, x: float, y: float):
    """Generate lores from N models, score, return best."""
    view, densities = render_view(seed, x, y, 0)
    s = score_view(view, densities)

    # Generate using 8 different prompts (variety)
    all_lores = []
    for prompt in PROMPTS:
        prompt_text = prompt.format(seed=seed, x=x, y=y)
        calls = [
            {"provider": p, "messages": [{"role": "user", "content": prompt_text}],
             "model": m, "max_tokens": 80, "temperature": 0.95}
            for p, m in MODELS[:4]  # 4 models per prompt
        ]
        try:
            results = await parallel_chat(calls)
            for r in results:
                if not r.startswith("[") and len(r.strip()) > 5:
                    lore = r.strip().strip('"').strip("'")
                    if "Here are" in lore or "Here's" in lore or "cyberpunk noir" in lore.lower()[:30]:
                        quote_start = lore.find('"')
                        if quote_start >= 0:
                            quote_end = lore.find('"', quote_start + 1)
                            if quote_end > quote_start:
                                lore = lore[quote_start + 1:quote_end]
                    all_lores.append((lore, prompt_text))
        except Exception as e:
            continue

    # Dedupe
    seen = set()
    unique = [(l, p) for l, p in all_lores if l not in seen and not seen.add(l)]

    # Score each
    scored = [(lore, prompt, score_lore(lore)) for lore, prompt in unique]
    scored.sort(key=lambda x: -x[2])

    return {
        "seed": seed,
        "x": x, "y": y,
        "view_score": s,
        "best_lore": scored[0][0] if scored else "",
        "best_lore_score": scored[0][2] if scored else 0,
        "top_3_lores": [l for l, _, _ in scored[:3]],
        "total_lores": len(scored),
    }


async def main(n_seeds=30):
    print(f"Composite Lore Generation — {n_seeds} seeds × 8 prompts × 4 models")
    
    # Use top seeds
    seeds = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))
    top_seeds = [m["seed"] for m in seeds[:n_seeds]]
    
    # Add some new seeds
    rng = random.Random(42)
    top_seeds.extend([rng.randint(100000, 999999) for _ in range(10)])
    
    results = []
    for i, seed in enumerate(top_seeds):
        # Try several positions, pick the best
        best = {"best_lore_score": 0}
        for x in range(8, 28, 8):
            for y in range(8, 28, 8):
                r = await composite_lore(seed, x, y)
                if r["best_lore_score"] > best.get("best_lore_score", 0):
                    best = r
        
        results.append(best)
        print(f"  [{i+1}/{len(top_seeds)}] seed {seed}: lore_score={best.get('best_lore_score', 0):.2f}")
        print(f"      '{best.get('best_lore', '')[:80]}'")
    
    results.sort(key=lambda r: -r.get("best_lore_score", 0))
    
    print(f"\n=== Top 10 by composite lore score ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:2}. seed {r['seed']:7} lore={r['best_lore_score']:.2f} - {r['best_lore'][:80]}")
    
    out_file = Path(__file__).parent / "composite_lore_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} to {out_file}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    asyncio.run(main(n))
