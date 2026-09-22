"""Composite lore v3 — multi-voice on top 20 seeds (fixed API call)."""

import json
import sys
import os
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
import multi_api as ma
from multi_api import chat
from playtest_v2 import render_view, score_view


TOP_SEEDS = [
    1504276, 164836, 302238, 550551, 662290, 2184160, 69006, 326028,
    310249, 9901, 690561, 7001, 18381, 4073, 163836, 800330, 728365, 995930
]


def ask_model(prompt, model="llama3-8b-instruct", provider="deepinfra"):
    """Get a lore from a specific model."""
    try:
        result = chat(
            provider=provider,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        if result and "content" in result:
            return result["content"]
        if isinstance(result, str):
            return result
    except Exception as e:
        print(f"  error: {e}")
    return ""


def composite(seed):
    view, densities = render_view(seed, 16, 16, 0)
    view_text = "\n".join("".join(row) for row in view)
    
    prompt = f"""Cyberpunk noir game narrator. A player walks through a city cell with this ASCII density pattern:

```
{view_text}
```

Write ONE opening line (15-25 words). Set tone, place, threat. No preamble."""
    
    voices = []
    models_with_provider = [
        ("deepinfra", "llama3-8b-instruct"),
        ("deepinfra", "gemma-3-27b-it"),
        ("deepinfra", "mistral-small-3.2-24b-instruct"),
    ]
    for provider, model in models_with_provider:
        lore = ask_model(prompt, model, provider)
        if lore:
            voices.append({"provider": provider, "model": model, "lore": lore})
    
    if not voices:
        return None
    
    print(f"  seed {seed:9}:")
    for v in voices:
        lore_short = v['lore'][:80].replace('\n', ' ')
        print(f"    [{v['model']:25}]: {lore_short}")
    
    return voices


def main():
    print("Composite lore v3 — multi-voice on top 18 seeds")
    
    all_results = []
    for seed in TOP_SEEDS:
        voices = composite(seed)
        if voices:
            all_results.append({"seed": seed, "voices": voices})
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v3.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nSaved {len(all_results)} composite lores")


if __name__ == "__main__":
    main()
