import sys
import json
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view


def pentagonal(n):
    return n * (3*n - 1) // 2


def hexagonal(n):
    return n * (2*n - 1)


def heptagonal(n):
    return n * (5*n - 3) // 2


print("Mining FIGURATE NUMBERS — pentagons, hexagons, heptagons")

all_figurate = set()
for n in range(1, 1500):
    p = pentagonal(n)
    h = hexagonal(n)
    he = heptagonal(n)
    if p < 5000000:
        all_figurate.add(p)
    if h < 5000000:
        all_figurate.add(h)
    if he < 5000000:
        all_figurate.add(he)

seeds = sorted(all_figurate)
print(f"Testing {len(seeds)} figurate numbers...")

results = []
for i, seed in enumerate(seeds):
    if i % 200 == 0:
        print(f"  {i}/{len(seeds)}")
    
    best_score = 0
    best_x, best_y = 16, 16
    for x in range(8, 28, 4):
        for y in range(8, 28, 4):
            view, densities = render_view(seed, x, y, 0)
            score = score_view(view, densities)
            if score > best_score:
                best_score = score
                best_x, best_y = x, y
    
    results.append({"seed": seed, "best_score": best_score, "x": best_x, "y": best_y})

results.sort(key=lambda r: -r["best_score"])
print(f"\nTop 25:")
for i, r in enumerate(results[:25], 1):
    print(f"{i:2}. seed {r['seed']:9} score {r['best_score']:.4f}")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/figurate_miner.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)}")
