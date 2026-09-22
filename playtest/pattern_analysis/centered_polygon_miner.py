"""Centered + Star polygon mine."""
import sys, json, time
sys.set_int_max_str_digits(100000)
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view


def centered_polygon(k, n):
    """Centered k-gonal number for n=1,2,3,..."""
    if n < 1:
        return 0
    return (k * n * (n - 1)) // 2 + 1


def star_polygon(k, n):
    """Star k-gonal number."""
    if n < 1:
        return 0
    return (k * n * n - (k - 4) * n) // 2


print("Centered + Star polygon mine")

seeds = set()
seed_to_kind = {}

# Centered polygons up to n=10000
print("  Generating centered polygon seeds...")
for k in [3, 4, 5, 6, 7, 8, 9, 11, 13]:
    for n in range(1, 10001):
        v = centered_polygon(k, n)
        seeds.add(v)
        seed_to_kind[v] = f"centered_{k}-gon_n{n}"

# Star polygons
print("  Generating star polygon seeds...")
for k in [5, 6, 7, 8, 9, 11]:
    for n in range(1, 5001):
        v = star_polygon(k, n)
        seeds.add(v)
        seed_to_kind[v] = f"star_{k}-gon_n{n}"

seeds = sorted(seeds)
print(f"Total unique seeds: {len(seeds)}")

# Score them
results = []
t0 = time.time()
last_print = 0
for i, s in enumerate(seeds):
    if i - last_print >= 5000:
        elapsed = time.time() - t0
        rate = i / elapsed if elapsed > 0 else 0
        eta = (len(seeds) - i) / rate if rate > 0 else 0
        print(f"  {i}/{len(seeds)} elapsed {elapsed:.1f}s rate {rate:.1f}/s eta {eta:.1f}s", flush=True)
        last_print = i
    try:
        view = render_view(s, steps=8)
        score = score_view(view)
        if score > 0.86:
            results.append({"seed": s, "best_score": score, "kind": seed_to_kind.get(s, "?")})
    except Exception as e:
        pass

results.sort(key=lambda x: -x["best_score"])
print(f"\nFound {len(results)} candidates with score > 0.86")
print("\nTop 25:")
for i, r in enumerate(results[:25], 1):
    print(f"  #{i:3} seed {r['seed']:>11}  score {r['best_score']:.4f}  ({r.get('kind', '?')[:25]})")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/centered_polygon_miner.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} candidates")
print(f"With score >= 0.866: {sum(1 for r in results if r['best_score'] >= 0.866)}")
