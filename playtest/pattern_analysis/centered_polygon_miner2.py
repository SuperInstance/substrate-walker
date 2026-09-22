"""Centered + Star polygon mine v2 - lower threshold + score tracking."""
import sys, json, time
sys.set_int_max_str_digits(100000)
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view


def centered_polygon(k, n):
    if n < 1:
        return 0
    return (k * n * (n - 1)) // 2 + 1


def star_polygon(k, n):
    if n < 1:
        return 0
    return (k * n * n - (k - 4) * n) // 2


print("Centered + Star polygon mine v2")

seeds = set()
seed_to_kind = {}

for k in [3, 4, 5, 6, 7, 8, 9, 11, 13]:
    for n in range(1, 10001):
        v = centered_polygon(k, n)
        seeds.add(v)
        seed_to_kind[v] = f"centered_{k}-gon_n{n}"

for k in [5, 6, 7, 8, 9, 11]:
    for n in range(1, 5001):
        v = star_polygon(k, n)
        seeds.add(v)
        seed_to_kind[v] = f"star_{k}-gon_n{n}"

seeds = sorted(seeds)
print(f"Total unique seeds: {len(seeds)}")

results = []
scores = []
t0 = time.time()
last_print = 0
for i, s in enumerate(seeds):
    if i - last_print >= 20000:
        elapsed = time.time() - t0
        print(f"  {i}/{len(seeds)} elapsed {elapsed:.1f}s", flush=True)
        last_print = i
    try:
        view = render_view(s, steps=8)
        score = score_view(view)
        scores.append(score)
        if score > 0.84:
            results.append({"seed": s, "best_score": score, "kind": seed_to_kind.get(s, "?")})
    except Exception as e:
        pass

results.sort(key=lambda x: -x["best_score"])

import statistics
print(f"\nScore stats: mean={statistics.mean(scores):.4f} median={statistics.median(scores):.4f} max={max(scores):.4f} min={min(scores):.4f}")
print(f"\nFound {len(results)} candidates with score > 0.84")
print("\nTop 25:")
for i, r in enumerate(results[:25], 1):
    print(f"  #{i:3} seed {r['seed']:>11}  score {r['best_score']:.4f}  ({r.get('kind', '?')[:30]})")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/centered_polygon_miner2.json", "w") as f:
    json.dump(results, f, indent=2)
