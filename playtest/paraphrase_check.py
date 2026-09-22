"""Paraphrase penalty — detect canon homogeneity.

Measures pairwise similarity between lores. If two lores are too similar
(N-gram overlap, ROUGE, or simple prefix), penalize the newer one.

This addresses JEV's finding that 100/100 cells were rain + neon themed.
"""
import json
import re
from collections import Counter
from pathlib import Path


def normalize(lore: str) -> str:
    """Normalize a lore string for comparison."""
    # Lowercase, strip punctuation
    s = lore.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    # Truncate to first 100 words
    words = s.split()[:100]
    return " ".join(words)


def ngram_jaccard(a: str, b: str, n: int = 3) -> float:
    """Jaccard similarity on n-grams."""
    a_norm = normalize(a)
    b_norm = normalize(b)
    
    a_grams = Counter()
    for i in range(len(a_norm.split()) - n + 1):
        ngram = tuple(a_norm.split()[i:i+n])
        a_grams[ngram] += 1
    
    b_grams = Counter()
    for i in range(len(b_norm.split()) - n + 1):
        ngram = tuple(b_norm.split()[i:i+n])
        b_grams[ngram] += 1
    
    if not a_grams or not b_grams:
        return 0.0
    
    overlap = sum((a_grams & b_grams).values())
    total = sum((a_grams | b_grams).values())
    return overlap / total


def main():
    gm_path = Path("/workspace/research/substrate-walker/playtest/great_moments.json")
    gm = json.load(open(gm_path))
    
    print(f"Loaded {len(gm)} great_moments")
    
    # Compute pairwise similarity
    lores = [m.get("lore", "") for m in gm]
    seen_lores = [l for l in lores if l and len(l) > 5]
    
    print(f"\nPairwise similarity (n=3 trigram Jaccard):")
    
    close_pairs = []
    for i in range(len(seen_lores)):
        for j in range(i+1, len(seen_lores)):
            sim = ngram_jaccard(seen_lores[i], seen_lores[j])
            if sim > 0.3:  # High similarity
                close_pairs.append((i, j, sim, gm[i]["seed"], gm[j]["seed"]))
    
    print(f"\nFound {len(close_pairs)} close pairs (similarity > 0.3):")
    for i, j, sim, s1, s2 in close_pairs[:20]:
        print(f"  seed {s1} ~ seed {s2}: {sim:.3f}")
    
    # Find unique lores
    print(f"\nLore count: {len(seen_lores)}")
    print(f"Unique normalized lores: {len(set(normalize(l) for l in seen_lores))}")
    
    # Save report
    Path("/workspace/research/substrate-walker/playtest").mkdir(exist_ok=True)
    with open("/workspace/research/substrate-walker/playtest/paraphrase_report.json", "w") as f:
        json.dump({
            "total_lores": len(seen_lores),
            "unique_lores": len(set(normalize(l) for l in seen_lores)),
            "close_pairs_count": len(close_pairs),
            "close_pairs": [
                {"seed_a": s1, "seed_b": s2, "similarity": sim}
                for _, _, sim, s1, s2 in close_pairs[:50]
            ],
        }, f, indent=2)
    
    print("\nReport saved to paraphrase_report.json")
    

if __name__ == "__main__":
    main()
