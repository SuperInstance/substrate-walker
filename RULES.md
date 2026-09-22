# Substrate Walker — Rules (Discovery Criteria)

A canonical seed is one that satisfies ALL of these rules:

## 1. Low Kolmogorov Complexity (KC)

The seed's information content is low relative to its size.

Examples of low-KC seeds:
- Perfect squares: 164836 = 406², 42849 = 207²
- Triangular numbers: 69006 = T_371, 326028 = T_807
- Pentagonal: 1504276 = P_1001, 70051917 = P(12, 16) ★
- Hexagonal: 17759001 = H_2984
- Star polygons, centered polygons, etc.

## 2. Multi-Model Agreement

The lore generated for that seed is favored by multiple models.

We've tested v3 (DeepSeek), v4 (Llama-8b), v5/v6/v7 (best-of-N), v8/v9 (DeepSeek Reasoner), v10 (ZAI glm-5.3-flash).

When 5+ models independently score a seed above 0.86, the seed is strongly canon-worthy.

## 3. Distinct Multi-Voice Lores

The seed can sustain 7 voices WITHOUT all voices collapsing into the same "rain + neon" trope.

Each voice produces a distinctive lore (architecture POV, first-person POV, prophecy POV, lyric POV, ontology POV, hard-boiled POV, Lovecraftian POV).

Paraphrase penalty verified: only 1/100 close pair (was 100/100 before multi-voice diversification).

## 4. JEV Oracle Acceptance (NEW — Sept 22)

JEV (Typesafe.ai System One model) — calibrated probabilistic oracle.

A lore is ACCEPT iff:
- canon_worthy (noul) > 0.7
- distinct_voice (noul) > 0.5

Of 100 great_moments: 14/100 ACCEPT. Voice distribution: 8 lyricist, 3 structuralist, 3 noir_classic.

## 5. Hash Chain Integrity

Each cell carries FNV-1a 64-bit hash of (seed, lore, score, rank).

Verified byte-exact across 6 ports: Python + TypeScript + Rust + Bash + JavaScript ESM + C# (.NET 9).

Fleet canary pin: 0x024a555471370b18d (`fnv1a-64('café Δ 日本語')`)

## 6. Doctrine Anchoring

Each cell canonically anchors to one of 10 doctrine-prime bedrock principles:

1. substrate_is_grown — the canon is grown, not designed
2. cells_are_scars — each cell is what the walker stood in front of
3. witness_log_is_prediction — the chain is the city
4. oracle_is_heard — JEV makes the oracle a step, not a process
5. fnv_1a_canary — fleet canary is the substrate
6. lower_kolmogorov_complexity — low-KC seeds canonize
7. polyformalism — one truth, many dialects
8. jev_canon_gate — calibrated probabilistic oracle
9. no_deletion (Casey doctrine) — we archive with provenance
10. empathy_as_substrate — to understand is to walk in pattern

## 7. Doctrine-Prime Type

Cells score ≥ 0.867 (top tier) become doctrine-prime. Currently:
- 19 concrete doctrine-prime
- 10 abstract doctrine-prime (the bedrock canon about canon)

## Recipe

Given a seed:
1. Generate lore in 7 voices
2. Score each voice with multi-model (best-of-N)
3. Apply paraphrase penalty (no close pairs)
4. Query JEV oracle for canon-acceptance
5. File as canon cell with hash chain

The function that maps a seed to canon is the substrate walker itself.
