import sys, json
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view

# Increase the int str limit (mersenne numbers need this)
sys.set_int_max_str_digits(100000)


def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True


# Mersenne numbers BUT cap size
mersenne_exponents = [13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203]  # only small ones
mersenne_numbers = [2**p - 1 for p in mersenne_exponents if 2**p - 1 < 10000000]

print("Mining RARE PRIME CLASSES")
seeds = set()

# Small primes (gaps)
count = 0
n = 2
while count < 500:
    if is_prime(n):
        seeds.add(n)
        count += 1
    n += 1

# Sophie Germain p (and 2p+1)
p_count = 0
for p in range(2, 50000):
    if is_prime(p) and is_prime(2*p + 1):
        seeds.add(p)
        seeds.add(2*p+1)
        p_count += 1
        if p_count > 200: break

# Twin primes
for p in range(2, 50000):
    if is_prime(p) and is_prime(p + 2):
        seeds.add(p)
        seeds.add(p + 2)

# Factorials (n!)
for n in range(3, 15):
    f = 1
    for k in range(2, n+1):
        f *= k
    seeds.add(f)
    seeds.add(f * 3)  # 3*n!

# Mersenne numbers (small only)
seeds.update(mersenne_numbers)

# Catalan numbers
def catalan(n):
    from math import factorial
    return factorial(2*n) // (factorial(n+1) * factorial(n))

for n in range(1, 30):
    c = catalan(n)
    if c < 10000000:
        seeds.add(c)

# Highly composite (sigma-rich)
for n in [1, 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720, 840, 1260, 1680, 2520, 5040, 7560, 10080]:
    seeds.add(n)

# Sum of divisors perfect numbers
for p in [2, 3, 5, 7, 13]:
    n = (2**(p-1)) * (2**p - 1)
    if n < 10000000:
        seeds.add(n)

seeds = sorted(seeds)
print(f"Testing {len(seeds)} rare prime-class numbers...")

results = []
for i, seed in enumerate(seeds):
    if i % 100 == 0:
        print(f"  {i}/{len(seeds)}", flush=True)
    
    if seed > 10000000:
        continue
    
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
print(f"\nTop 25 RARE PRIMES:")
for i, r in enumerate(results[:25], 1):
    print(f"{i:2}. seed {r['seed']:>9}  score {r['best_score']:.4f}")

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/more_special.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)}")
