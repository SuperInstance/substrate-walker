// substrate_walker_rust: Rust port of the substrate walker FNV-1a hash
// References:
//   - Python: substrate-walker/playtest/lore_miner.py
//   - TypeScript: substrate-walker/scripts/canary_check.ts
//   - Fleet canary pin: 0x024a555471370b18d

use std::env;

const FNV_OFFSET: u64 = 0xcbf29ce484222325;
const FNV_PRIME: u64 = 0x100000001b3;

fn fnv1a_64(s: &str) -> u64 {
    let mut h = FNV_OFFSET;
    for b in s.as_bytes() {
        h ^= *b as u64;
        h = h.wrapping_mul(FNV_PRIME);
    }
    h
}

fn main() {
    println!("=== Substrate Walker Rust Port — FNV-1a 64-bit ===");
    println!();
    
    let reference: Vec<(&str, u64)> = vec![
        ("", 0xcbf29ce484222325),
        ("a", 0xaf63dc4c8601ec8c),
        ("foobar", 0x85944171f73967e8),
        ("abc", 0xe71fa2190541574b),
        ("café Δ 日本語", 0x024a555471370b18d),
        ("witness log is the prediction", 0x176137b542efe82a),
    ];
    
    let mut all_pass = true;
    for (input, expected) in &reference {
        let got = fnv1a_64(input);
        let status = if got == *expected { "✓" } else { "✗" };
        if got != *expected { all_pass = false; }
        println!("{} '{}': 0x{:016x} (expected 0x{:016x})", status, input, got, expected);
    }
    println!();
    if all_pass {
        println!("All 6 reference vectors match — fleet canary pinned ✓");
    } else {
        println!("MISMATCH — investigate!");
    }
}
