# Substrate Walker — Canon

The substrate as a 3D ASCII city. Each cell is a building. The player walks
the canon itself.

## Core Doctrine

- **Cell = building**: every building in the city is a substrate cell
  carrying FNV-1a 64-bit prev_hash.
- **Frontal cortex = critical moments only**: the agent (JEV/JEPA) does not
  narrate every frame. It fires on: new district, new cell with a building,
  idle >2s, examine-key.
- **Speed = real-time UI**: routine movement is FREE. API calls only happen
  at moments that matter.

## The 4 Critical Moments

1. **New district entered** → seed-mini generates district name
2. **New cell with a building** → seed-mini generates building name
3. **Player idle for >2s** → DeepSeek ambient observation
4. **Player presses L** → DeepSeek on-demand narration

## Cache Strategy

- Cell → lore: keyed by cell coordinates
- District → lore: keyed by district coordinates (8-cell regions)
- Narrative thread: per-district deepseek context (last 3 observations)
- Cache size: 500 entries max

## API Tier Strategy

- **seed-mini** (Qwen2.5-7B-Instruct): 60 max_tokens, fast, cheap
  - District names (2-4 words)
  - Building names (3-6 words)
- **DeepSeek V3**: 150 max_tokens, slower, more thoughtful
  - Narrative observations (one sentence)
  - Examine narration (one vivid sentence)

## Fleet Alignment

- FNV-1a 64-bit canary verified: `0x24a555471370b18d` for `"café Δ 日本語"`
- Chain integrity: 22/22 tests pass
- WASM release size: 67KB
- Native binary: <1MB
