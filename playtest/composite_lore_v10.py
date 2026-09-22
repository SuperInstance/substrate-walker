"""Composite lore v10 — top 50 seeds × 7 voices × ZAI glm-5.3-flash."""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_zai, extract_content


VOICES = ["structuralist", "narrativist", "futurist", "lyricist", "philosophical", "noir_classic", "cosmic_horror"]


VOICE_PROMPTS = {
    "structuralist": """You are a structuralist architect. Describe a cyberpunk-noir city in 2-3 sentences. Focus on:
- Architectural form: brutalist, angular, layered, vertical
- The bones and grid of the city
- Materials: concrete, glass, rust, neon
- The geometry of habitation
Do not use first-person. Do not invent characters. Pure structural description.""",

    "narrativist": """You are a first-person narrator. Describe a cyberpunk-noir city in 2-3 sentences. Focus on:
- Walking through streets
- Sensory details: rain, neon, smell, sound
- The body in motion through the city
- First-person POV ("I walk...", "The alley swallows me...")
Strong noir voice. Hard-boiled but not pulp.""",

    "futurist": """You are a futurist prophet. Describe a cyberpunk-noir city in 2-3 sentences. Focus on:
- The city as organism, evolving, breathing
- Time: past feeding future, memories becoming architecture
- Prophecy: what this city will become
- Mythic register""",

    "lyricist": """You are a lyric poet. Describe a cyberpunk-noir city in 2-4 SHORT lines. Focus on:
- Pure image
- Compressed language
- Musicality, rhythm
- No narrative, no philosophy
- Each line should land on its own""",

    "philosophical": """You are a philosopher of place. Describe a cyberpunk-noir city in 2-3 sentences. Focus on:
- Ontology: what kind of being does this city have?
- Memory, time, identity embedded in urban form
- Heidegger, Calvino, Borges echo
- Question the city rather than describe it""",

    "noir_classic": """You are a hard-boiled detective in a 1940s noir novel, but the city is cyberpunk. Describe in 2-3 sentences. Focus on:
- The dame, the case, the weather
- Rain, neon, danger
- Short sentences. Tough. Economical.
- "The kind of town where..." voice""",

    "cosmic_horror": """You are a Lovecraftian narrator. Describe a cyberpunk-noir city in 2-3 sentences. Focus on:
- The geometry should NOT be possible
- The city is dreaming
- Angles that should not exist
- The narrator is afraid but compelled
- Hint at an underlying truth too terrible to name"""
}


def gen_lore(seed: int, voice: str, model: str = "glm-5.3-flash") -> str:
    """Generate one lore string."""
    system = VOICE_PROMPTS[voice]
    user = f"Write a lore fragment for city seed {seed}. 2-3 sentences. The voice is {voice}."
    
    try:
        r = call_zai([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ], max_tokens=2000, temperature=0.85)
        text = extract_content(r).strip()
        # Clean up
        if not text:
            return ""
        # Strip leading numbering/bullets
        text = text.lstrip("0123456789.-) ").strip()
        return text
    except Exception as e:
        return f"[error: {str(e)[:60]}]"


def main():
    # Load top 50 from great_moments
    gm_path = Path("/workspace/research/substrate-walker/playtest/great_moments.json")
    gm = json.load(open(gm_path))
    top = gm[:50]
    
    print(f"Composite lore v10 — {len(top)} seeds × 7 voices × ZAI glm-5.3-flash")
    
    out = []
    for i, m in enumerate(top, 1):
        seed = m["seed"]
        print(f"\n{i}/{len(top)} seed {seed}:")
        entry = {"seed": seed, "score": m["score"], "voices": {}}
        for v in VOICES:
            print(f"  [{v:14}] ...", end="", flush=True)
            lore = gen_lore(seed, v)
            entry["voices"][v] = lore
            if lore and not lore.startswith("[error"):
                print(f" {lore[:50]}...")
            else:
                print(f" {lore[:50]}")
            time.sleep(0.3)  # gentle rate limit
        
        out.append(entry)
        # Save incremental
        with open("/workspace/research/substrate-walker/playtest/composite_lore/composite_lore_v10.json", "w") as f:
            json.dump(out, f, indent=2)
    
    print(f"\n\nDONE — {len(out)} seeds × 7 voices saved")


if __name__ == "__main__":
    main()
