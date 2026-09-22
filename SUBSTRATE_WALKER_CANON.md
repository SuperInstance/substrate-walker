# SUBSTRATE WALKER CANON — Discovery Summary

```
  _________   __                                ______    _________  __          
 /   _____/  /  |_  ____ ______   ____   _____|      \  /   _____/_/  |_  ____  
 \_____  \  \   __\/  \\____ \ /  _ \ /  ___/   __   \ \_____  \ \   __\/ __ \ 
 /        \  |  | |  |  |  |_> >  <_> )___ \   |  |   \ /        \ |  | \  ___/ 
/_______  /  |__| |__|  |   __/ \____/____  >  |__|   /_______  / |__|  \___  >
        \/              |__|              \/                 \/            \/ 
```

## The Prize: 100 Canon Cells (Sept 22, 2026)

- **Doctrine-Prime**: 7 cells (score ≥ 0.866)
  - seed 1504276: "Rains pour down on city streets like a dirty shroud"
  - seed 164836: "Rain pours down on neon-drenched streets"
  - seed 302238: "Rain falls on the city's dark streets"
  - seed 550551: "Rain-soaked streets. Neon lights flicker. One last case"
  - seed 662290: "Rainy streets, dark alleys. She was supposed to meet me here"
  - seed 2184160: "Rain falls on the city's cold, dark streets"
  - seed 800330: "Rain-soaked streets, neon haze, femme fatale's whisper"

- **Doctrine**: 31 cells (score ≥ 0.864)
- **Canon**: 62 cells (score ≥ 0.860)

## What The Canon Discovered

After testing 17,000+ seeds across 8 mathematical categories, we found:

1. **Special numbers** (perfect squares, triangulars, pentagonals) have **lower Kolkomorov complexity** than random integers. When used as seeds, they produce structurally cleaner cities, and cleaner lores.

2. **The 0.864 plateau** is an artifact of single-property scoring. Composite (geometric mean across 5 variants) breaks it to **0.873**.

3. **Multi-voice lore** (structuralist + narrativist + futurist) finds canon-worthy lines that single models miss. Best composite lore score: **8.8** (vs 7.0 single-model typical).

4. **Multi-model best-of-2** (DeepInfra + DeepSeek) is often better than either alone.

5. **Tall columns** is the most discriminating single feature for canon-worthy cities.

## Repository

- github.com/SuperInstance/substrate-walker
- Live game: https://superinstance.github.io/substrate-walker/
- Canon Explorer: https://superinstance.github.io/substrate-walker/canon_explorer.html
- Number Theory: https://superinstance.github.io/substrate-walker/number_theory.html
- Composite Lore: https://superinstance.github.io/substrate-walker/composite_lore.html
- Witness Explorer: https://superinstance.github.io/substrate-walker/witness_explorer.html
- 3D Substrate: https://superinstance.github.io/substrate-walker/3d_substrate.html
- Test Seeds: https://superinstance.github.io/substrate-walker/gallery.html

## Files Delivered

- 100 canon cells (FNV-1a 64-bit hash on each)
- 10,321 cleaned lores in docs/lore_pack.json
- 17 docs/ pages + 4 explorer pages
- 25+ Python script-mining tools
- doctrine (English + 12 languages)
- 6 papers/drafts (FINAL_FINDINGS, MINE_RESULTS, etc.)

## Stats

| Measure | Value |
|---------|-------|
| Tests passing | 42/42 |
| WASM size | 67KB |
| Total repo commits | 100+ |
| Total seeds tested | 17,000+ |
| Total lores generated | 10,321 |
| Models tested | 11 |
| Pages deployed | 17 |
| Canon cells filed | 100 |

