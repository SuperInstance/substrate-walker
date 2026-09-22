"""Fill lores for all top 100 canon seeds."""
import json, sys
sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from multi_api import chat
from playtest_v2 import render_view, score_view, generate_lore

gm = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))

def get_lore(seed, score):
    """Try multiple providers for lore."""
    view, densities = render_view(seed, 16, 16, 0)
    lore = generate_lore({"view": view, "x": 16, "y": 16, "angle": 0, "score": score, "seed": seed})
    if lore and len(lore) > 5:
        return lore
    return ""

# Process all
print(f"Generating lores for all 100 great moments")
for i, m in enumerate(gm, 1):
    if i % 10 == 0:
        print(f"  {i}/100", flush=True)
    if m.get("lore") and len(m["lore"]) > 5:
        continue
    lore = get_lore(m["seed"], m["score"])
    if lore:
        m["lore"] = lore

# Save
with open("/workspace/research/substrate-walker/playtest/great_moments.json", "w") as f:
    json.dump(gm, f, indent=2)

# Count filled
with_lore = sum(1 for m in gm if m.get("lore") and len(m["lore"]) > 5)
print(f"\n{with_lore}/100 with lores")
