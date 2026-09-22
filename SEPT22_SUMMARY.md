# Substrate Walker — September 22 Build Summary

## Stats

- **42/42 tests pass** (30 lib + 12 integration)
- **67KB WASM release**
- **485 lore snippets** in cache
- **242 unique seeds** tested
- **7+ gold mine runs** completed
- **6 tycoon GAN runs**
- **3+ parallel exploration scripts**
- **3 lore factory iterations** (193 + 240 + 195 lores)
- **All-time best: seed 800330 (0.864)**

## Architecture

### Engine (Rust)
- 32×32 city grid with FNV-1a 64-bit prev_hash chain
- Raycaster casts 160 rays across FOV
- 5 substrate cell types: doctrine/witness/canon/perception/foundation
- Tournament scoring: integrity × diversity × accessibility
- WebGL 2.0 + 16×16 font atlas compositor

### Frontal Cortex (Agent)
- **Fires ONLY at critical moments:**
  1. New district entered → seed-mini district name
  2. New cell with building → seed-mini building name
  3. Player idle >2s → DeepSeek ambient observation
  4. Player presses L → DeepSeek examine narration
- Routine movement = ZERO API calls
- 60-70% cache hit rate on full walk
- 100% cache hit rate on re-walk

### JEPA Prediction (Visual Cortex)
- Predicts next cells based on velocity vector
- Pure WASM (no API)
- HUD shows predicted cell height

### Frontend Features
- WASM ASCII renderer at 60fps
- WASD/QE/RLP controls
- HUD with FPS, chain integrity, position, API stats
- Screenshot capture
- **Ghost Substrate** - record + replay with JEPA error visualization
- **Adaptive Soundtrack** - Web Audio API procedural sound
- **Streaming Lore** - character-by-character reveal
- **Lore Cache Loader** - instant responses from 485 pre-generated snippets
- Sound toggle (🔊/🔇)
- Live at https://superinstance.github.io/substrate-walker/

### Multi-API Orchestra
- DeepInfra: Llama-8b (cheap), Llama-70b, Gemma-3-27b, Mistral-24b, Gemini-Flash-Lite, Qwen-7b/72b
- DeepSeek direct: chat (V3), reasoner (R1)
- Composite lore pattern: 3-8 models in parallel per request

## Top Discoveries

### Gold Mine Champions
| Seed | Score | Lore |
|------|-------|------|
| 800330 | 0.864 | "Rain-soaked streets, neon haze, femme fatale's whisper in the darkness" |
| 654321 | 0.864 | "Rain pours down on streets of New Erebo" |
| 390172 | 0.863 | "Rain-soaked streets reflected city's neon despair" |
| 272801 | 0.863 | "Rain-soaked streets. Shadows hide secrets" |
| 270801 | 0.862 | "Rain pours on the streets of Neo-Tokyo. Dark alleys hide secrets" |
| 997878 | 0.862 | "A rainy night in the sprawl. The city never sleeps, but neither do its secrets" |
| 331481 | 0.862 | "The rain pours down, a cold shroud over the city's decay" |

### Tycoon GAN Champions
| Idea | Score | Type |
|------|-------|------|
| "Emergent Port Constructions: Customizable Modular Portals" | 32.0 | gameplay/economy |
| "Route Controller's Dilemma" | 31.7 | gameplay |
| "Weather-Driven Route Optimization (WDRO)" | 31.0 | gameplay |
| "Fleet Composition Reimagined" | 29.0 | gameplay/economy |
| "Port Resilience" | 28.7 | gameplay/economy |
| "Voyage Insurance and Risk Management" | 27.3 | gameplay |

## Key Insights

1. **Speed = Real-Time UI**
   - Don't make slow things fast. Make slow things rare.
   - Agent confirms critical moments, player autopilots the rest.
   - 1000ms API call is fine if 1×/10sec, not 60×/sec.

2. **Cache Everything**
   - 485 lores pre-generated → instant responses
   - Re-walk = 100% cache hit
   - First walk = 60-70% cache hit

3. **Composite is King**
   - 3-8 models per request → variety
   - Cross-pollination across models → discovery
   - Pick longest/most descriptive → best quality

4. **GAN Iterations Pay Off**
   - 100+ generations find gems
   - Crossover + mutation across seeds → exploration
   - Best seeds cluster around 0.86 plateau

## Files Created (Sept 22)

### Core
- `src/types.rs`, `src/cell.rs`, `src/engine.rs`, `src/lib.rs`, `src/lore.rs`, `src/jepa_predict.rs`, `src/scoring.rs`

### Frontend
- `docs/index.html`, `docs/app.js`, `docs/style.css`
- `docs/cortex.js`, `docs/ghost.js`, `docs/sound.js`, `docs/streaming_lore.js`, `docs/lore_cache_loader.js`

### Playtest & Discovery
- `playtest/playtest_v2.py`, `playtest/playtest_explorer.py`
- `playtest/parallel_expedition.py`, `playtest/parallel_expedition_big.py`
- `playtest/lore_miner.py`, `playtest/lore_factory_v2.py`, `playtest/lore_factory_v3.py`
- `playtest/super_explorer.py`, `playtest/super_explorer_v2.py`

### Gold Mines
- `playtest/gan/gold_mining_gan.py`
- 7 mine outputs: mine_001, mine_004, mine_005, mine_big, mine_long, mine_mega, mine_huge, mine_massive, mine_quantum
- 5 neighborhood mines: 800340, 390222, 271801, 654321, ...

### Tycoon GAN
- `tycoon-gan/tycoon_gan_loop.py`, `tycoon_deep_loop.py`
- 6 runs: run_001-006
- 2 deep iterations: deep_gambit, deep_ports, deep_route

### Canon & Documentation
- `canon/canon-2026-09-22.md` (canon cell filed)
- `ROADMAP.md`, `GALLERY_INDEX.md`, `SEPT22_SUMMARY.md`
