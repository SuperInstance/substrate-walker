"""Deep Lore Mining - uses unusual prompt styles to find non-obvious patterns."""

import os
import sys
import json
import asyncio
import random
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view


# UNUSUAL prompt styles
PROMPT_STYLES = [
    # Poetic
    "Write one line of cyberpunk haiku (5-7-5 syllable structure): {seed}",
    # Philosophical
    "One sentence in the voice of a cyberpunk philosopher: '{lore}' → rephrase as koan about seed {seed}",
    # Dialogue
    "Last words spoken by a stranger in a rain-soaked alley at ({x:.1f}, {y:.1f}), seed {seed}:",
    # Technical
    "Debug log line for cyberpunk simulation: seed {seed} pos ({x:.1f}, {y:.1f}) sensors:",
    # Witness log
    "Canon witness entry for substrate cell ({x:.1f}, {y:.1f}) seed {seed}, ≤40 chars:",
    # Memory
    "Memory fragment from a cyberpunk android about neighborhood seed {seed}:",
    # Future
    "Prophecy for cyberpunk city block seed {seed} in year 2087:",
    # Black market
    "Black market notification for item delivery at ({x:.1f}, {y:.1f}), seed {seed}:",
    # Police dispatch
    "Police dispatch call: code {seed} at ({x:.1f}, {y:.1f}), situation:",
    # News headline
    "News headline about cyberpunk city block seed {seed}:",
    # Old letter
    "Last sentence of a letter found in cyberpunk cell ({x:.1f}, {y:.1f}) seed {seed}:",
    # Advertisement
    "Cyberpunk neon advertisement slogan for location ({x:.1f}, {y:.1f}) seed {seed}:",
]

MODELS = [
    ("deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
    ("deepinfra", "Qwen/Qwen2.5-7B-Instruct"),
    ("deepseek", "deepseek-chat"),
]


async def deep_explore(seed, x, y, style_idx, prompt_template):
    """Try one prompt style with one seed/position."""
    view, densities = render_view(seed, x, y, 0)
    score = score_view(view, densities)

    prompt = prompt_template.format(seed=seed, x=x, y=y, lore="")

    try:
        result = chat(MODELS[0][0],
                      [{"role": "user", "content": prompt}],
                      model=MODELS[0][1],
                      max_tokens=80, temperature=0.95)
        result = result.strip().strip('"').strip("'")
        # Cleanup
        if "Here are" in result or "Here's" in result or "cyberpunk" in result.lower()[:30]:
            quote_start = result.find('"')
            if quote_start >= 0:
                quote_end = result.find('"', quote_start + 1)
                if quote_end > quote_start:
                    result = result[quote_start + 1:quote_end]
        return {
            "seed": seed,
            "x": x, "y": y,
            "style_idx": style_idx,
            "style_name": ["haiku", "philosopher", "dialogue", "debug", "witness",
                           "memory", "prophecy", "market", "police", "news",
                           "letter", "ad"][style_idx] if style_idx < 12 else f"style_{style_idx}",
            "score": score,
            "lore": result,
        }
    except Exception as e:
        return None


async def main(n_seeds=300):
    print(f"Deep Lore Mining — {n_seeds} seeds × {len(PROMPT_STYLES)} styles (12)")
    rng = random.Random(42)
    tasks = []
    for i in range(n_seeds):
        seed = rng.randint(1000, 999999)
        for style_idx in range(len(PROMPT_STYLES)):
            x = rng.uniform(0, 32)
            y = rng.uniform(0, 32)
            tasks.append(deep_explore(seed, x, y, style_idx, PROMPT_STYLES[style_idx]))

    # Process in batches
    batch_size = 20
    results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        for r in batch_results:
            if r and not isinstance(r, Exception):
                results.append(r)
        if (i // batch_size) % 5 == 0:
            print(f"  completed {min(i + batch_size, len(tasks))}/{len(tasks)}, valid: {len(results)}")

    print(f"\nTotal valid: {len(results)}")
    
    # Group by style
    by_style = {}
    for r in results:
        style = r.get("style_name", "unknown")
        if style not in by_style:
            by_style[style] = []
        by_style[style].append(r)

    print(f"\n=== Best per style ===")
    for style, items in by_style.items():
        # Dedupe by lore
        seen = set()
        unique = [x for x in items if x["lore"] not in seen and not seen.add(x["lore"])]
        unique.sort(key=lambda x: -len(x["lore"]))
        print(f"\n{style} ({len(unique)} unique):")
        for x in unique[:3]:
            print(f"  {x['lore'][:80]}")

    out_file = Path(__file__).parent / "deep_lore_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} to {out_file}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    asyncio.run(main(n))
