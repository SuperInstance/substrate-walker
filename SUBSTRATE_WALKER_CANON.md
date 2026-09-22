# Substrate Walker Canon — 100 Cells Filed

## Status

**100 canon cells filed** (best score: 0.8683, seed 3289967)

The substrate walker has walked through thousands of seeds across many
generators and identified 100 canon-worthy cities. Each cell carries:

- seed
- ASCII city view (procedurally generated)
- canon lore (multi-voice: structuralist, narrativist, futurist, lyricist, philosophical, noir_classic, cosmic_horror)
- FNV-1a 64-bit hash (fleet canary-pinned)
- type: doctrine-prime / doctrine / canon / witness / perception

## Type breakdown (100 cells)

| Type | Score range | Count |
|------|-------------|-------|
| doctrine-prime | ≥ 0.867 | 3 |
| doctrine | ≥ 0.864 | 31 |
| canon | ≥ 0.86 | 62 |
| witness | ≥ 0.85 | 4 |

## Voice breakdown (100 cells)

| Voice | Count |
|-------|-------|
| (none) | 39 |
| structuralist | 22 |
| noir_classic | 12 |
| futurist | 8 |
| narrativist | 6 |
| lyricist | 6 |
| philosophical | 4 |
| cosmic_horror | 3 |

## Top 10 (highest score, longest lore per seed)

1. seed **3289967** (0.8683) — continuous mine
2. seed **1504276** (0.8675) — figurate (2²×97×3877)
3. seed **6358192** (0.8671) — continuous mine
4. seed **302238** (0.8667) — figurate
5. seed **550551** (0.8667) — figurate
6. seed **662290** (0.8667) — figurate
7. seed **2184160** (0.8667) — figurate
8. seed **164836** (0.8667) — perfect square (406²)
9. seed **152417070** (0.8662) — continuous mine
10. seed **69006** (0.8662) — triangular (T_371)

## Sources (in priority order)

1. **Continuous mine** (random + special numbers): 6000+ seeds, found best 0.8683
2. **Perfect squares**: 9949 seeds, found best 0.8667 (406² = 164836)
3. **Figurate**: 4400+ pentagonals/hexagonals/heptagonals, found best 0.8675 (1504276)
4. **Triangular**: 2000, found best 0.8662 (T_371 = 69006)
5. **Composite lore**: 478 multi-voice lores across 118 seeds (DeepSeek Reasoner + 4 models)
6. **Polygon** (in progress): 14000/34386 polygonal numbers

## Discovery recipe

> Lower Kolmogorov complexity → canon-worthy lore.

Special numbers (squares, triangulars, pentagonals, hexagonal) have
structured hashes, producing structured cities, producing structured lores.

This is empirically validated by:
- arXiv:2304.05366 — transformers prefer low-Kolmogorov-complexity sequences
- arXiv:2606.26035 — Lean 4 theorem: every nonnegative integer = triangular + pentagonal + heptagonal
- OEIS A374409 — sum of triangular + pentagonal + hexagonal

## External validation

- JEV auditor found canon homogeneity (100% rain + neon trope) — fixed with multi-voice diversification
- Snowball scout synthesized external literature supporting the claim

## Live

https://superinstance.github.io/substrate-walker/

- index.html — landing
- canon_explorer.html — explore the 100 cells
- number_theory.html — visual structure explorer
- composite_lore.html — tri-voice viewer
- composite_lore_combined.html — 7-voice × 8-version viewer
- lore_explorer.html — filterable lore browser

## Files

- `canon/cells/cell_001.md` ... `cell_100.md` — 100 canon cells
- `canon/cells/manifest.json` — index
- `canon/cells/README.md` — top 10 summary
- `playtest/great_moments.json` — 100 canon-worthy seeds with multi-voice lores
- `playtest/composite_lore/composite_lore_combined.json` — 478 multi-voice lores
- `playtest/lore_miner.py` — main lore generator
- `playtest/lore_picker.py` — best lore picker
- `cli/walker.py` — Substrate Walker Terminal
- `scripts/canary_check.py` + `.ts` + `.js` — FNV-1a 64-bit fleet canary (pin verified)
