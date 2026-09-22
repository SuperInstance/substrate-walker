"""Centered + Star polygon mine v3."""
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


print("Centered + Star polygon mine v3")

seeds = set()
seed_to_kind = {}

for k in [3, 4, 5, 6, 7, 8, 9, 11, 13]:
    for n in range(1, 5001):
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
    if i - last_print >= 1000:
        elapsed = time.time() - t0
        print(f"  {i}/{len(seeds)} elapsed {elapsed:.1f}s", flush=True)
        last_print = i
    try:
        best_score = 0
        best_x, best_y = 16, 16
        for x in [8, 12, 16, 20, 24]:
            for y in [8, 12, 16, 20, 24]:
                view, densities = render_view(s, x, y, 0)
                score = score_view(view, densities)
                if score > best_score:
                    best_score = score
                    best_x, best_y = x, y
        scores.append(best_score)
        if best_score > 0.85:
            results.append({"seed": s, "best_score": best_score, "x": best_x, "y": best_y, "kind": seed_to_kind.get(s, "?")})
    except Exception as e:
        pass

results.sort(key=lambda x: -x["best_score"])

import statistics
if scores:
    print(f"\nScore stats: mean={statistics.mean(scores):.4f} median={statistics.median(scores):.4f} max={max(scores):.4f}")

print(f"\nFound {len(results)} candidates with score > 0.85")
print("\nTop 30:")
for i, r in enumerate(results[:30], 1):
    print(f"  #{i:3} seed {r['seed']:>11}  score {r['best_score']:.4f}  ({r.get('kind', '?')[:30]})")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/centered_polygon_miner3.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)}")
print(f"With score >= 0.866: {sum(1 for r in results if r['best_score'] >= 0.866)}")
