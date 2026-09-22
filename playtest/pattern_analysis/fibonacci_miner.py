import sys
import json
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view


def fib():
    a, b = 0, 1
    while a < 10000000:
        yield a
        a, b = b, a + b


print("Mining FIBONACCI NUMBERS")
seeds = list(fib())[2:200]  # skip 0, 1
print(f"Testing {len(seeds)} Fibonacci numbers...")

results = []
for i, seed in enumerate(seeds):
    if i % 20 == 0:
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
print(f"\nTop 20:")
for i, r in enumerate(results[:20], 1):
    print(f"{i:2}. seed {r['seed']:9} score {r['best_score']:.4f}")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/fibonacci_miner.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)}")
