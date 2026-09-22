"""Analyze how number structure correlates with score (final)."""

import json
from pathlib import Path


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def is_palindrome(s):
    s = str(s)
    return s == s[::-1]


def is_perfect_square(n):
    if n < 0:
        return False
    r = int(n ** 0.5)
    return r * r == n


def is_perfect_triangular(n):
    k = (1 + (1 + 8*n)**0.5) / 2
    return abs(k - round(k)) < 1e-9


def is_fibonacci(n):
    a, b = 0, 1
    while a < n:
        if a == n:
            return True
        a, b = b, a + b
    return a == n


def is_pentagonal(n):
    k = (1 + (1 + 24*n)**0.5) / 6
    return abs(k - round(k)) < 1e-6


def is_hexagonal(n):
    k = (1 + (1 + 8*n)**0.5) / 4
    return abs(k - round(k)) < 1e-6


def factor(n):
    factors = {}
    d = 2
    while d*d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


gm = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))

print(f"Analyzing {len(gm)} great moments by number structure\n")
buckets = {
    "perfect_square": [],
    "perfect_triangular": [],
    "fibonacci": [],
    "pentagonal": [],
    "hexagonal": [],
    "palindromic": [],
    "prime": [],
    "all_digits_same": [],
    "binary_palindrome": [],
    "even_only": [],
}

for m in gm:
    seed = m["seed"]
    score = m["score"]
    
    if is_perfect_square(seed): buckets["perfect_square"].append(m)
    if is_perfect_triangular(seed): buckets["perfect_triangular"].append(m)
    if is_fibonacci(seed): buckets["fibonacci"].append(m)
    if is_pentagonal(seed): buckets["pentagonal"].append(m)
    if is_hexagonal(seed): buckets["hexagonal"].append(m)
    if is_palindrome(seed): buckets["palindromic"].append(m)
    if is_prime(seed): buckets["prime"].append(m)
    
    s = str(seed)
    if len(set(s)) == 1 and len(s) > 1:
        buckets["all_digits_same"].append(m)
    
    bin_repr = bin(seed)[2:]
    if bin_repr == bin_repr[::-1]:
        buckets["binary_palindrome"].append(m)
    
    f = factor(seed)
    if all(p == 2 for p in f.keys()):
        buckets["even_only"].append(m)

print("=" * 80)
print(f"{'STRUCTURE':<25} {'COUNT':<8} {'AVG SCORE':<11} {'MAX SCORE':<11} {'BEST SEED':<12}")
print("=" * 80)
for name, ms in buckets.items():
    if not ms:
        continue
    scores = [m["score"] for m in ms]
    best = max(ms, key=lambda x: x["score"])
    print(f"{name:<25} {len(ms):<8} {sum(scores)/len(scores):<11.4f} {best['score']:<11.4f} {best['seed']:<12}")

# Save the findings
out = {
    "buckets": {name: [{"seed": m["seed"], "score": m["score"]} for m in ms] for name, ms in buckets.items()},
    "all_count": len(gm),
    "best_overall": gm[0],
}

with open("/workspace/research/substrate-walker/playtest/pattern_analysis/number_struct.json", "w") as f:
    json.dump(out, f, indent=2)

# Most discriminating categories by highest AVG
print("\n=== MOST CANON-WORTHY STRUCTURES (by avg score) ===")
ranked = sorted([(name, ms) for name, ms in buckets.items() if ms], key=lambda x: -sum(m["score"] for m in x[1])/len(x[1]))
for name, ms in ranked[:5]:
    avg = sum(m["score"] for m in ms) / len(ms)
    print(f"{name}: avg {avg:.4f} ({len(ms)} seeds)")
