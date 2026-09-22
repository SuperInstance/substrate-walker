# Substrate Walker — Showcase Gallery

## Live Game
- 🌐 **GitHub Pages**: https://superinstance.github.io/substrate-walker/
- 📂 **Repo**: https://github.com/SuperInstance/substrate-walker
- 📊 **Tests**: 42/42 passing
- ⚡ **WASM**: 67KB release
- 🎮 **Controls**: WASD/QE movement, L for narration, R reset, 📷 screenshot

## Vision Gallery (16 SDXL-Lightning generations)

All generated via Cloudflare Workers AI with `@cf/bytedance/stable-diffusion-xl-lightning`.

### Cities & Districts
1. Cyberpunk city (the canonical aesthetic)
2. Neon cathedral (vertical scale)
3. Witness block (residential canon)
4. Canon spire (doctrine building)
5. Feral substrate (peripheral zone)
6. Perception station (JEPA prediction hub)

### Special Locations
7. Doctrine vault (substrate core)
8. Memory debt alley (forgotten canon)
9. Rain intersection (atmospheric)
10. Substrate mitosis (cell division scene)

### Generated from Gold Mines (top seeds)
11. Seed 294689 - "Shadows dance on rain-soaked walls..."
12. Seed 426053 - "Rain lashes down on rain-slick streets..."
13. Seed 137014 - "Rain pours down on the city's neon-drenched streets..."
14. Seed 5641 - "Rains pour down on the city's dark streets..."
15. Seed 800340 - "Rain-soaked streets. Shadows twist."
16. Seed 551048 - "The rain-soaked streets of Neo-Tokyo. Darkness closes in."

## Great Moments (auto-compiled from gold mines)

| Seed | Strategy | Score | Lore |
|------|----------|-------|------|
| 294689 | straight_east | 0.859 | "Shadows dance on rain-soaked walls, the city's dark heart beats on" |
| 5641 | straight_east | 0.859 | "Rains pour down on the city's dark streets" |
| 137014 | straight_east | 0.858 | "Rain pours down on the city's neon-drenched streets" |
| 426053 | straight_east | 0.857 | "Rain lashes down on rain-slick streets" |
| 551048 | straight_east | 0.857 | "The rain-soaked streets of Neo-Tokyo. Darkness closes in" |

See `playtest/GREAT_MOMENTS.md` for the full curated list.

## Features Built (Sept 22)

### Core
- Rust + WASM raycaster (67KB)
- WebGL 2.0 font atlas compositor
- FNV-1a 64-bit prev_hash chain on every cell
- Tournament scoring: integrity × diversity × accessibility

### Frontal Cortex (Agent)
- Fires only at critical moments (new district, new building, idle, examine)
- Cheap seed-mini for naming (60 tokens, fast)
- DeepSeek V3 for narration (150 tokens, deeper)
- Cache hits = free

### Visual Cortex (Prediction)
- JEPA-style prediction of next cells
- Pure WASM (no API)
- HUD shows predicted cell height

### Features
- Ghost Substrate - record + replay walks with JEPA error visualization
- Adaptive Soundtrack - Web Audio API procedural sound
- Streaming Lore - character-by-character reveal
- Lore Cache - 100 pre-generated snippets for instant responses
- Screenshot capture
- Screenshot gallery (pre-rendered views)

## Multi-API Orchestra

Models used (all via DeepInfra + DeepSeek):
- Llama-3.1-8B-Turbo (cheap)
- Llama-3.3-70B-Turbo (medium)
- Gemma-3-27b-it (medium)
- Mistral-Small-3.2-24B (medium)
- Gemini-3.1-flash-lite (flash)
- Qwen2.5-7B/72B (non-reasoning only)
- DeepSeek-V3 via direct API
- DeepSeek-R1 via direct API

Composite lore pattern:
- 3-8 models in parallel per request
- Pick longest/most descriptive
- Cross-pollination = variety

## Stats

- 100+ lore snippets cached
- 30+ vision images generated (16 curated)
- 50+ playtest runs
- 5 tycoon GAN runs
- 7 gold mine runs
- 3 tycoon deep iterations
- 200+ lore mining operations
