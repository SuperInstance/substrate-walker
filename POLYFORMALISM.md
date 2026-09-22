# Substrate Walker — Polyformalism Port

The substrate walker is a canonical member of the substrate-* fleet. As such,
it must follow the polyformalism principle: **the same algorithm expressed in
many languages, all agreeing byte-exact on the fleet canary**.

## Fleet canary

`'café Δ 日本語'` → `0x024a555471370b18d` (FNV-1a 64-bit)

This is the canary that ties every substrate-* project together.

## Reference vectors (verified by all ports)

| Input | FNV-1a 64-bit |
|-------|---------------|
| `""` | `0xcbf29ce484222325` |
| `"a"` | `0xaf63dc4c8601ec8c` |
| `"foobar"` | `0x85944171f73967e8` |
| `"abc"` | `0xe71fa2190541574b` |
| `"café Δ 日本語"` | `0x024a555471370b18d` |
| `"witness log is the prediction"` | `0x176137b542efe82a` |

## Ports (4 verified implementations)

| Language | File | Notes |
|----------|------|-------|
| Python 3 | `scripts/canary_check.py` | reference |
| TypeScript | `scripts/canary_check.ts` + `canary_check.js` | runs on Node |
| Rust | `scripts/canary_check_rust.rs` | compiled to `canary_check_rust` |
| Bash | `scripts/canary_check_bash.sh` | uses 64-bit bash arithmetic |
| JavaScript ESM | `scripts/canary_check.mjs` | Node 18+ BigInt |

All five agree on the fleet canary. Run `./scripts/canary_test.sh` to verify.

## Why polyformalism matters

When the substrate walker hashes a canon cell, the hash must be reproducible
across all the substrate-* projects — regardless of language, runtime, or
deployment platform. The canary is the seed that proves byte-exact agreement.

This is the same polyformalism principle as:
- The `quilt-substrate-meta` C99 implementation (proves the algebra)
- The 24-repo polyformalism fleet (ports the cell algebra across languages)
- The 12-language witness-log encoding (one truth, many dialects)

## Polyformalism scope

Substrate walker's polyformalism has 4 ports today:
1. Python (3.10+)
2. TypeScript (Node 18+)
3. Rust (1.65+)
4. Bash (4.0+ for 64-bit arithmetic)
5. JavaScript ESM (Node 18+, BigInt support)

Future ports: Go (when available), Zig, OCaml, Haskell, Lua, Ruby, PHP, Java.

Each port must:
- Pass the fleet canary (6 reference vectors)
- Use the same FNV-1a 64-bit constants
- Produce byte-exact output for all inputs
