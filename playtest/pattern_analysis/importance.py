"""Find the REAL feature importance across many positions per seed."""

import sys
import json
import random
import numpy as np
from pathlib import Path

sys.path.insert(0, '/workspace/research/substrate-walker/playtest')
from playtest_v2 import render_view, score_view as base_score_view


def features(view, densities):
    """Same as before."""
    h = len(view)
    w = len(view[0]) if view else 0
    if h == 0 or w == 0:
        return {}

    density = sum(sum(1 for c in row if c != ' ') for row in view) / (h * w)
    glyphs = set(c for row in view for c in row if c != ' ')
    variety = len(glyphs) / 15

    # Density bins by row
    row_densities = [sum(1 for c in row if c != ' ') / w for row in view]
    density_max = max(row_densities)
    density_mean = sum(row_densities) / h
    density_min = min(row_densities)

    # Vertical columns
    col_densities = []
    for x in range(w):
        count = 0
        for y in range(h):
            if view[y] and x < len(view[y]) and view[y][x] != ' ':
                count += 1
        d = count / h if h > 0 else 0
        col_densities.append(d)
    col_max = max(col_densities) if col_densities else 0

    # Has narrow column (a single tall building)
    tall_columns = sum(1 for cd in col_densities if cd > 0.7)

    # Glyph transitions
    transitions = 0
    for y in range(h):
        for x in range(w-1):
            a = view[y][x] != ' '
            b = view[y][x+1] != ' '
            if a != b:
                transitions += 1

    # Numbers/symbols vs letters
    symbols = sum(1 for row in view for c in row if c in "!@#$%^&*()")
    letters = sum(1 for row in view for c in row if c.isalpha())

    return {
        "density": density,
        "variety": variety,
        "density_max": density_max,
        "density_mean": density_mean,
        "density_min": density_min,
        "col_max": col_max,
        "tall_columns": tall_columns,
        "transitions": transitions / 100,
        "symbols": symbols / 10,
        "letters": letters / 10,
    }


def main():
    # Big analysis across many seeds × many positions
    rng = random.Random(123)
    seeds = [rng.randint(100000, 999999) for _ in range(50)]
    
    data = []
    print(f"Analyzing {len(seeds)} seeds × many positions...")
    for seed in seeds:
        best_score = 0
        best_features = None
        for x in range(4, 28, 2):
            for y in range(4, 28, 2):
                view, densities = render_view(seed, x, y, 0)
                f = features(view, densities)
                # Quick heuristic score
                quick = f.get("density", 0) * 0.3 + f.get("variety", 0) * 0.3 + f.get("density_max", 0) * 0.4
                if quick > best_score:
                    best_score = quick
                    best_features = f
        if best_features:
            data.append({
                "seed": seed,
                "feature_score": best_score,
                **best_features,
            })
    
    # Find which features BEST predict the feature_score
    feature_keys = ['density', 'variety', 'density_max', 'density_mean',
                    'density_min', 'col_max', 'tall_columns',
                    'transitions', 'symbols', 'letters']
    
    print(f"\n=== Top features by variance (high variance = more discriminating) ===")
    for k in feature_keys:
        values = [d[k] for d in data]
        variance = np.var(values)
        print(f"  {k:18}: var = {variance:.4f}, mean = {np.mean(values):.3f}")
    
    # Find the top contributing feature
    print(f"\n=== Feature ranking by max value occurrence ===")
    top_by_score = sorted(data, key=lambda d: -d["feature_score"])[:10]
    for d in top_by_score:
        print(f"  score {d['feature_score']:.3f} seed {d['seed']}: density={d['density']:.3f}, variety={d['variety']:.3f}, density_max={d['density_max']:.3f}, tall_columns={d['tall_columns']}")
    
    out_file = Path(__file__).parent / "importance.json"
    with open(out_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved {len(data)} to {out_file}")


if __name__ == "__main__":
    main()
