"""JEV canon-acceptance gate.

For each great_moment (seed + lore), ask JEV:
- Is this canon-worthy? (noul)
- Which voice is best? (choice)
- Distinct from canon? (noul)

This is the canon-promotion gate. p>0.7 = ACCEPT.
"""
import json
import time
import sys
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev


VOICES = ["structuralist", "narrativist", "futurist", "lyricist", "philosophical", "noir_classic", "cosmic_horror"]


def jev_score(lore: str) -> dict:
    """Score one lore with JEV."""
    try:
        r = call_jev(
            lore,
            {
                "canon_worthy": {
                    "type": "noul",
                    "instructions": "Is this passage canon-worthy cyberpunk-noir prose?"
                },
                "distinct_voice": {
                    "type": "noul",
                    "instructions": "Does this have a distinctive, non-formulaic voice?"
                },
                "best_voice": {
                    "type": "choice",
                    "instructions": "Which voice register does this most embody?",
                    "criteria": {
                        "structuralist": "architecture and grid",
                        "narrativist": "first-person POV",
                        "futurist": "prophecy, organism",
                        "lyricist": "compressed image",
                        "philosophical": "ontology, being",
                        "noir_classic": "hard-boiled detective",
                        "cosmic_horror": "Lovecraftian, impossible geometry"
                    }
                },
                "concrete_density": {
                    "type": "score",
                    "instructions": "How dense is the concrete, sensory detail (1=abstract, 5=overflowing with concrete images)?",
                    "criteria": [
                        {"level": "abstract", "score": 0.0},
                        {"level": "minimal", "score": 0.25},
                        {"level": "moderate", "score": 0.5},
                        {"level": "rich", "score": 0.75},
                        {"level": "overflowing", "score": 1.0}
                    ]
                }
            }
        )
        return r["answers"]
    except Exception as e:
        return {"error": str(e)}


def main():
    gm_path = Path("/workspace/research/substrate-walker/playtest/great_moments.json")
    gm = json.load(open(gm_path))
    
    print(f"=== JEV Canon-Gate — {len(gm)} great_moments ===\n")
    
    out = []
    for i, m in enumerate(gm, 1):
        seed = m["seed"]
        lore = m.get("lore", "")
        if not lore or len(lore) < 30:
            print(f"{i:3}/{len(gm)} seed {seed:>9}: SKIP (no lore)")
            continue
        
        # Truncate lore for JEV (state is text only)
        state = lore[:6000]
        
        try:
            answers = jev_score(state)
            
            canon_noul = answers.get("canon_worthy", {}).get("noul", 0)
            distinct_noul = answers.get("distinct_voice", {}).get("noul", 0)
            voice_choice = answers.get("best_voice", {}).get("choice", "?")
            density = answers.get("concrete_density", {}).get("score", 0)
            
            # Promote if canon_worthy > 0.7 AND distinct > 0.5
            promote = canon_noul > 0.7 and distinct_noul > 0.5
            
            entry = {
                "seed": seed,
                "score": m.get("score", 0),
                "lore": lore,
                "noul_canon": canon_noul,
                "noul_distinct": distinct_noul,
                "jev_voice": voice_choice,
                "density": density,
                "promote": promote
            }
            out.append(entry)
            
            status = "ACCEPT" if promote else "REVIEW"
            print(f"{i:3}/{len(gm)} seed {seed:>9}: canon={canon_noul:.2f} distinct={distinct_noul:.2f} voice={voice_choice:14} density={density:.2f} -> {status}")
        except Exception as e:
            print(f"{i:3}/{len(gm)} seed {seed:>9}: ERROR {str(e)[:80]}")
        
        # Save incremental
        out_path = Path("/workspace/research/substrate-walker/playtest/jev_canon.json")
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)
        
        time.sleep(0.05)
    
    # Summary
    n_accept = sum(1 for e in out if e.get("promote"))
    n_review = sum(1 for e in out if not e.get("promote"))
    print(f"\n=== JEV CANON GATE ===")
    print(f"Accept: {n_accept}, Review: {n_review}")
    print(f"\nTop 10 by JEV canon score:")
    by_jev = sorted([e for e in out if "noul_canon" in e], key=lambda x: -x["noul_canon"])[:10]
    for e in by_jev:
        print(f"  seed {e['seed']:>9}  canon={e['noul_canon']:.2f}  distinct={e['noul_distinct']:.2f}  voice={e['jev_voice']:14}")


if __name__ == "__main__":
    main()
