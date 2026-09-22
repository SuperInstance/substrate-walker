"""Mine Catalan numbers, Motzkin numbers, Lucas numbers."""

import sys
import json
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view


def catalan(n):
    """C_n = (2n)! / ((n+1)! n!)"""
    from math import factorial
    return factorial(2*n) // (factorial(n+1) * factorial(n))


def motzkin(n):
    """M_0=1, M_n = ((2n+1)M_{n-1} + (3n-3)M_{n-2}) / (n+2)"""
    if n == 0:
        return 1
    if n == 1:
        return 1
    a, b = 1, 1
    for k in range(2, n+1):
        a, b = b, ((2*k+1)*b + (3*k-3)*a) // (k+2)
    return b


def lucas():
    a, b = 2, 1
    while a < 10000000:
        yield a
        a, b = b, a + b


def pell():
    a, b = 0, 1
    while a < 10000000:
        yield a
        a, b = b, 2*a + b


print("Mining SPECIAL SEQUENCES — Catalan, Motzkin, Lucas, Pell")

seeds = set()

# Catalan
for n in range(1, 25):
    c = catalan(n)
    if c < 1000000:
        seeds.add(c)

# Motzkin
for n in range(0, 50):
    m = motzkin(n)
    if m < 1000000:
        seeds.add(m)

# Lucas
seeds.update(list(lucas())[1:30])

# Pell
seeds.update(list(pell())[2:30])

seeds = sorted(seeds)
print(f"Testing {len(seeds)} special numbers...")

results = []
for i, seed in enumerate(seeds):
    if i % 30 == 0:
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

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/special_miner.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)}")
