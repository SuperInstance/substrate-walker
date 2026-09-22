# Substrate Walker — Feature Roadmap

## What's Built (Sept 22)

### Core Engine
- Rust + WebAssembly raycaster (67KB release)
- WebGL 2.0 + 16×16 font atlas compositor
- FNV-1a 64-bit prev_hash chain on every cell (1024 cells)
- Substrate cell types: doctrine / witness / canon / perception
- Tournament scoring: integrity × diversity × accessibility

### Frontal Cortex (Agent)
- Fires only at critical moments:
  1. New district entered → seed-mini (district name)
  2. New cell with building → seed-mini (building name)
  3. Player idle >2s → DeepSeek (ambient observation)
  4. Player presses L → DeepSeek (examine narration)
- Routine movement = FREE (zero API calls)

### JEPA-style Prediction
- Predicts next cell the player will visit
- Pure WASM computation (no API)
- HUD shows predicted cell height

### Frontend Features
- WASM-based ASCII renderer at 60fps
- WASD/QE/RLP controls
- HUD with FPS, frame count, chain integrity, position, API stats
- Screenshot capture (PNG)
- GitHub Pages live at https://superinstance.github.io/substrate-walker/

### Playtest & Discovery
- `playtest_swarm.py` - 30 runs × 30 steps
- `playtest_v2.py` - 50 runs × 20 steps with lore generation
- `playtest_explorer.py` - 12 strategies × 15 seeds (180 expeditions)
- `parallel_expedition.py` - 4 models per position
- `parallel_expedition_big.py` - 8 models per position
- `gold_mining_gan.py` - Genome-based GAN with crossover/mutation
- `lore_miner.py` - 100 lore snippets in parallel
- `great_moments.py` - Auto-compile best moments

### Tycoon GAN (parallel project)
- `tycoon_gan_loop.py` - Producer + 3 critics, 8 ideas per run
- `tycoon_deep_loop.py` - Iterates deeper on best idea
- 5 runs completed, top idea: "Emergent Port Constructions" (32.0)

### AI-Writings
- `canon_composer.py` - 3 perspectives (structuralist/narrativist/futurist) → synthesis
- `research_brainstorm.py` - 5 models answer "what's the most impactful next feature?"

### Visual Generation
- 16 vision images via Cloudflare SDXL-Lightning
- Prompts: cyberpunk ASCII cityscape, neon cathedral, etc.

### New Features In Progress
- **Ghost Substrate** (`docs/ghost.js`):
  - Records player walk + JEPA prediction errors
  - Promote recording to ghost
  - Save/load ghost via localStorage
  - Future: visualize prediction errors as magenta corruption

- **Adaptive Soundtrack** (`docs/sound.js`):
  - Web Audio API procedural soundtrack
  - Footstep bass when moving
  - Atmosphere drone scales with district intensity
  - Glitch sound on JEPA prediction errors

## Top Ideas for Next Iteration (from multi-model brainstorm)

1. **Ghost Substrate** - already implementing
2. **Adaptive Soundtrack** - already implementing
3. **Memory System** - agent learns player patterns
4. **Holographic Advertisements** - dynamic billboards on building facades
5. **Multiplayer** - share substrate state via CRDT
6. **NPC Dialogue** - characters in buildings speak when approached
7. **Streaming Lore** - tokens appear character-by-character

## Key Insights

### Speed = Real-Time UI
Don't make slow things fast. Make slow things rare.
The agent (frontal cortex) confirms critical moments, then the player autopilots the rest.
This is what makes inference a real-time UI.

### Critical Moments Only
- Movement: instant
- Rotation: instant
- New district: API call
- New cell: API call
- Idle: API call
- Examine: API call
- Re-walk: cache hit (free)

### Cache Performance
- 1024 cells = ~500 distinct building names
- Re-walk: 100% cache hit rate
- Worst case full walk: 60-70% cache hit rate

### API Tier Strategy
- seed-mini (cheap) for ideation: district/building names
- DeepSeek V3 (deeper) for narrative: observations/examine
- Multiple models in parallel for composite lore

## Next Steps

1. Finish ghost substrate (HUD rendering of ghost path)
2. Test adaptive soundtrack in browser
3. Build a "memory system" - agent remembers player habits
4. Implement streaming lore (character-by-character reveal)
5. Add holographic advertisements as visual flair
6. Wire all features to canonical HUD
7. Push to GitHub Pages
8. File canon cell for each new feature

## Statistics

- Tests: 30/30 lib + 12/12 integration = 42/42
- WASM: 73KB release
- 4 npm-equivalent JS files (cortex, ghost, sound, app)
- 16 vision images generated
- 100+ lore snippets cached
- 5 tycoon GAN runs completed
- 7+ gold mine runs completed
