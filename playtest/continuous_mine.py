"""Continuous mine — keep finding canon-worthy seeds."""
import sys, json, random, time
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view

def gen_special_seed(rng):
    """Generate a special number seed (squares, triangulars, primes, etc.)"""
    n = rng.randint(50, 9999)
    pick = rng.randint(0, 7)
    if pick == 0: return n * n               # square
    if pick == 1: return n * (n+1) // 2     # triangular
    if pick == 2: return n * (3*n - 1) // 2 if n > 0 else n  # pentagonal
    if pick == 3: return n * (2*n - 1)       # hexagonal
    if pick == 4: return n * (5*n - 3) // 2  # heptagonal
    if pick == 5: return 2**rng.randint(3, 30) - rng.randint(1, 50)  # Mersenne-ish
    if pick == 6: return int(f"1{rng.randint(10**5, 10**7)}")  # big number ending in 1
    return rng.randint(100000, 9999999)

print("Continuous mine — looking for canon-worthy seeds")
rng = random.Random(42)
tested = set()
results = []

for round_num in range(20):  # 20 rounds = 6000 seeds
    seeds = [gen_special_seed(rng) for _ in range(300)]
    for i, seed in enumerate(seeds):
        if seed in tested or seed < 100:
            continue
        tested.add(seed)
        
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
    
    if round_num % 2 == 0:
        results.sort(key=lambda r: -r["best_score"])
        top = results[0]
        print(f"Round {round_num + 1}: {len(tested)} tested, top score {top['best_score']:.4f} seed {top['seed']}")
    
    if len(tested) > 6000:
        break

results.sort(key=lambda r: -r["best_score"])
print(f"\nTop 20 from continuous mine:")
for i, r in enumerate(results[:20], 1):
    print(f"{i:2}. seed {r['seed']:9} score {r['best_score']:.4f}")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/continuous_mine.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} total")
