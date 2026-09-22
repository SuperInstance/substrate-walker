"""Composite lore v5 — top 10 seeds with multiple models."""

import json
import sys
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view


# TOP 10 ONLY
TOP_SEEDS = [1504276, 164836, 302238, 550551, 662290, 2184160, 69006, 326028, 728365, 995930]


def ask(provider, model, prompt, max_tokens=200):
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
        print(f"  [{provider}/{model}]: {e}")
    return ""


def get_lore(seed, voice):
    view, densities = render_view(seed, 16, 16, 0)
    view_text = "\n".join("".join(row) for row in view)
    
    prompts = {
        "structuralist": f"""Cyberpunk noir ARCHITECT. City cell:

{view_text}

ONE sentence (15-25 words). Focus on structure, geometry, and form. No preamble.""",
        "narrativist": f"""Cyberpunk noir CHARACTER. Walking:

{view_text}

ONE first-person sentence (15-25 words). Sensory detail. No preamble.""",
        "futurist": f"""Cyberpunk noir PROPHET. The city as living organism:

{view_text}

ONE prophetic sentence (15-25 words). Make the city breathe, dream, eat, or speak. No preamble.""",
    }
    return prompts[voice]


def main():
    print(f"Composite lore v5 — top 10 seeds × 3 voices × 2 models\n")
    
    all_results = []
    for i, seed in enumerate(TOP_SEEDS, 1):
        print(f"\n{i}. seed {seed}:")
        voices = {}
        for voice in ["structuralist", "narrativist", "futurist"]:
            prompt = get_lore(seed, voice)
            
            # Try Llama-8b
            lore1 = ask("deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", prompt, 100)
            # Try DeepSeek
            lore2 = ask("deepseek", "deepseek-chat", prompt, 100)
            
            # Pick the longer one
            lore = max([lore1, lore2], key=lambda x: len(x) if x else 0) if (lore1 or lore2) else ""
            if lore:
                lore = lore.strip().replace("\n", " ").strip('"').strip()
                voices[voice] = lore
                print(f"   [{voice:14}]: {lore[:70]}")
        
        if voices:
            all_results.append({"seed": seed, "voices": voices})
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v5.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\nSaved {len(all_results)} composite lores (top 10 × 3 voices × 2 models)")


if __name__ == "__main__":
    main()
