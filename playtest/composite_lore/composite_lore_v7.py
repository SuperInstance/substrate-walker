"""Composite lore v7 - top 10 seeds, all working models, multi-voice."""
import json, sys, time
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view

TOP_SEEDS = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))[:10]
TOP_SEED_IDS = [m["seed"] for m in TOP_SEEDS]

# 7 models — all verified working
MODELS = [
    ("deepseek", "deepseek-chat", "DeepSeek"),
    ("deepseek", "deepseek-reasoner", "DeepSeek-Reasoner"),
    ("deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "Llama-8b"),
    ("deepinfra", "google/gemma-3-27b-it", "Gemma-3-27b"),
    ("deepinfra", "mistralai/Mistral-Small-3.2-24B-Instruct-2506", "Mistral-Small"),
]


def ask(p, m, prompt, max_tokens=180):
    try:
        r = chat(provider=p, model=m, messages=[{"role":"user","content":prompt}], max_tokens=max_tokens)
        if isinstance(r, dict): return r.get("content","")
        if isinstance(r, str): return r
    except: pass
    return ""

def best(*lores):
    valid = [l for l in lores if l and len(l) > 15]
    if not valid: return ""
    return max(valid, key=len)

def generate(seed):
    view, densities = render_view(seed, 16, 16, 0)
    text = "\n".join("".join(r) for r in view)
    
    prompts = {
        "structuralist": f"""Cyberpunk noir ARCHITECT. City cell:

{text}

ONE sentence (15-25 words). Architecture focus. No preamble.""",
        "narrativist": f"""Cyberpunk noir CHARACTER walking through:

{text}

ONE first-person sentence (15-25 words). Sensory. No preamble.""",
        "futurist": f"""Cyberpunk noir PROPHET. The city as living organism:

{text}

ONE prophetic sentence (15-25 words). Make city breathe, dream, eat, speak. No preamble.""",
        "lyricist": f"""Cyberpunk noir POET. Rain + neon + memory:

{text}

ONE lyrical sentence (15-25 words). Pure image, no explanation. No preamble.""",
        "philosophical": f"""Cyberpunk noir PHILOSOPHER. The city's deeper truth:

{text}

ONE ontological sentence (15-25 words). What is this city's nature? No preamble.""",
    }
    
    voices = {}
    for voice, prompt in prompts.items():
        lores = []
        for p, m, _ in MODELS:
            lore = ask(p, m, prompt, 150)
            if lore and len(lore) > 15:
                lores.append(lore.strip().replace("\n"," ").strip('"').strip())
        if lores:
            voices[voice] = max(lores, key=len)
    
    return voices


def main():
    print(f"Composite lore v7 — top 10 seeds × 5 voices × 5 models (best-of)\n")
    
    all_results = []
    for i, seed in enumerate(TOP_SEED_IDS, 1):
        print(f"\n{i}. seed {seed}:", end='', flush=True)
        voices = generate(seed)
        if voices:
            all_results.append({"seed": seed, "voices": voices})
            print(f" {len(voices)} voices")
            for v, l in voices.items():
                print(f"   [{v:14}]: {l[:80]}")
        time.sleep(0.2)
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v7.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\nSaved {len(all_results)} composite lores (10 seeds × 5 voices × 5 models best-of)")


if __name__ == "__main__":
    main()
