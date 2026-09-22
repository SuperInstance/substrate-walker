"""More special number mining — abundant, amicable, tau, sigma-rich numbers."""

import sys
import json
import math
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view


def divisor_sum(n):
    """Sum of proper divisors."""
    if n <= 1:
        return 0
    s = 1
    r = int(n ** 0.5)
    for i in range(2, r + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s


def amicable_chain(n, depth=2):
    """Trace amicable pair chain starting at n (depth 1) or pair (depth 2)."""
    out = [n]
    cur = n
    for _ in range(depth * 5):
        s = divisor_sum(cur)
        if s <= cur or s > 1000000:
            return out
        out.append(s)
        cur = s
    return out


def tau_count(n):
    """Number of divisors."""
    c = 1
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        if p * p > n:
            break
        exp = 1
        while n % p == 0:
            n //= p
            exp += 1
        c *= exp
    if n > 1:
        c *= 2
    return c


print("Mining SPECIAL NUMBERS — amicable pairs, abundant, perfect, etc.")

seeds = set()

# Perfect numbers
known_perfect = [6, 28, 496, 8128, 33550336]
seeds.update(p for p in known_perfect if p < 1000000)

# Amicable pair starting values
known_amicable_starts = [220, 284, 1184, 1210, 2620, 2924, 5020, 5564, 6232, 6368, 10744, 10856, 12285, 14595, 17296, 18416, 19652, 19658, 20084, 20312, 23585, 23976, 24920, 27596, 27644, 29062, 29172]
for a in known_amicable_starts[:50]:
    seeds.add(a)

# Abundant numbers (more abundant than themselves)
for n in range(12, 5000):
    if divisor_sum(n) > n:
        seeds.add(n)
        if len([s for s in seeds if 1000 <= s <= 5000]) > 500:
            break

# Tau-rich (more divisors than typical)
for n in range(60, 50000, 1):
    if tau_count(n) > 100:
        seeds.add(n)
        if len([s for s in seeds if 1000 <= s <= 5000]) > 500:
            break

# Some known high-tau numbers
seeds.update([720, 840, 1260, 1680, 2520, 5040, 7560, 10080])

# Lucky numbers (sieve)
lucky = [1, 3, 7, 9, 13, 15, 21, 25, 31, 33, 37, 43, 49, 51]
seeds.update(l * 100 for l in lucky[:30])

seeds = sorted(seeds)
print(f"Testing {len(seeds)} special numbers...")

results = []
for i, seed in enumerate(seeds):
    if i % 100 == 0:
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

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/special_numbers_2.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)}")
