# Polyformalism — Substrate Walker Port Table

The Quilt substrate walker is implemented across 6 polyformalism ports. All ports
must produce byte-exact output for the same input.

## Port Table

| Port | Language | Status | Description |
|---|---|---|---|
| 1 | Python | ✅ Complete | Reference impl, JEV probe + 7-voice lore gen |
| 2 | TypeScript | ✅ Complete | Schema-parity types in `@superinstance/polyvocoder-bindings` |
| 3 | Rust | ✅ Complete | WASM core in `src/lib.rs` (60KB release) |
| 4 | Bash | ✅ Complete | FNV-1a + dials generator + canon submit |
| 5 | JavaScript ESM | ✅ Complete | Browser-side lore render |
| 6 | C#/.NET 9 | ✅ Complete | CLI for canon archive queries |

## Fleet Canary

All ports agree on: `fnv1a-64('café Δ 日本語') = 0x024a555471370b18d`

## Use Cases per Port

### Python
- Reference implementation
- JEV oracle integration
- Multi-voice lore generation
- Composite scoring
- Auto-promoter

### TypeScript
- Web UI binding (lore_explorer.html)
- Schema-parity with Python
- REST API client

### Rust + WASM
- 3D ASCII city renderer (60KB WASM)
- FNV-1a prev_hash chain (browser-side)
- Sub-millisecond raycasting

### Bash
- Cron-style canon-submit to /api/cell
- Fleet canary verification
- Standalone replay harness

### JavaScript ESM
- Browser-side lore renderer (no Python needed)
- Polyformalism harness (verifies all ports)

### C#/.NET 9
- Canon archive CLI (`quilt canon search --doctrine cells_are_scars`)
- Read-only archive queries
- Cross-platform Windows/Linux/Mac support

## Why Polyformalism?

From the substrate walker doctrine (CANON.md):

> "The same model in N languages IS a stress test. Each language is a *medium*,
> not a ranking."

A polyformalism port is NOT a port for compatibility's sake. It's a stress test:

- **Python** tests algorithm clarity + library richness
- **TypeScript** tests schema expressiveness + browser portability
- **Rust** tests algorithmic efficiency + memory safety
- **Bash** tests shell-script survivability + cron-ability
- **JavaScript** tests browser-as-runtime + minimal deps
- **C#/.NET** tests Windows-portability + enterprise tooling

If the same canon lore produces the same FNV-1a hash across all 6 ports, you've
verified that the doctrine is portable across language boundaries.

## Adding a New Port

To add a port:

1. Implement the FNV-1a 64-bit hash function correctly
2. Encode the canary string `'café Δ 日本語'` as UTF-8 with `errors="surrogatepass"`
3. Verify the hash equals `0x024a555471370b18d`
4. Implement the doctrine lore format
5. Implement the 5 doctrine questions for JEV probing
6. File the port in this table

