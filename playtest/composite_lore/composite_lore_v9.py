"""Composite lore v9 — every cell in great_moments (all 100) with 7 voices (DeepSeek reasoner)."""
import json, sys, time
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view

TOP_SEEDS = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))[:100]
TOP_SEED_IDS = [m["seed"] for m in TOP_SEEDS]

def ask(prompt, max_tokens=150):
    """Use DeepSeek REASONER for deeper analysis."""
    try:
        result = chat(
            provider="deepseek", model="deepseek-reasoner",
            messages=[{"role":"user","content":prompt}],
            max_tokens=300,
        )
        if isinstance(result, dict): return result.get("content","")
        if isinstance(result, str): return result
    except: pass
    return ""

def generate(seed):
    view, densities = render_view(seed, 16, 16, 0)
    text = "\n".join("".join(r) for r in view)
    
    prompts = {
        "structuralist": f"""Cyberpunk noir ARCHITECT. City cell:

{text}

ONE sentence (15-25 words). Focus on architecture. No preamble.""",
        "narrativist": f"""Cyberpunk noir CHARACTER walking:

{text}

ONE first-person sentence (15-25 words). Sensory detail. No preamble.""",
        "futurist": f"""Cyberpunk noir PROPHET. The city as organism:

{text}

ONE prophetic sentence (15-25 words). Breathe, dream, eat, speak. No preamble.""",
        "lyricist": f"""Cyberpunk noir POET. Rain + neon + memory:

{text}

ONE lyrical sentence (15-25 words). Pure image. No preamble.""",
        "philosophical": f"""Cyberpunk noir PHILOSOPHER. The city's deeper truth:

{text}

ONE ontological sentence (15-25 words). What is this city? No preamble.""",
        "noir_classic": f"""Hard-boiled detective voice. Cyberpunk city:

{text}

ONE terse sentence (15-25 words). Like the opening line of a Chandler novel. No preamble.""",
        "cosmic_horror": f"""Cosmic horror voice. The city as incomprehensible:

{text}

ONE sentence (15-25 words). Lovecraftian overtones. The city as unknowable entity. No preamble.""",
    }
    
    voices = {}
    for voice, prompt in prompts.items():
        lore = ask(prompt, 200)
        if lore and len(lore) > 15:
            lore = lore.strip().replace("\n"," ").strip('"').strip()
            voices[voice] = lore
    return voices

def main():
    print(f"Composite lore v9 — top 100 × 7 voices (DeepSeek Reasoner)\n")
    
    all_results = []
    for i, seed in enumerate(TOP_SEED_IDS, 1):
        if i % 10 == 0:
            print(f"{i}/100", flush=True)
        voices = generate(seed)
        if voices:
            all_results.append({"seed": seed, "voices": voices})
    
    with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v9.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved {len(all_results)} composite lores (100 seeds × 7 voices × DeepSeek Reasoner)")

if __name__ == "__main__":
    main()
