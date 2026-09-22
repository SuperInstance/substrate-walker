"""Quilt cell-state — link every canon cell to its Quilt substrate binding."""
import json
from pathlib import Path
from datetime import datetime


def main():
    # Load canon
    m = json.load(open("/workspace/research/substrate-walker/canon/cells/manifest.json"))
    jev_data = json.load(open("/workspace/research/substrate-walker/playtest/jev_canon.json"))
    jev_signatures = json.load(open("/workspace/research/substrate-walker/playtest/jev_signatures.json"))
    
    # Build seed → JEV maps
    jev_map = {d["seed"]: d for d in jev_data if "seed" in d}
    sign_map = {d["seed"]: d for d in jev_signatures if "seed" in d}
    
    # Compose full cell-state
    cell_states = []
    for entry in m["entries"]:
        seed = entry["seed"]
        
        # Build state tuple
        state = {
            "cell_id": entry["cell_id"],
            "type": entry["type"],
            "seed": seed,
            "score": entry["score"],
            "lore": entry.get("lore", ""),
            "voice": entry.get("voice", ""),
            "hash": entry["hash"],
            "jev": {}
        }
        
        if isinstance(seed, int) or isinstance(seed, str) and seed.isdigit():
            sk = int(seed) if isinstance(seed, str) else seed
            if sk in jev_map:
                state["jev"] = jev_map[sk]
            if sk in sign_map:
                state["jev_fingerprint"] = sign_map[sk]["jev_fingerprint"]
        
        cell_states.append(state)
    
    state_doc = {
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "quilt_runtime": "substrate-walker",
        "federation": "substrate-*",
        "fnv_canary": "0x024a555471370b18d",
        "best_score": m["best_score"],
        "total_cells": m["total_cells"],
        "type_breakdown": m["type_breakdown"],
        "voice_breakdown": m["voice_breakdown"],
        "cells": cell_states,
    }
    
    with open("/workspace/research/substrate-walker/quilt_canon_state.json", "w") as f:
        json.dump(state_doc, f, indent=2)
    
    print(f"Wrote quilt_canon_state.json — {len(cell_states)} cells")
    return state_doc


if __name__ == "__main__":
    main()
