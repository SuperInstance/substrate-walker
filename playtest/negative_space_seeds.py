"""Generate seeds in negative space patterns."""

import json
from pathlib import Path


def gen_negative_space():
    seeds = []
    # Negative seeds
    for i in [1, 7, 42, 100, 1000, 10000, 100000, 1000000]:
        seeds.append(-i)
    
    # Very large
    for i in [10000000, 50000000, 100000000, 999999999]:
        seeds.append(i)
    
    # All-1s bit patterns
    seeds.extend([7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535])
    
    # Palindromes (5-digit)
    palindromes = []
    for a in range(1, 10):
        for b in range(0, 10):
            for c in range(0, 10):
                palindromes.append(int(f"{a}{b}{c}{b}{a}"))
    seeds.extend(palindromes[:100])
    
    # Primes up to 10000
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True
    
    primes = [n for n in range(2, 10000) if is_prime(n)]
    seeds.extend(primes[::10])  # Sample 1/10
    
    # Perfect squares
    seeds.extend([i*i for i in range(1, 1000)])
    
    # Fibonacci
    a, b = 1, 1
    fibs = [1, 1]
    for _ in range(50):
        a, b = b, a + b
        fibs.append(b)
    seeds.extend(fibs[:30])
    
    # Powers of 2
    seeds.extend([2**i for i in range(20)])
    
    # Powers of 10
    seeds.extend([10**i for i in range(10)])
    
    # Single digit repeats
    for d in range(10):
        for n in [2, 3, 4, 5, 6]:
            seeds.append(int(str(d) * n))
    
    # Math constants as int
    seeds.extend([31415, 27182, 14142, 17320])  # π, e, √2, √3
    
    return seeds


if __name__ == "__main__":
    seeds = gen_negative_space()
    seeds = list(set(seeds))  # dedupe
    print(f"Generated {len(seeds)} negative-space seeds")
    
    out_file = Path(__file__).parent / "negative_space_seeds.json"
    with open(out_file, "w") as f:
        json.dump(sorted(seeds), f, indent=2)
    print(f"Saved to {out_file}")
