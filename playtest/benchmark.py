"""Substrate Walker Lore Benchmark.

Scores lores across 8 criteria. Composite = weighted sum (max 10).
"""

import json
import re
from pathlib import Path
from typing import Dict, List

# Weights (sum to 10)
WEIGHTS = {
    "atmosphere": 2.0,
    "image": 1.5,
    "brevity": 1.0,
    "texture": 1.5,
    "voice": 1.0,
    "substrate": 1.5,
    "specificity": 1.0,
    "witness": 0.5,
}

# Keyword patterns
NOIR_WORDS = ["rain", "neon", "shadow", "dark", "night", "lone", "femme", "blade",
              "chrome", "blood", "smoke", "alley", "sprawl", "dystopia"]
TEXTURE_WORDS = ["rain", "wet", "cold", "hot", "smoke", "neon", "chrome", "puddle",
                 "light", "shadow", "haze", "slick", "rough", "broken"]
SUBSTRATE_WORDS = ["cell", "scar", "chain", "witness", "canon", "substrate",
                   "doctrine", "fracture", "link", "tick", "bind"]


def score_atmosphere(lore: str) -> float:
    """Cyberpunk noir mood."""
    score = 5.0
    lore_lower = lore.lower()
    for w in NOIR_WORDS:
        if w in lore_lower:
            score += 0.5
    if "cyberpunk" in lore_lower or "noir" in lore_lower:
        score += 1.0
    return min(score, 10.0)


def score_image(lore: str) -> float:
    """Vivid visual."""
    # Has at least 2 distinct nouns
    nouns = re.findall(r'\b[A-Z][a-z]+\b', lore)
    if len(nouns) >= 3:
        return 8.0
    elif len(nouns) >= 2:
        return 6.0
    elif len(nouns) >= 1:
        return 4.0
    return 2.0


def score_brevity(lore: str) -> float:
    """Conciseness (≤40 chars ideal)."""
    n = len(lore)
    if n <= 30:
        return 10.0
    elif n <= 40:
        return 9.0
    elif n <= 60:
        return 7.0
    elif n <= 100:
        return 5.0
    else:
        return 3.0


def score_texture(lore: str) -> float:
    """Sensory detail."""
    score = 0.0
    lore_lower = lore.lower()
    for w in TEXTURE_WORDS:
        if w in lore_lower:
            score += 1.0
    return min(score, 10.0)


def score_voice(lore: str) -> float:
    """Sounds like noir."""
    if any(p in lore for p in ["...", "—", "—", ".."]):
        return 9.0
    if lore.endswith("."):
        return 7.0
    if re.search(r'[,;:]', lore):
        return 6.0
    return 5.0


def score_substrate(lore: str) -> float:
    """Substrate doctrine reference."""
    score = 0.0
    lore_lower = lore.lower()
    for w in SUBSTRATE_WORDS:
        if w in lore_lower:
            score += 2.0
    return min(score, 10.0)


def score_specificity(lore: str) -> float:
    """Not generic."""
    generic = ["city", "night", "rain"]
    count = sum(1 for g in generic if g in lore.lower())
    if count >= 2 and len(lore) < 50:
        return 8.0  # Specific because of combinations
    elif count == 0:
        return 4.0
    return 6.0


def score_witness(lore: str) -> float:
    """Feels like a record of something."""
    if "I " in lore or "you" in lore.lower() or "me" in lore.lower():
        return 8.0
    if any(w in lore.lower() for w in ["witness", "record", "logged", "noted"]):
        return 9.0
    return 5.0


def benchmark_lore(lore: str) -> Dict:
    return {
        "atmosphere": score_atmosphere(lore),
        "image": score_image(lore),
        "brevity": score_brevity(lore),
        "texture": score_texture(lore),
        "voice": score_voice(lore),
        "substrate": score_substrate(lore),
        "specificity": score_specificity(lore),
        "witness": score_witness(lore),
    }


def composite(b: Dict) -> float:
    return sum(b[k] * WEIGHTS[k] for k in WEIGHTS)


def main():
    # Load all lores
    lore_pack = json.load(open("playtest/lore_pack_combined.json"))
    
    results = []
    for seed, lore in lore_pack.items():
        if not lore or len(lore) < 5 or len(lore) > 300:
            continue
        b = benchmark_lore(lore)
        c = composite(b)
        results.append({
            "seed": seed,
            "lore": lore,
            "scores": b,
            "composite": c,
        })
    
    results.sort(key=lambda r: -r["composite"])
    
    print(f"Benchmarked {len(results)} lores")
    print(f"\n=== Top 20 by composite ===")
    for i, r in enumerate(results[:20], 1):
        print(f"{i:2}. score {r['composite']:.2f} - {r['lore'][:70]}")
    
    out_file = Path("playtest/benchmark_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    main()
