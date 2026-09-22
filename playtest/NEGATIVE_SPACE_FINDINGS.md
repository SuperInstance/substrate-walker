# Negative-Space Mining Findings

## Hypothesis

We had plateaued at 0.864 (seed 800330). The "negative space" — seeds we hadn't tested — might hold a > 0.870 breakthrough.

## Methodology

Generated 1328 seeds in unexplored categories:
- Negative numbers (-1 to -1,000,000)
- Very large positives (10M to 999M)
- All-1s bit patterns (7, 15, 31, ... 65535)
- 5-digit palindromes (12321, 54745, ...)
- Primes (selected samples)
- Perfect squares (1² to 999²)
- Fibonacci numbers
- Powers of 2 and 10
- Mathematical constants as ints (31415, 27182, 14142, 17320)
- Repeated digits (111, 2222, 55555)

For each, did a quick scoring pass (36 positions, single path).

## Results

- **Total seeds tested**: 1328
- **Best score found**: 0.863
- **Seeds scoring >= 0.87**: 0

The plateau is real.

## Top Negative-Space Discoveries

| Rank | Seed | Score | Notes |
|------|------|-------|-------|
| 1 | 7396 | 0.863 | Negative space bit pattern (2*sqrt=...) |
| 2 | 18881 | 0.863 | Negative space bit pattern |
| 3 | 620944 | 0.863 | High-bit pattern |
| 4 | 332929 | 0.863 | Negative space all-1s |
| 5 | 401956 | 0.863 | Mid-range prime |

## Analysis

The 0.864 ceiling appears to be a structural feature of:
1. The 32×32 grid geometry
2. The 5-criteria scoring function (density × vertical × center × variety × horizon)
3. The cell height distribution

To break 0.870, we would need to either:
1. **Change the scoring function** (different weights)
2. **Try a different grid size** (64×64 = 4096 cells)
3. **Compose multiple scoring functions** (variety_score + density_score etc.)
4. **Use composite lore generation** (multiple models vote)

The next frontier: **composite scoring** — instead of one model voting on the score, have 3-5 models each score independently, then average. This is the polyformalism doctrine applied to scoring itself.

