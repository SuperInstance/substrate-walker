"""Canon Scorer - uses existing canon as similarity anchor.

The canon-worthy score of a new lore is its similarity to existing canon.
We use TF-IDF-like keyword overlap with the top 50 canon cells.
"""

import json
import math
import re
from pathlib import Path


# Stop words to ignore
STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "on", "in", "at", "of",
              "and", "or", "to", "for", "with", "as", "by", "this", "that", "i",
              "you", "we", "they", "it", "be", "have", "has", "had"}


def tokenize(text):
    """Extract lowercase words."""
    text = text.lower()
    words = re.findall(r'\b[a-z]+\b', text)
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def keyword_overlap(text, canon_keywords):
    """How many canon keywords appear in text?"""
    tokens = set(tokenize(text))
    overlap = tokens & canon_keywords
    return len(overlap) / max(len(tokens), 1)


def canon_similarity(text, canon_lores):
    """TF-IDF style similarity to canon corpus."""
    text_tokens = tokenize(text)
    if not text_tokens:
        return 0.0
    
    # IDF: how rare is each word in the canon?
    doc_freq = {}
    for lore in canon_lores:
        if not lore:
            continue
        unique_words = set(tokenize(lore))
        for w in unique_words:
            doc_freq[w] = doc_freq.get(w, 0) + 1
    
    n_docs = len([l for l in canon_lores if l])
    
    # Score text by IDF-weighted keyword coverage
    score = 0
    for word in set(text_tokens):
        if word in doc_freq:
            # Rare words (low doc_freq) score higher
            idf = math.log(n_docs / (doc_freq[word] + 1))
            score += idf
    
    return score / max(len(set(text_tokens)), 1)


def main():
    # Load canon lores
    manifest = json.load(open("/workspace/research/substrate-walker/canon/cells/manifest.json"))
    canon_lores = [e["lore"] for e in manifest["entries"] if e.get("lore")]
    
    # Build canon keywords
    canon_keywords = set()
    for lore in canon_lores:
        if lore:
            canon_keywords.update(tokenize(lore))
    
    print(f"Canon: {len(canon_lores)} lores, {len(canon_keywords)} unique keywords")
    
    # Score the great moments against canon
    gm = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))
    
    scored = []
    for m in gm:
        if not m.get("lore"):
            continue
        sim = canon_similarity(m["lore"], canon_lores)
        overlap = keyword_overlap(m["lore"], canon_keywords)
        m["canon_similarity"] = sim
        m["keyword_overlap"] = overlap
        scored.append(m)
    
    scored.sort(key=lambda x: -x["canon_similarity"])
    
    print(f"\n=== Top 10 by canon similarity (excluding self) ===")
    for m in scored[:10]:
        print(f"  rank {m['rank']}: seed {m['seed']:7} sim={m['canon_similarity']:.3f} overlap={m['keyword_overlap']:.3f}")
        print(f"    {m['lore'][:70]}")
    
    out_file = Path(__file__).parent / "canon_scores.json"
    with open(out_file, "w") as f:
        json.dump(scored, f, indent=2)
    print(f"\nSaved {len(scored)} to {out_file}")


if __name__ == "__main__":
    main()
