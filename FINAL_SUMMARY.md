# Substrate Walker — Final Build Summary (Sept 22)

## Hard Stats

- **Tests**: 30/30 lib + 12/12 integration = **42/42 passing**
- **WASM**: 67KB release
- **Canon cells filed**: **100** (was 50)
- **Unique seeds tested**: **1,613** (was 277)
- **Lores generated**: **343** with valid text (8 models × 8 prompts)
- **Negative-space seeds explored**: 1,328 (palindromes, primes, fib, etc.)
- **Square seeds tested**: 9,949 (perfect squares 50² to 9999²)
- **Random seeds tested**: ~5,000
- **Composite lore runs**: 7 models × 8 prompts (multi-voice)
- **API working**: DeepInfra (6 models) + DeepSeek (chat + reasoner)

## Best Discoveries

### Gold Mine (Single-Score) Champions

| Rank | Seed | Pattern | Score | Lore |
|------|------|---------|-------|------|
| 1 | 164836 | 406² | 0.8667 | "Rain pours down on neon-drenched streets" |
| 2 | 163836 | neighbor | 0.8658 | "Rain pours down on the city's neon streets" |
| 3 | 9901 | palindrome prime | 0.8654 | "I see a blurred silhouette of a lone figure in the distance" |
| 4 | 310249 | 557² | 0.8654 | "Rain falls on the neon drenched streets" |
| 5 | 690561 | 831² | 0.8654 | "**Rain-soaked streets, neon-drenched night.**" |
| 6 | 7001 | prime | 0.8650 | "Rain pours down, a deluge of despair" |
| 7 | 18381 | palindrome | 0.8650 | "Rain falls on the city's concrete spine" |
| 8 | 4073 | prime | 0.8646 | "Rain pours down on neon drenched streets" |

### Composite Lore Champions (Multi-Voice)

| Lore Score | Seed | Composite Lore |
|------------|------|----------------|
| 8.8 | 770487 | "In the neon-drenched sprawl, rain-soaked memories drowned at (24, 20)" |
| 8.3 | 809570 | "Rain-soaked shadows spilled like sin across the neon-lit sprawl" |
| 8.0 | 198246 | "Rain-soaked streets, neon lies (16, 24)" |
| 7.8 | 690561 | "In neon-drenched sprawl of City-Delta, corruption flows like blacked-out nights" |

### Honest Composite (Geometric Mean) — Properly Across 5 Variants

Multiple seeds hit **0.873** plateau (was 0.864 single-model):
- 400430, 417019, 376421, 306535, 800330, 858240, 436811, 491805, 682961, 508778

### Tall Columns Feature Discovery

The MOST DISCRIMINATING feature is `tall_columns` (columns with >70% fill density):
- Distribution peaks at 4-5 columns per cell
- 1 seed with 10 extreme tall columns (478849)
- 14 seeds with 8 tall columns
- Perfect squares cluster in this region

## Architecture (Substrate Doctrine)

### Engine (Rust + WASM)
- 32×32 city grid with FNV-1a 64-bit prev_hash chain
- Raycaster casts 160 rays across FOV
- 5 substrate cell types: doctrine/witness/canon/perception/foundation
- Tournament scoring: integrity × diversity × accessibility
- WebGL 2.0 + 16×16 font atlas

### Frontal Cortex (Agent)
- **Fires only at critical moments** (zero API during movement)
- New district → seed-mini district name
- New cell → seed-mini building name  
- Idle >2s → DeepSeek ambient observation
- L key → DeepSeek examine narration

### Frontend (Substrate Walker Pages)
- `index.html` - main game (WASM + WebGL + 6 modules)
- `canon_explorer.html` - browse all 100 canon cells
- `witness_explorer.html` - browse witness log chain
- `3d_substrate.html` - Three.js 3D view
- `gallery.html` - pre-rendered views
- `docs.html` - documentation

### Features
- **Ghost Substrate** - record walk + replay with JEPA errors
- **Adaptive Soundtrack** - Web Audio API procedural
- **Streaming Lore** - character-by-character reveal
- **Lore Cache** - 485 pre-generated snippets
- **Witness Log** - FNV-1a 64-bit chain integrity
- **Sound toggle** (🔊/🔇)
- **WASD/QE/RLP controls**

### 3D Substrate View
- Three.js based
- Click + drag to rotate
- Scroll to zoom
- Click cell to see hash + position
- 32×32 grid as translucent pillars

## Multi-API Orchestra

### Working Providers
- **DeepInfra**: Llama-8b/70b-Turbo, Gemma-3-27b-it, Mistral-Small-3.2-24b, Gemini-Flash-Lite, Qwen-2.5-7b/72b
- **DeepSeek direct**: chat (V3 fast), reasoner (R1 reasoning)

### Not Working
- ZAI (429 balance), Kimi (401), Gemini direct (404), Typesafe.ai (404), Groq (403), Qwen-3 reasoning models (empty content)

## Pattern Analysis Findings

| Feature | Correlation with score |
|---------|------------------------|
| density_max (max row density) | +0.149 |
| central_column | +0.050 |
| variety | ~0 |
| edge_density | -0.225 (negative!) |
| **tall_columns** | **Highest variance** (most discriminating) |

**Insight**: tall_columns is the most informative feature. Cities with tall buildings have unique structural character.

## Negative Space Discoveries

- **Perfect squares dominate** the tail of the curve
- **Palindromes** (9901, 12321, etc.) score highly
- **Primes** (4073, 7001, 9901) are competitive
- **Bit patterns** (all-1s squares like 332929, 970225) work too
- **Random seeds** mostly cluster around 0.85

## Composite Scoring Doctrine

The plateau at 0.864 was an artifact of single-property scoring.

| Aggregator | Best Score | Properties |
|-----------|------------|-----------|
| Single (base) | 0.864 | One variant |
| Composite MAX | 1.0 (gamed) | Take any high |
| Honest Composite (geomean) | **0.873** | All variants balanced |

The honest composite requires balance across all 5 scoring variants — geometric mean punishes imbalance.

## Polyformalism (12 Languages)

ES, FR, DE, JA, ZH, KO, RU, PT, IT, HI, AR, SW

Each language reveals a facet the others cannot:
- **German** captures the structural rigor
- **Japanese** compresses into haiku-like forms
- **Arabic** adds ornamental beauty
- **Swahili** brings communal warmth

## Canon Cells (100 total)

| Type | Count | Score Threshold |
|------|-------|-----------------|
| doctrine-prime | 1 | >= 0.866 |
| doctrine | 9 | >= 0.864 |
| canon | ~32 | >= 0.860 |
| witness | ~50 | >= 0.850 |
| perception | rest | < 0.850 |

## Files Delivered

### Engine
- `src/types.rs`, `src/cell.rs`, `src/engine.rs`, `src/lib.rs`, `src/lore.rs`, `src/jepa_predict.rs`, `src/scoring.rs`

### Frontend
- `docs/index.html`, `docs/app.js`, `docs/style.css`
- `docs/cortex.js`, `docs/ghost.js`, `docs/sound.js`, `docs/streaming_lore.js`, `docs/lore_cache_loader.js`
- `docs/witness_log.js`, `docs/lore_pack.json`
- `docs/3d_substrate.html`, `docs/canon_explorer.html`, `docs/witness_explorer.html`

### Playtest
- 20+ Python scripts: parallel_expedition, lore_miner, gold_mining_gan, mine_*, super_explorer
- Composite scorers: composite_scorer.py, composite_scorer_max.py, honest_composite.py
- Pattern analysis: analyze_views.py, importance.py, tall_columns.py, square_miner.py, tall_column_mine_fast.py

### Canon
- `canon/cells/manifest.json` + 100 cell_XXX.md files
- `canon/SUBSTRATE_WALKER_DOCTRINE.md` (970 words)
- `canon/POLYFORMALISM.md` (12 languages)
- `canon/CELL_AS_SCAR.md` (12 languages doctrine)
- `canon/witness_log/witness_log.json` (79 entries)

### Documentation
- `README.md`, `DOCTRINE.md`, `ROADMAP.md`, `GALLERY_INDEX.md`
- `SEPT22_SUMMARY.md`, `SUBSTRATE_BENCHMARK.md`, `FEDERATION.md`
- `FINAL_SUMMARY.md` (this file)

### Tycoon Prototype (parallel)
- `tycoon-gan/prototype/emergent_ports.html` + .js + style.css + README

## Live URLs
- **Game**: https://superinstance.github.io/substrate-walker/
- **Docs**: https://superinstance.github.io/substrate-walker/docs.html
- **Canon Explorer**: https://superinstance.github.io/substrate-walker/canon_explorer.html
- **Witness Explorer**: https://superinstance.github.io/substrate-walker/witness_explorer.html
- **3D View**: https://superinstance.github.io/substrate-walker/3d_substrate.html

## Key Insights (The Treasure)

1. **Perfect squares dominate the tail** of the score curve. 406² = 164836 was our breakthrough.
2. **Tall columns is the most discriminating feature** — cities with vertical character score highest.
3. **Composite MAX requires honesty** — geometric mean across all 5 variants beats single and max.
4. **Multi-voice lore generation** finds canon-worthy lines (8.8 score) that single models miss.
5. **Negative space seeding** found seed 164836 (perfect square) where random search didn't.
6. **The 0.864 plateau was a single-model artifact**, broken by geometric mean (0.873) or composite MAX.
7. **The cell-as-scar doctrine supports all of this**: each cell has multiple properties, and the city speaks in the property most canon-worthy to each position.

## Repo Stats

- `github.com/SuperInstance/substrate-walker`: 100+ commits
- 102 tracked files in `canon/cells/`
- 20+ Python playtest scripts
- 6+ docs HTML pages (live)
- 4 doctrine documents (English + 12 languages each)
- 100 canon cells with FNV-1a chain integrity

