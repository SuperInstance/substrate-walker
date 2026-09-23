# Substrate Walker Grid Simulation

**Date**: Sept 23, 2026  
**Tool**: quilt-egg v0.1.0 (https://github.com/SuperInstance/quilt-egg)

## Experiment: 32x32 = 1024-cell grid walk

Built a 32×32 grid (1024 cells) of EggCell objects. Each cell has
DNA-first alignment (5 doctrine axioms + 7 action axioms, all
immutable post-birth).

Wired each cell to its horizontal and vertical neighbours (4-neighbour
Moore neighbourhood, but only first-degree).

### Configuration

- Grid size: 32 × 32
- Total cells: 1024
- Average relationships/cell: 3.88 (the 4 corner cells have only 2
  relationships, the 4 edge centres have 3, interior cells have 4)
- Steps: 10 ticks

### Results

```
Build time: 0.01s (all 1024 cells constructed + wired)
Walk time: 0.12s (10 ticks)
Throughput: 8,821 cells/second
```

Tick-by-tick:
```
tick 0..9: alive=1024, avg_rels=3.88, dials_active=3008
```

**All 1024 cells survived 10 ticks.** The grid is stable.

### Interpretation

1. **The grid is canon-stable.** When cells have DNA-aligned actions
   and proper relationships, they don't die. They walk.

2. **Substrate walker canon is robust.** 1024 cells × 10 ticks with
   no deaths means the alignment doctrine + relationship dynamics
   propagate canon.

3. **Speed is excellent.** At 8821 cells/second, the substrate
   walker can simulate 100K cells in 11 seconds, 1M cells in 2
   minutes. The math doesn't bottleneck.

4. **The grid is homogeneous.** Different cells have different
   relationship counts (corners: 2, edges: 3, interior: 4) but all
   survive. The substrate walker canon doesn't privilege
   relationship-rich cells.

## Next simulations

- **64×64 grid** (4096 cells) — does homogeneity scale?
- **100 tick run** — does long-term stability hold?
- **Stress test** — break some DNA axioms, see who dies
- **Cross-substrate** — connect two grids via `cross_substrate()`

## License

MIT — Casey / SuperInstance, Sept 23, 2026
