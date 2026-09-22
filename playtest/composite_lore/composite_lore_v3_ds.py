"""Composite lore v3 with DeepSeek — multi-voice."""

import json
import sys
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view


TOP_SEEDS = [
    1504276, 164836, 302238, 550551, 662290, 2184160, 69006, 326028,
    310249, 9901, 690561, 7001, 18381, 4073, 163836, 800330, 728365, 995930
]


def ask_deepseek(prompt, model="deepseek-chat"):
    try:
        result = chat(
            provider="deepseek",
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        if isinstance(result, dict):
            return result.get("content", "")
        return result
    except Exception as e:
        print(f"  error: {e}")
    return ""


def multi_voice_composite(seed):
    """Get multiple voices from same seed."""
    view, densities = render_view(seed, 16, 16, 0)
    view_text = "\n".join("".join(row) for row in view)
    
    # Different prompts for different voices
    prompts = {
        "structuralist": f"""You are a structuralist narrator. A cyberpunk walker sees this city cell:

```
{view_text}
```

Output ONE sentence (15-25 words) emphasizing the architectural and structural qualities. No preamble.""",
        "narrativist": f"""You are a character-focused narrator. A cyberpunk walker approaches this scene:

```
{view_text}
```

Write ONE evocative first-person sentence (15-25 words) capturing a single sensory detail and the character's mood. No preamble.""",
        "futurist": f"""You are a futuristic philosopher-narrator. A walker sees this dystopian cell:

```
{view_text}
```

Write ONE prophetic sentence (15-25 words) about the city's deeper nature. No preamble.""",
    }
    
    voices = {}
    for voice, prompt in prompts.items():
        lore = ask_deepseek(prompt, "deepseek-chat")
        if lore:
            voices[voice] = lore
    
    if not voices:
        return None
    
    print(f"\n  seed {seed:9}:")
    for v, l in voices.items():
        print(f"    [{v:14}]: {l[:80].replace(chr(10), ' ')}")
    
    return voices


def main():
    print("Composite lore v3 — DeepSeek multi-voice on top 18 seeds")
    
    all_results = []
    for seed in TOP_SEEDS:
        voices = multi_voice_composite(seed)
        if voices:
            all_results.append({"seed": seed, "voices": voices})
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v3.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nSaved {len(all_results)} composite lores")


if __name__ == "__main__":
    main()
