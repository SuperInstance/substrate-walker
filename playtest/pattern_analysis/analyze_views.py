"""Pattern Analysis - find what view features correlate with high composite scores.

This is the negative space of the score function itself.
"""

import sys
import json
import random
import numpy as np
from pathlib import Path

sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view as base_score_view


def analyze_view_features(view, densities):
    """Extract features from an ASCII view."""
    h = len(view)
    w = len(view[0]) if view else 0
    if h == 0 or w == 0:
        return {}

    # Basic counts
    density = sum(sum(1 for c in row if c != ' ') for row in view) / (h * w)

    # Glyph variety
    glyphs = set(c for row in view for c in row if c != ' ')
    variety = len(glyphs) / 15

    # Vertical structure
    center_col = [view[i][w//2] if view[i] and w//2 < len(view[i]) else ' ' for i in range(h)]
    has_central_column = sum(1 for c in center_col if c != ' ') / h

    # Edge contrasts
    edge_density = sum(sum(1 for c in row[0] if c != ' ') + sum(1 for c in row[-1] if c != ' ')
                      for row in view) / (h * 2)

    # Density distribution
    row_densities = [sum(1 for c in row if c != ' ') / w for row in view]
    density_variance = float(np.var(row_densities))
    density_max = max(row_densities)
    density_mean = sum(row_densities) / h

    # Horizon (center of view)
    horizon_band = row_densities[h//2-3:h//2+3] if h//2-3 >= 0 else row_densities
    horizon_active = sum(1 for d in horizon_band if d > 0.2) / len(horizon_band)

    # Symmetry
    symmetry_h = sum(1 for y in range(h) if view[y] == view[h-1-y]) / h
    symmetry_v = sum(1 for x in range(w) if [view[y][x] for y in range(h)] == [view[y][w-1-x] for y in range(h)]) / w if w > 0 else 0

    # Most common glyph
    glyph_counts = {}
    for row in view:
        for c in row:
            if c != ' ':
                glyph_counts[c] = glyph_counts.get(c, 0) + 1
    most_common_freq = max(glyph_counts.values()) / (h * w) if glyph_counts else 0

    # Unique in center
    center_block = [view[y][w//2 - 5:w//2 + 6] for y in range(h//2 - 3, h//2 + 4) if 0 <= y < h and view[y]]
    center_chars = set()
    for block in center_block:
        for c in block:
            if c != ' ':
                center_chars.add(c)
    center_variety = len(center_chars) / 15

    return {
        "density": density,
        "variety": variety,
        "central_column": has_central_column,
        "edge_density": edge_density,
        "density_variance": density_variance,
        "density_max": density_max,
        "density_mean": density_mean,
        "horizon_active": horizon_active,
        "symmetry_h": symmetry_h,
        "symmetry_v": symmetry_v,
        "most_common_freq": most_common_freq,
        "center_variety": center_variety,
    }


def main():
    # Sample seeds (the top 50 + random)
    gm = json.load(open("/workspace/research/substrate-walker/playtest/great_moments.json"))
    seeds = [m["seed"] for m in gm[:50]]
    rng = random.Random(42)
    seeds.extend([rng.randint(100000, 999999) for _ in range(50)])

    data = []
    print(f"Analyzing {len(seeds)} seeds...")
    for i, seed in enumerate(seeds):
        # Best position for this seed
        best_score = 0
        best_features = None
        for x in range(8, 28, 4):
            for y in range(8, 28, 4):
                view, densities = render_view(seed, x, y, 0)
                features = analyze_view_features(view, densities)
                # Quick score
                score = features["density"] * 0.3 + features["variety"] * 0.3 + features["horizon_active"] * 0.4
                if score > best_score:
                    best_score = score
                    best_features = features
        
        if best_features is None:
            continue
        
        # Get the actual base score too
        view, densities = render_view(seed, 16, 16, 0)
        base = base_score_view(view, densities)
        
        entry = {
            "seed": seed,
            "base_score": base,
            "feature_score": best_score,
            **best_features,
        }
        data.append(entry)
    
    # Correlations
    import statistics
    keys = list(data[0].keys())
    keys.remove("seed")
    
    print(f"\n=== Feature correlations with base score ===")
    for k in keys:
        values = [d[k] for d in data]
        scores = [d["base_score"] for d in data]
        # Pearson correlation
        try:
            n = len(values)
            mean_v = sum(values) / n
            mean_s = sum(scores) / n
            cov = sum((values[i] - mean_v) * (scores[i] - mean_s) for i in range(n)) / n
            std_v = (sum((v - mean_v)**2 for v in values) / n) ** 0.5
            std_s = (sum((s - mean_s)**2 for s in scores) / n) ** 0.5
            corr = cov / (std_v * std_s) if std_v * std_s > 0 else 0
            print(f"  {k:20}: r = {corr:+.3f}")
        except:
            pass
    
    # Top features by correlation
    print(f"\n=== Top features positively correlated ===")
    
    out = {
        "analyzed_at": str(datetime.now()),
        "total_seeds": len(seeds),
        "features": data,
    }
    
    out_file = Path(__file__).parent / "feature_analysis.json"
    with open(out_file, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    from datetime import datetime
    main()
