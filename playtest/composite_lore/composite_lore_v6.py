"""Composite lore v6 — top 50 seeds × 7 working models, multi-voice."""
import json, sys, time
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view

TOP_SEEDS = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))[:50]
TOP_SEED_IDS = [m["seed"] for m in TOP_SEEDS]

MODELS = [
    ("deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "Llama-8b"),
    ("deepinfra", "google/gemma-3-27b-it", "Gemma-3-27b"),
    ("deepinfra", "mistralai/Mistral-Small-3.2-24B-Instruct-2506", "Mistral-Small"),
    ("deepseek", "deepseek-chat", "DeepSeek"),
]

def ask(provider, model, prompt, max_tokens=180):
    try:
        result = chat(
            provider=provider,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        if isinstance(result, dict): return result.get("content", "")
        if isinstance(result, str): return result
    except Exception as e:
        print(f"  [err {model[:20]}]: {e}")
    return ""

def best(l1, l2):
    return max([l1, l2], key=lambda x: len(x) if x else 0) if (l1 or l2) else ""

def generate_for_seed(seed):
    view, densities = render_view(seed, 16, 16, 0)
    view_text = "\n".join("".join(row) for row in view)
    
    prompts = {
        "structuralist": f"""Cyberpunk noir ARCHITECT. City cell pattern:

{view_text}

ONE sentence (15-25 words). Focus on architecture, geometry, structure. No preamble.""",
        "narrativist": f"""Cyberpunk noir CHARACTER walking through:

{view_text}

ONE first-person sentence (15-25 words). Use 'I' or sensory detail. No preamble.""",
        "futurist": f"""Cyberpunk noir PROPHET. The city as living organism:

{view_text}

ONE prophetic sentence (15-25 words). Make the city breathe, dream, eat, or speak. No preamble.""",
    }
    
    voices = {}
    for voice, prompt in prompts.items():
        # Try each model, take the longest non-empty result
        lores = []
        for provider, model, _ in MODELS:
            lore = ask(provider, model, prompt, 180)
            if lore and len(lore) > 20:
                lore = lore.strip().replace("\n", " ").strip('"').strip()
                lores.append(lore)
        if lores:
            voices[voice] = max(lores, key=len)
    
    return voices

def main():
    print(f"Composite lore v6 — top 50 × 4 models × 3 voices\n")
    
    all_results = []
    for i, seed in enumerate(TOP_SEED_IDS, 1):
        print(f"\n{i}. seed {seed}:", end='', flush=True)
        voices = generate_for_seed(seed)
        if voices:
            all_results.append({"seed": seed, "voices": voices})
            print(f" {len(voices)} voices", flush=True)
        else:
            print(f" failed", flush=True)
        time.sleep(0.1)
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v6.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nSaved {len(all_results)} composite lores (50 seeds × 3 voices × 4 models best-of)")

if __name__ == "__main__":
    main()
