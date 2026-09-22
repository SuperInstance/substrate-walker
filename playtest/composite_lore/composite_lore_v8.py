"""Composite lore v8 — top 100 seeds × 3 voices (DeepSeek only, fast)."""
import json, sys, time
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view

# Top 100 from great_moments
TOP_SEEDS = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))
TOP_SEED_IDS = [m["seed"] for m in TOP_SEEDS]

def ask(prompt, max_tokens=120):
    try:
        result = chat(
            provider="deepseek", model="deepseek-chat",
            messages=[{"role":"user","content":prompt}],
            max_tokens=max_tokens,
        )
        if isinstance(result, dict): return result.get("content","")
        if isinstance(result, str): return result
    except: pass
    return ""

def generate(seed):
    view, densities = render_view(seed, 16, 16, 0)
    text = "\n".join("".join(r) for r in view)
    
    prompts = {
        "structuralist": f"""Cyberpunk noir ARCHITECT. City cell pattern:

{text}

ONE sentence (15-25 words). Focus on architecture and form. No preamble.""",
        "narrativist": f"""Cyberpunk noir CHARACTER POV. Walking through:

{text}

ONE first-person sentence (15-25 words). Use 'I' or sensory detail. No preamble.""",
        "futurist": f"""Cyberpunk noir PROPHET. The city as living organism:

{text}

ONE prophetic sentence (15-25 words). Make the city breathe, dream, eat, or speak. No preamble.""",
    }
    
    voices = {}
    for voice, prompt in prompts.items():
        lore = ask(prompt, 120)
        if lore:
            lore = lore.strip().replace("\n"," ").strip('"').strip()
            if len(lore) > 15:
                voices[voice] = lore
    return voices

def main():
    print(f"Composite lore v8 — top 100 × 3 voices (DeepSeek)\n")
    
    all_results = []
    for i, seed in enumerate(TOP_SEED_IDS, 1):
        if i % 10 == 0:
            print(f"{i}/100", flush=True)
        voices = generate(seed)
        if voices:
            all_results.append({"seed": seed, "voices": voices})
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v8.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved {len(all_results)} composite lores (100 seeds × 3 voices × DeepSeek)")

if __name__ == "__main__":
    main()
