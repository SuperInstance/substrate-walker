"""JEV canon signature — compute a multi-question JEV signature per canon cell.

Each canon cell gets a JEV "fingerprint":
- canon_worthy (noul)
- best_voice (choice)
- concrete_density (score)

This is the 21st-century analog of a canonization seal.
"""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev


VOICES = ["structuralist", "narrativist", "futurist", "lyricist", "philosophical", "noir_classic", "cosmic_horror"]


def jev_fingerprint(lore: str) -> dict:
    try:
        r = call_jev(lore[:6000], {
            "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir prose?"},
            "best_voice": {"type": "choice", "instructions": "Which voice?",
                          "criteria": {v: v.replace("_", " ") for v in VOICES}},
            "register": {"type": "score", "instructions": "Register diversity (1=formulaic, 5=novel)",
                        "criteria": [
                            {"level": "formulaic", "score": 0.0},
                            {"level": "familiar", "score": 0.25},
                            {"level": "distinct", "score": 0.5},
                            {"level": "novel", "score": 0.75},
                            {"level": "uncanny", "score": 1.0}
                        ]},
            "place_anxiety": {"type": "noul", "instructions": "Does this evoke place-as-anxiety (Heideggerian Unheimlichkeit)?"}
        })
        return r["answers"]
    except Exception as e:
        return {"error": str(e)}


def main():
    gm_path = Path("/workspace/research/substrate-walker/playtest/great_moments.json")
    gm = json.load(open(gm_path))
    top = gm[:30]
    
    print(f"=== JEV CANON SIGNATURE — {len(top)} cells ===\n")
    
    out = []
    for i, m in enumerate(top, 1):
        seed = m["seed"]
        lore = m.get("lore", "")
        if not lore or len(lore) < 30:
            continue
        
        fp = jev_fingerprint(lore)
        canon = fp.get("canon_worthy", {}).get("noul", 0)
        voice = fp.get("best_voice", {}).get("choice", "?")
        register = fp.get("register", {}).get("score", 0)
        anxiety = fp.get("place_anxiety", {}).get("noul", 0)
        
        entry = {"seed": seed, "score": m.get("score", 0), "lore": lore,
                "jev_fingerprint": {
                    "canon": canon, "voice": voice, "register": register, "anxiety": anxiety
                }}
        out.append(entry)
        print(f"{i:3}/{len(top)} seed {seed:>9}: canon={canon:.2f} voice={voice:14} register={register:.2f} anxiety={anxiety:.2f}")
        
        # Save incrementally
        with open("/workspace/research/substrate-walker/playtest/jev_signatures.json", "w") as f:
            json.dump(out, f, indent=2)
        
        time.sleep(0.05)
    
    # Summary
    if out:
        n_high_anxiety = sum(1 for e in out if e["jev_fingerprint"]["anxiety"] > 0.7)
        n_register_novel = sum(1 for e in out if e["jev_fingerprint"]["register"] > 0.5)
        print(f"\nHigh place-anxiety (p>0.7): {n_high_anxiety}/{len(out)}")
        print(f"Novel register (>0.5): {n_register_novel}/{len(out)}")


if __name__ == "__main__":
    main()
