"""Giant polygon mine - search MUCH larger polygons (n up to 100,000)."""
import sys, json, time
sys.set_int_max_str_digits(100000)
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
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


def decagonal(n):
    return n * (4*n - 3)


def hendecagonal(n):
    return n * (9*n - 7) // 2


def dodecagonal(n):
    return n * (5*n - 4)


def star_polygon(k, n):
    if n < 1:
        return 0
    return (k * n * n - (k - 4) * n) // 2


print("Giant polygon mine — n up to 100,000")

seeds = set()
seed_to_kind = {}

# Polygons up to n=100000
print("  Generating polygon seeds...")
for n in range(1, 100001):
    for fn, name in [(pentagonal, "P"), (hexagonal, "H"), (heptagonal, "He"), 
                     (octagonal, "O"), (nonagonal, "N"), (decagonal, "D"),
                     (hendecagonal, "Hd"), (dodecagonal, "Dd")]:
        try:
            v = fn(n)
            if v < 1_000_000_000:
                seeds.add(v)
                seed_to_kind[v] = f"{name}({n})"
        except:
            pass

# Star polygons
print("  Generating star polygon seeds...")
for k in [5, 6, 7, 8, 9, 11]:
    for n in range(1, 50001):
        v = star_polygon(k, n)
        if v < 1_000_000_000:
            seeds.add(v)
            seed_to_kind[v] = f"star_{k}({n})"

seeds = sorted(seeds)
print(f"Total unique seeds: {len(seeds)}")

results = []
t0 = time.time()
last_print = 0
for i, s in enumerate(seeds):
    if i - last_print >= 2000:
        elapsed = time.time() - t0
        print(f"  {i}/{len(seeds)} elapsed {elapsed:.1f}s", flush=True)
        last_print = i
    try:
        best_score = 0
        best_x, best_y = 16, 16
        for x in [8, 12, 16, 20, 24]:
            for y in [8, 12, 16, 20, 24]:
                try:
                    view, densities = render_view(s, x, y, 0)
                    score = score_view(view, densities)
                    if score > best_score:
                        best_score = score
                        best_x, best_y = x, y
                except:
                    pass
        if best_score > 0.85:
            results.append({"seed": s, "best_score": best_score, "x": best_x, "y": best_y, "kind": seed_to_kind.get(s, "?")})
    except Exception as e:
        pass

results.sort(key=lambda x: -x["best_score"])

print(f"\nFound {len(results)} candidates with score > 0.85")
print("\nTop 30:")
for i, r in enumerate(results[:30], 1):
    print(f"  #{i:3} seed {r['seed']:>11}  score {r['best_score']:.4f}  ({r.get('kind', '?')[:30]})")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/giant_polygon_miner.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nWith score >= 0.866: {sum(1 for r in results if r['best_score'] >= 0.866)}")
print(f"With score >= 0.87: {sum(1 for r in results if r['best_score'] >= 0.87)}")
