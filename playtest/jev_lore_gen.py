"""JEV-driven lore generation: use JEV to score, then use ZAI/DeepInfra to fill in.

JEV is the canon-gate oracle. ZAI/DeepInfra generate lore that JEV approves.
"""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev, call_zai, call_deepinfra, extract_content


VOICES = ["structuralist", "narrativist", "futurist", "lyricist", "philosophical", "noir_classic", "cosmic_horror"]


VOICE_PROMPTS = {
    "structuralist": "You are a structuralist architect. 2-3 sentences. Architecture, brutalist, vertical, grid. NO first-person. NO characters.",
    "narrativist": "You are a first-person narrator. 2-3 sentences. Walking streets. Rain, neon, sensory. Hard-boiled noir. 'I walk...' or similar.",
    "futurist": "You are a futurist prophet. 2-3 sentences. City as organism. Time, prophecy, becoming.",
    "lyricist": "You are a lyric poet. 2-4 SHORT lines. Pure image. Compressed. Musical.",
    "philosophical": "You are a philosopher of place. 2-3 sentences. Ontology, being, Heidegger echo.",
    "noir_classic": "You are a hard-boiled detective. 2-3 sentences. Short. Tough. Economical. 'The kind of town...' voice.",
    "cosmic_horror": "You are a Lovecraftian narrator. 2-3 sentences. Impossible geometry. Dreaming city."
}


def gen_lore_zai(seed: int, voice: str) -> str:
    system = VOICE_PROMPTS[voice]
    user = f"Write a lore fragment for cyberpunk city seed {seed}. Voice: {voice}. 2-3 sentences."
    try:
        r = call_zai([
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ], max_tokens=2000, temperature=0.85)
        return extract_content(r).strip()
    except Exception as e:
        return f"[error: {e}]"


def jev_score_lore(lore: str) -> dict:
    try:
        r = call_jev(lore[:6000], {
            "canon_worthy": {"type": "noul", "instructions": "Is this canon-worthy cyberpunk-noir prose?"},
            "distinct_voice": {"type": "noul", "instructions": "Has distinctive voice, non-formulaic?"},
            "density": {"type": "score", "instructions": "Concrete sensory density (1=abstract, 5=overflowing)",
                       "criteria": [
                           {"level": "abstract", "score": 0.0},
                           {"level": "minimal", "score": 0.25},
                           {"level": "moderate", "score": 0.5},
                           {"level": "rich", "score": 0.75},
                           {"level": "overflowing", "score": 1.0}
                       ]}
        })
        return r["answers"]
    except Exception as e:
        return {"error": str(e)}


def main():
    """For each of top 50 seeds, generate 3 candidate lores per voice, keep the JEV-approved one."""
    gm_path = Path("/workspace/research/substrate-walker/playtest/great_moments.json")
    gm = json.load(open(gm_path))
    top = gm[:30]  # top 30 to keep this manageable
    
    print(f"=== JEV-DRIVEN LORE GEN === {len(top)} seeds × 7 voices × ZAI\n")
    
    out = []
    for i, m in enumerate(top, 1):
        seed = m["seed"]
        entry = {"seed": seed, "score": m["score"], "voices": {}, "jev_scores": {}}
        
        for v in VOICES:
            print(f"{i}/{len(top)} seed {seed} [{v:14}] ", end="", flush=True)
            
            # Try multiple times, keep best JEV score
            best_lore = ""
            best_score = -1
            
            for attempt in range(2):
                lore = gen_lore_zai(seed, v)
                if lore.startswith("[error"):
                    print("E", end="", flush=True)
                    continue
                
                scores = jev_score_lore(lore)
                canon = scores.get("canon_worthy", {}).get("noul", 0)
                distinct = scores.get("distinct_voice", {}).get("noul", 0)
                density = scores.get("density", {}).get("score", 0)
                combo = (canon + distinct + density) / 3
                
                if combo > best_score:
                    best_score = combo
                    best_lore = lore
                    best_scores = scores
                
                time.sleep(0.1)
            
            if best_lore:
                entry["voices"][v] = best_lore
                entry["jev_scores"][v] = {
                    "canon": scores.get("canon_worthy", {}).get("noul", 0),
                    "distinct": scores.get("distinct_voice", {}).get("noul", 0),
                    "density": scores.get("density", {}).get("score", 0),
                }
                print(f"canon={entry['jev_scores'][v]['canon']:.2f} distinct={entry['jev_scores'][v]['distinct']:.2f}")
            else:
                entry["voices"][v] = ""
                print(f"FAILED")
        
        out.append(entry)
        with open("/workspace/research/substrate-walker/playtest/jev_lore_gen.json", "w") as f:
            json.dump(out, f, indent=2)
    
    print(f"\nDone — {len(out)} seeds × 7 voices")
    print(f"\nBy voice, avg canon score:")
    for v in VOICES:
        avg = sum(e["jev_scores"][v]["canon"] for e in out if v in e["jev_scores"]) / len(out)
        print(f"  {v:14}: {avg:.3f}")


if __name__ == "__main__":
    main()
