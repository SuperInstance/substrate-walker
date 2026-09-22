# Substrate Walker

> A 3D ASCII city where every building is a canon cell. JEV frontal-cortex generates districts on critical moments only.

## What is this?

Substrate Walker is a browser-based 3D ASCII city built on:

- **Rust + WebAssembly** (no_std, 60KB release) — raycasting engine
- **WebGL 2.0** — GPU compositor + font atlas
- **FNV-1a 64-bit prev_hash chain** — every building is a substrate cell

The twist: **the agent only fires at critical moments**, like a human frontal cortex.
Routine movement is free. The agent confirms the zipper parts are married, then
you look up and zip the coat the rest of the way while walking.

## Frontal Cortex — Critical Moments Only

The agent (JEV/JEPA via DeepInfra) only intervenes when something genuinely
new happens:

| Trigger | API call | Model |
|---------|----------|-------|
| Player enters a new **district** (8-cell region) | District name | seed-mini (cheap) |
| Player enters a new **cell** with a building | Building name | seed-mini (cheap) |
| Player **idle for >2s** | Ambient observation | DeepSeek (deeper) |
| Player presses **L** (examine) | On-demand narration | DeepSeek (deeper) |

**Routine movement = zero API calls.** This is the speed trick that makes
inference into a real-time UI.

## Build

```bash
# Native
cargo test --lib
cargo run --release --example text_render

# WASM
cargo build --release --target wasm32-unknown-unknown --features wasm
cp target/wasm32-unknown-unknown/release/substrate_walker.wasm web/walker.wasm

# Serve
cd web && python3 -m http.server 8080
```

## Controls

- **WASD / arrows**: walk
- **Q/E**: turn
- **R**: reset to (16, 16)
- **L**: examine (triggers DeepSeek narration)
- **P**: capture PNG screenshot

## Architecture

```
┌─────────────────────────────────────────────┐
│              Rust Core (WASM)               │
│  [CityGrid 32×32 cells + FNV-1a chain]      │
│         ↓                                   │
│  [Raycaster::cast(camera, grid)]            │
│         ↓                                   │
│  [Vec<PackedCell> of 160×60 cells]          │
│         ↓                                   │
│  [Zero-copy WASM memory buffer]             │
└─────────────────────────────────────────────┘
                ↓ (raw memory read)
┌─────────────────────────────────────────────┐
│           Browser (WebGL 2.0)               │
│  [JS reads Uint8Array from WASM heap]       │
│         ↓                                   │
│  [texImage2D → texture slot 0]              │
│         ↓                                   │
│  [Fragment shader → font atlas → screen]    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│      Frontal Cortex (JavaScript)            │
│  [Critical-moment detector]                 │
│         ↓                                   │
│  [Cache: cell → lore, district → lore]      │
│         ↓                                   │
│  [DeepInfra API (seed-mini + DeepSeek)]     │
│         ↓                                   │
│  [HUD lore display]                         │
└─────────────────────────────────────────────┘
```

## Substrate Cells

Each cell in the city grid carries:
- `x, y`: position
- `height`: building height (0 = empty street)
- `cell_type`: 0=doctrine, 1=witness, 2=canon, 3=perception
- `prev_hash`: FNV-1a 64-bit hash of previous cell
- `hash`: FNV-1a 64-bit hash of self + prev_hash

The chain integrity is verified across all 1024 cells. Tampering with any
cell breaks the chain.

## Fleet Canary

The FNV-1a 64-bit canary for `"café Δ 日本語"` is `0x24a555471370b18d`,
verified across all SuperInstance substrate-aware repos.

## License

MIT
