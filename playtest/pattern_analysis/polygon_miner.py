"""Polygon miner — pentagons, hexagons, heptagons, octagons, nonagons at LARGER sizes."""
import sys, json
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
sys.set_int_max_str_digits(100000)
from playtest_v2 import render_view, score_view


def pentagonal(n):
    return n * (3*n - 1) // 2


def hexagonal(n):
    return n * (2*n - 1)


def heptagonal(n):
    return n * (5*n - 3) // 2


def octagonal(n):
    return n * (3*n - 2)


def nonagonal(n):
    return n * (4*n - 3) // 2


print("Mining LARGER polygonal numbers (n up to 50000)")

seeds = set()
for n in range(1, 50000):
    for fn in [pentagonal, hexagonal, heptagonal, octagonal, nonagonal]:
        try:
            v = fn(n)
            if v < 100000000:
                seeds.add(v)
        except:
            pass

seeds = sorted(seeds)
print(f"Testing {len(seeds)} polygonal numbers...")

results = []
for i, seed in enumerate(seeds):
    if i % 500 == 0:
        print(f"  {i}/{len(seeds)}", flush=True)
    
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
print(f"\nTop 25 LARGER POLYGONS:")
for i, r in enumerate(results[:25], 1):
    print(f"{i:2}. seed {r['seed']:>11}  score {r['best_score']:.4f}")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/polygon_miner.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)}")
