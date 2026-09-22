"""Composite Lore v2 - better scoring, focused on canon-worthy lines."""

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


# Models in 4 voices
MODELS_BY_VOICE = {
    "deep": [
        ("deepseek", "deepseek-chat"),
        ("deepinfra", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
        ("deepinfra", "Qwen/Qwen2.5-72B-Instruct"),
    ],
    "fast": [
        ("deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
        ("deepinfra", "Qwen/Qwen2.5-7B-Instruct"),
    ],
    "atmospheric": [
        ("deepinfra", "google/gemma-3-27b-it"),
        ("deepinfra", "mistralai/Mistral-Small-3.2-24B-Instruct-2506"),
    ],
}


def is_canon_worthy(lore: str) -> float:
    """Score a lore 0-10."""
    if not lore or len(lore) < 5 or len(lore) > 150:
        return 0.0

    score = 5.0  # Base
    lore_lower = lore.lower()

    # Atmospheric words (+0.5 each, max +3)
    atmos = sum(1 for w in ["rain", "neon", "shadow", "dark", "night", "lone",
                            "chrome", "alley", "cyber", "noir", "sprawl",
                            "femme", "blood", "neon-drenched", "rain-soaked"]
               if w in lore_lower)
    score += min(3.0, atmos * 0.5)

    # Penalize filler (-3)
    if "here are" in lore_lower or "here's" in lore_lower:
        score -= 3.0
    if lore.startswith("**"):
        score -= 1.5
    if lore.startswith("*"):
        score -= 0.5
    if "what would you" in lore_lower:
        score -= 1.0

    # Brevity (+1 if ≤40, +0.5 if ≤60)
    n = len(lore)
    if n <= 40:
        score += 1.0
    elif n <= 60:
        score += 0.5

    # Substrate doctrine (+1 if has substrate words)
    if any(w in lore_lower for w in ["cell", "scar", "chain", "witness", "substrate"]):
        score += 1.0

    # Has specific location/noun (+0.5)
    if any(w in lore_lower for w in ["neo-tokyo", "new", "sector", "sprawl", "street"]):
        score += 0.5

    # Punctuation bonus
    if lore.endswith((".", "!", "?")):
        score += 0.3

    return max(0.0, min(10.0, score))


async def composite_lore_one(seed: int):
    """Generate composite lores for one seed."""
    # Find best position first
    best_score = 0
    best_x, best_y = 16, 16
    for x in range(8, 28, 4):
        for y in range(8, 28, 4):
            view, densities = render_view(seed, x, y, 0)
            score = score_view(view, densities)
            if score > best_score:
                best_score = score
                best_x, best_y = x, y

    # Generate lores from all voices
    all_lores = []
    for voice_name, models in MODELS_BY_VOICE.items():
        prompt = f"Cyberpunk noir one-liner (≤50 chars) for ASCII city at ({best_x}, {best_y}), seed {seed}."
        calls = [
            {"provider": p, "messages": [{"role": "user", "content": prompt}],
             "model": m, "max_tokens": 60, "temperature": 0.95}
            for p, m in models
        ]
        try:
            results = await parallel_chat(calls)
            for r in results:
                if not r.startswith("[") and len(r.strip()) > 5:
                    lore = r.strip().strip('"').strip("'")
                    # Clean preambles
                    if "Here are" in lore or "Here's" in lore or "cyberpunk" in lore.lower()[:30]:
                        quote_start = lore.find('"')
                        if quote_start >= 0:
                            quote_end = lore.find('"', quote_start + 1)
                            if quote_end > quote_start:
                                lore = lore[quote_start + 1:quote_end]
                    all_lores.append((lore, voice_name))
        except:
            continue

    # Score each
    scored = [(lore, voice, is_canon_worthy(lore)) for lore, voice in all_lores]

    # Dedupe
    seen = set()
    unique = []
    for entry in scored:
        if entry[0] not in seen and entry[0].strip():
            seen.add(entry[0])
            unique.append(entry)

    unique.sort(key=lambda x: -x[2])
    return {
        "seed": seed,
        "best_x": best_x,
        "best_y": best_y,
        "view_score": best_score,
        "top_lore": unique[0][0] if unique else "",
        "top_lore_score": unique[0][2] if unique else 0,
        "top_lore_voice": unique[0][1] if unique else "",
        "n_lores": len(unique),
        "all_lores": [(l, v, s) for l, v, s in unique[:8]],
    }


async def main(n_seeds=40):
    print(f"Composite Lore v2 — {n_seeds} seeds × multiple voices")
    
    # Top seeds + new
    gm = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))
    seeds = [m["seed"] for m in gm[:50] if m.get("lore")]
    rng = random.Random(42)
    seeds.extend([rng.randint(100000, 999999) for _ in range(20)])
    seeds = list(set(seeds))[:n_seeds]
    
    results = []
    for i, seed in enumerate(seeds, 1):
        r = await composite_lore_one(seed)
        results.append(r)
        if i % 5 == 0:
            print(f"  [{i}/{len(seeds)}] {seed}: lore_score={r['top_lore_score']:.1f} - {r['top_lore'][:60]}")
    
    results.sort(key=lambda r: -r["top_lore_score"])
    
    print(f"\n=== Top 10 ===")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:2}. seed {r['seed']:7} score={r['top_lore_score']:.1f} ({r['top_lore_voice']}) - {r['top_lore'][:80]}")
    
    out_file = Path(__file__).parent / "composite_lore_v2_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} to {out_file}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    asyncio.run(main(n))
