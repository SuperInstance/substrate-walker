# Substrate Walker — Quick Start (5 min to run)

## Prerequisites

- Python 3.10+
- pip install (no special deps)

## Run the canonical mines

```bash
cd /workspace/research/substrate-walker

# 1. Reproduce polygon mine (34386 seeds, ~30 min)
python3 playtest/pattern_analysis/polygon_miner.py

# 2. Reproduce continuous mine (6000+ seeds, ~5 min)
python3 playtest/continuous_mine.py

# 3. Reproduce figurate mine (4400+ seeds, ~3 min)
python3 playtest/pattern_analysis/figurate_miner.py
```

## Verify the polyformalism canary (6 ports)

```bash
./scripts/canary_test.sh
```

Expected: `All 6 ports agree — fleet canary pinned ✓`

## Run the JEV canon-gate

```bash
python3 playtest/jev_canon_gate.py
```

Requires `TYPESAFEAI_KEY` environment variable.

## Read the canon

- `docs/canon_v3.html` — single-page overview
- `docs/canon_explorer.html` — explore 100+10 cells
- `canon/cells/manifest.json` — programmatic access

## Build new canon cells

```bash
# Discover — find new high-scoring seeds
python3 playtest/pattern_analysis/giant_polygon_miner.py

# Score with multi-model
python3 playtest/composite_lore_v10.py

# Gate with JEV oracle
python3 playtest/jev_canon_gate.py

# File canon
python3 scripts/make_doctrine_cells.py
```

## Polyformalism dev

Add a new port by:
1. Implement FNV-1a 64-bit in your language
2. Verify against the 6 reference vectors
3. Place the implementation in `scripts/canary_check_<lang>`
4. Update `scripts/canary_test.sh` to include the new port

## Doctrine-Prime anchors

The 10 doctrine-prime cells in `canon/cells/doctrine_*.md` are the bedrock canon:

1. substrate_is_grown
2. cells_are_scars  
3. witness_log_is_prediction
4. oracle_is_heard
5. fnv_1a_canary
6. lower_kolmogorov_complexity
7. polyformalism
8. jev_canon_gate
9. no_deletion
10. empathy_as_substrate
