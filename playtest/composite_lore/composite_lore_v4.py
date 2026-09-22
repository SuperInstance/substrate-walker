"""Composite lore v4 — multi-model + multi-prompt."""

import json
import sys
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view


# Top 30 from updated canon
TOP_SEEDS = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))[:30]
TOP_SEED_IDS = [m["seed"] for m in TOP_SEEDS]


def ask_model(prompt, provider="deepinfra", model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", max_tokens=200):
    try:
        result = chat(
            provider=provider,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        if isinstance(result, dict):
            return result.get("content", "")
        if isinstance(result, str):
            return result
    except Exception as e:
        print(f"  [{provider}/{model}]: ERROR {e}")
    return ""


def composite_seed(seed):
    view, densities = render_view(seed, 16, 16, 0)
    view_text = "\n".join("".join(row) for row in view)
    
    prompts = {
        "structuralist": f"""Cyberpunk noir NARRATOR. City cell:

```
{view_text}
```

ONE sentence (15-25 words). Focus on architecture and form. No preamble.""",
        "narrativist": f"""Cyberpunk noir CHARACTER POV. Walking through:

```
{view_text}
```

ONE sensory sentence (15-25 words). Use 'I' or character mood. No preamble.""",
        "futurist": f"""Cyberpunk noir PHILOSOPHER. City as living being:

```
{view_text}
```

ONE prophecy (15-25 words). Make the city dream, eat, speak. No preamble.""",
    }
    
    voices = {}
    
    # Use each prompt with one model
    for voice, prompt in prompts.items():
        # Try DeepInfra first
        lore = ask_model(prompt, "deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", 200)
        if not lore:
            # Fall back to DeepSeek
            lore = ask_model(prompt, "deepseek", "deepseek-chat", 200)
        
        if lore:
            # Clean up
            lore = lore.strip().replace("\n", " ")
            if lore.startswith('"') and lore.endswith('"'):
                lore = lore[1:-1]
            voices[voice] = lore
    
    return voices


def main():
    print(f"Composite lore v4 — multi-voice on top 30 canon seeds\n")
    
    all_results = []
    for i, seed in enumerate(TOP_SEED_IDS, 1):
        print(f"\n{i}. seed {seed}:")
        voices = composite_seed(seed)
        if voices:
            for v, l in voices.items():
                print(f"   [{v:14}]: {l[:70]}")
            all_results.append({"seed": seed, "voices": voices})
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v4.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nSaved {len(all_results)} composite lores")


if __name__ == "__main__":
    main()
