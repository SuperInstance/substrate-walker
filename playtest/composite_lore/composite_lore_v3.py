"""Composite lore v3 — focus on top-tier seeds with multi-voice."""

import json
import sys
import os
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view


# Top 20 seeds from new findings
TOP_SEEDS = [
    1504276,  # figurate best
    164836,   # perfect square best
    302238, 550551, 662290, 2184160,  # tied at 0.8667
    69006, 326028,  # triangular best
    310249, 9901, 690561, 7001, 18381, 4073,  # original top
    163836, 800330, 728365, 995930,  # more top
]


def ask_model(prompt, model="llama3-8b-instruct"):
    """Get a lore from a specific model."""
    try:
        result = chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=200,
        )
        if result and "content" in result:
            return result["content"]
    except Exception as e:
        print(f"  error: {e}")
    return ""


def composite(seed, score):
    """Build composite lore for a seed."""
    view, densities = render_view(seed, 16, 16, 0)
    view_text = "\n".join("".join(row) for row in view)
    
    prompt = f"""You are a cyberpunk noir game narrator. A player just walked through a city cell with the following ASCII density pattern:

```
{view_text}
```

The cell has score {score:.4f} (out of 1.0, higher is better).
Seed: {seed}

Write a single opening line (one sentence, 15-25 words) for this location. Set tone, place, and threat. No preamble."""
    
    voices = []
    models = ["llama3-8b-instruct", "gemma-3-27b-it", "mistral-small-3.2-24b-instruct"]
    for model in models:
        lore = ask_model(prompt, model)
        if lore:
            voices.append({"model": model, "lore": lore})
    
    if not voices:
        return None
    
    # Combine: pick the best 2 voices and concatenate
    print(f"  seed {seed:9}:")
    for v in voices:
        print(f"    [{v['model']}]: {v['lore'][:80]}")
    
    return voices


def main():
    print("Composite lore v3 — multi-voice on top 20 seeds")
    
    all_results = []
    for seed in TOP_SEEDS:
        voices = composite(seed, 0.866)
        if voices:
            all_results.append({"seed": seed, "voices": voices})
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v3.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nSaved {len(all_results)} composite lores")


if __name__ == "__main__":
    main()
