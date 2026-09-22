"""Composite lore v11 — use JEV-scored seeds, generate with DeepInfra (free tier).

Strategy:
1. Get the 14 ACCEPT seeds from JEV canon-gate
2. For each, generate 7 voices with DeepInfra Llama-3.1-8B
3. Apply paraphrase penalty
4. Save combined
"""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, extract_content


VOICES = ["structuralist", "narrativist", "futurist", "lyricist", "philosophical", "noir_classic", "cosmic_horror"]


VOICE_PROMPTS = {
    "structuralist": "You are a structuralist architect. Write 2-3 sentences about a cyberpunk city at the given seed. Focus on architecture: brutalist, angular, vertical, grid, concrete, glass, rust, neon. No first-person. No characters. Pure structural description.",
    "narrativist": "You are a first-person noir narrator. Write 2-3 sentences walking through a cyberpunk city at the given seed. Hard-boiled but not pulp. Sensory details: rain, neon, smell, sound. Start with 'I'.",
    "futurist": "You are a futurist prophet. Write 2-3 sentences about the cyberpunk city at the given seed as organism. Time, prophecy, becoming. Mythic register.",
    "lyricist": "You are a lyric poet. Write 2-4 SHORT lines about a cyberpunk city at the given seed. Pure image. Compressed. Musical. No narrative, no philosophy.",
    "philosophical": "You are a philosopher of place. Write 2-3 sentences about the cyberpunk city at the given seed. Ontology, being, Heidegger echo. Question the city rather than describe it.",
    "noir_classic": "You are a hard-boiled detective. Write 2-3 sentences. Short. Tough. Economical. 'The kind of town where...' voice.",
    "cosmic_horror": "You are a Lovecraftian narrator. Write 2-3 sentences. Geometry that should NOT be possible. The city is dreaming. Angles that should not exist. Hint at a truth too terrible to name."
}


def gen_lore_di(seed: int, voice: str) -> str:
    system = VOICE_PROMPTS[voice]
    user = f"Cyberpunk city at seed {seed}. Voice: {voice}."
    try:
        r = call_deepinfra([
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ], model="meta-llama/Meta-Llama-3.1-8B-Instruct",
            max_tokens=300, temperature=0.85)
        return extract_content(r).strip()
    except Exception as e:
        return f"[error: {str(e)[:80]}]"


def main():
    # Get ACCEPT seeds from jev_canon.json
    jev_path = Path("/workspace/research/substrate-walker/playtest/jev_canon.json")
    jev = json.load(open(jev_path))
    accepted_seeds = [d["seed"] for d in jev if d.get("promote")]
    
    print(f"=== Composite lore v11 — {len(accepted_seeds)} ACCEPT seeds × 7 voices × DeepInfra ===")
    print(f"Seeds: {accepted_seeds}\n")
    
    out = []
    for i, seed in enumerate(accepted_seeds, 1):
        print(f"\n{i}/{len(accepted_seeds)} seed {seed}:")
        entry = {"seed": seed, "voices": {}}
        for v in VOICES:
            print(f"  [{v:14}] ", end="", flush=True)
            lore = gen_lore_di(seed, v)
            entry["voices"][v] = lore
            print(f"{lore[:50].replace(chr(10), ' ')}...")
            time.sleep(0.1)
        out.append(entry)
        
        with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v11.json", "w") as f:
            json.dump(out, f, indent=2)
    
    print(f"\nDONE — {len(out)} seeds × 7 voices")


if __name__ == "__main__":
    main()
