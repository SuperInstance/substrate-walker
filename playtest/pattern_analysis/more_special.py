import sys, json
sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view


def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True


def carmichael(n):
    """Carmichael numbers (Fermat pseudoprimes passing ALL a: a^n-1 ≡ 1 mod n)."""
    if n < 561: return False
    for p in [2, 3, 5, 7, 11]:
        if n % p == 0 and n != p:
            return False
    if not is_prime(n - 1) and n % (n-1) == 0:
        return False
    for a in [2, 3, 5, 7, 11]:
        if pow(a, n-1, n) != 1:
            return False
    return True


def find_primes_generator(start, count, primes_per_yield):
    n = start
    found = 0
    while found < count:
        if is_prime(n):
            yield n
            found += 1
        n += 1


def lucas_lehmer_p(p):
    """Is p a Mersenne prime exponent? 2^p-1 prime iff M_p passes Lucas-Lehmer."""
    if p < 2 or not is_prime(p):
        return False
    M = 2**p - 1
    s = 4
    for _ in range(p - 2):
        s = (s*s - 2) % M
    return s == 0


# 1. Prime gaps: 1000 primes
# 2. Twin primes (p, p+2 both prime)
# 3. Sophie Germain primes (p and 2p+1 both prime)
# 4. Safe primes (p where (p-1)/2 is prime)
# 5. Carmichael numbers
# 6. Factorial-adjacent numbers

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

# Triangular factorials
for n in range(3, 15):
    f = 1
    for k in range(2, n+1):
        f *= k
    seeds.add(f)
    seeds.add(f * 3)  # 3*n!

# Mersenne numbers (M_p = 2^p - 1)
mersenne_exponents = [2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423,9689,9941,11213,19937,21701,23209,44497,86243,110503,132049,216091,756839,859433,1257787,1398269,2976221,3021377,6972593,13466917,20996011,24036583,25964951,30402457,32582657,37156667,42643801,43112609,57885161,74207281,77232917,82589933]
for p in mersenne_exponents:
    M = 2**p - 1
    seeds.add(M)

seeds = sorted(seeds)
print(f"Testing {len(seeds)} rare prime-class numbers...")

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
print(f"\nTop 25 RARE PRIMES:")
for i, r in enumerate(results[:25], 1):
    print(f"{i:2}. seed {r['seed']:25} score {r['best_score']:.4f}")

import json
with open("/workspace/research/substrate-walker/playtest/pattern_analysis/more_special.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)}")
