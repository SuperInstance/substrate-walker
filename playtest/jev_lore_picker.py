"""JEV lore picker — find the BEST lore per voice across all generators.

For each seed, look at lore across:
1. Composite lore v3-v11 (multiple voices × multiple models)
2. JEV-scored from jev_lore_gen.json

Then for each voice, pick the lore that JEV scores highest.

This is the lore picker — solves the multi-voice canon problem
of which lore is canonical for each voice per seed.
"""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev


VOICES = ["structuralist", "narrativist", "futurist", "lyricist", "philosophical", "noir_classic", "cosmic_horror"]


def jev_3q_score(lore: str) -> dict:
    """Score with 3 questions to keep it cheap."""
    try:
        r = call_jev(lore[:6000], {
            "canon": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
            "distinct": {"type": "noul", "instructions": "Distinct, non-formulaic voice?"},
            "voice": {"type": "choice", "instructions": "Which voice?",
                     "criteria": {v: v.replace("_", " ") for v in VOICES}}
        })
        return r["answers"]
    except Exception as e:
        return {"error": str(e)}


def main():
    print("=== JEV LORE PICKER — find best lore per voice per seed ===\n")
    
    # Collect all lores per seed per voice
    all_lores = {}  # seed → voice → list of lores
    
    # Composite lore sources
    cl_dir = Path("/workspace/research/substrate-walker/playtest/composite_lore")
    for jf in cl_dir.glob("composite_lore_v*.json"):
        if "combined" in jf.name:
            continue
        try:
            data = json.load(open(jf))
        except:
            continue
        if not isinstance(data, list):
            continue
        for entry in data:
            seed = entry.get("seed")
            voices = entry.get("voices", {})
            if not seed or not voices:
                continue
            
            if seed not in all_lores:
                all_lores[seed] = {v: [] for v in VOICES}
            for v in VOICES:
                if v in voices and voices[v] and not voices[v].startswith("[error"):
                    all_lores[seed][v].append(voices[v])
    
    print(f"Total seeds: {len(all_lores)}")
    print(f"Total lores: {sum(sum(len(ls) for ls in voices.values()) for voices in all_lores.values())}")
    
    # For each seed × voice, pick candidate lores and JEV-score them
    print(f"\nScoring... (this will take time)")
    
    out = {}
    for seed, voices in sorted(all_lores.items())[:50]:
        print(f"\nseed {seed}:")
        seed_best = {v: {"lore": "", "score": -1} for v in VOICES}
        
        for v in VOICES:
            candidates = voices[v]
            if not candidates:
                continue
            
            # Limit to 3 candidates per voice to keep cost down
            candidates = candidates[:3]
            
            print(f"  [{v:14}] {len(candidates)} candidates")
            
            for cand in candidates:
                # Use combined score: avg(canon, distinct)
                scores = jev_3q_score(cand)
                canon = scores.get("canon", {}).get("noul", 0)
                distinct = scores.get("distinct", {}).get("noul", 0)
                combo = (canon + distinct) / 2
                
                if combo > seed_best[v]["score"]:
                    seed_best[v] = {"lore": cand, "score": combo, "canon": canon, "distinct": distinct}
        
        out[seed] = seed_best
        with open("/workspace/research/substrate-walker/playtest/jev_best_lores.json", "w") as f:
            json.dump(out, f, indent=2)
        time.sleep(0.05)
    
    # Summary
    print("\n=== DONE ===")
    for seed in sorted(out.keys())[:10]:
        best_voices = sum(1 for v in VOICES if out[seed][v]["lore"])
        avg_score = sum(out[seed][v]["score"] for v in VOICES if out[seed][v]["lore"]) / max(1, best_voices)
        print(f"  seed {seed:>9}: {best_voices}/7 voices found, avg score {avg_score:.3f}")


if __name__ == "__main__":
    main()
