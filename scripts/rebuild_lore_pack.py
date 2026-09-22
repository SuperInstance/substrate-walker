"""Rebuild lore_pack.json from all sources."""
import json
from pathlib import Path

sources = [
    Path("/workspace/research/substrate-walker/playtest/square_lores.json"),
    Path("/workspace/research/substrate-walker/playtest/triangular_lores.json"),
    Path("/workspace/research/substrate-walker/playtest/figurate_lores.json"),
    Path("/workspace/research/substrate-walker/playtest/neighborhood_canon.json"),
    Path("/workspace/research/substrate-walker/playtest/new_bests_lores.json"),
    Path("/workspace/research/substrate-walker/playtest/great_moments.json"),
    Path("/workspace/research/substrate-walker/playtest/missing_lores.json"),
    Path("/workspace/research/substrate-walker/playtest/gan/mine_sigma/final.json"),
    Path("/workspace/research/substrate-walker/playtest/gan/mine_omega_long/final.json"),
]

all_lores = []
for src in sources:
    if not src.exists():
        continue
    try:
        data = json.load(open(src))
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "seed" in item:
                    lore = item.get("lore") or item.get("top_lore") or ""
                    score = item.get("best_score") or item.get("score") or 0.85
                    if lore and len(lore) > 5:
                        all_lores.append({"seed": item["seed"], "lore": lore, "score": score})
        elif isinstance(data, dict) and "best_score" in data:
            lore = data.get("lore", "")
            if lore:
                all_lores.append({"seed": data["seed"], "lore": lore, "score": data["best_score"]})
    except Exception as e:
        print(f"  warn: {src}: {e}")

# Dedupe by lore prefix
seen = set()
unique = []
for l in all_lores:
    # Skip junk
    if any(k in l["lore"] for k in ["RATINGS:", "AI:", "(Note:", "Your character", "*press enter", "press enter"]):
        continue
    if len(l["lore"]) < 15:
        continue
    if l.get("score", 1) > 0.95:
        l["score"] = 0.85
    key = l["lore"][:50]
    if key not in seen:
        seen.add(key)
        unique.append(l)

unique.sort(key=lambda x: -x["score"])
print(f"Total: {len(all_lores)}, unique: {len(unique)}")

lore_cache = {
    "version": "2.2.0",
    "updated_at": "2026-09-22T17:15:00Z",
    "total_lores": len(unique),
    "best_score": unique[0]["score"],
    "best_seed": unique[0]["seed"],
    "best_lore": unique[0]["lore"],
    "fnv_canary": "0x24a555471370b18d",
    "lores": unique,
}

with open("/workspace/research/substrate-walker/docs/lore_pack.json", "w") as f:
    json.dump(lore_cache, f, indent=2)

print(f"Saved lore_pack.json with {len(unique)} lores, top score {unique[0]['score']:.4f}")
