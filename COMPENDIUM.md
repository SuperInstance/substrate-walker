# Substrate Walker — Compendium (Sept 22 evening)

## One-page summary

The substrate walker is a cellular-architecture canon-discovery engine. It walks through 38,000+ procedurally-generated ASCII cities and identifies the canon-worthy ones via multi-model scoring.

**NEW ALL-TIME BEST (Sept 22):** seed 70051917 (polygon P(12, 16)) = 0.8692

**Canon filed:** 110 cells (100 concrete + 10 doctrine-prime abstract)

**Polyformalism:** 6 verified ports (Python + TypeScript + Rust + Bash + JS ESM + C#)
**Oracle:** JEV (Typesafe.ai System One model) for canon-acceptance
**Composite lore:** 478 multi-voice lores across 118 seeds

## What is canonical?

A canon cell is "canonical" when:
1. **Low Kolmogorov complexity** — seed has structure (special number, polygonal, perfect square)
2. **Multi-model agreement** — DeepSeek + Llama + Mistral + Gemma + ZAI score it highly
3. **Multi-voice coherence** — 7 voices produce distinct lore (not 1 voice × 7 aliases)
4. **JEV acceptance** — p>0.7 canon + p>0.5 distinct (calibrated oracle)
5. **Paraphrase diversity** — trigram Jaccard < 0.3 vs all other canon cells

## Discovery recipe (validated)

> **Lower Kolmogorov complexity → canon-worthy lore.**

This is consistent with:
- arXiv:2304.05366 (transformers prefer low-KC sequences)
- arXiv:2606.26035 Lean 4 theorem (every n = triangular + pentagonal + heptagonal)
- OEIS A374409 (sum of triangular + pentagonal + hexagonal)

The substrate walker's empirical claim is reproducible across:
- 8 generators (polygon, square, triangle, figurate, fibonacci, special, etc.)
- 8 model versions (v3 through v10)
- 7 voices (structuralist, narrativist, futurist, lyricist, philosophical, noir_classic, cosmic_horror)

## Multi-voice lore

Each canon cell can speak in 7 voices. The longest lore per voice survives.
Combined dataset: 478 multi-voice lores across 118 seeds.

| Voice | Best for |
|-------|----------|
| structuralist | Concrete architecture |
| narrativist | First-person POV |
| futurist | Prophecy, organism |
| lyricist | Compressed image |
| philosophical | Ontology |
| noir_classic | Hard-boiled detective |
| cosmic_horror | Lovecraftian geometry |

## JEV oracle (Typesafe.ai)

JEV is a System One model — returns calibrated probabilities instead of text.
Used for canon-acceptance gate on 100 great_moments.
Result: 14/100 ACCEPT. Voice distribution: 8 lyricist, 3 structuralist, 3 noir_classic.

## Polyformalism

Same algorithm in 6 languages, all byte-exact on the fleet canary.
The canary `0x024a555471370b18d` ties every substrate-* project together.

| Port | File | Verified |
|------|------|----------|
| Python | `scripts/canary_check.py` | ✓ |
| TypeScript | `scripts/canary_check.ts` | ✓ |
| Rust | `scripts/canary_check_rust.rs` | ✓ |
| Bash | `scripts/canary_check_bash.sh` | ✓ |
| JS ESM | `scripts/canary_check.mjs` | ✓ |
| C# / .NET 9 | `scripts/canary_check_cs` + `cs/` | ✓ |

## Live URLs

- https://superinstance.github.io/substrate-walker/
- /canon_v3.html — single-page canon showcase (NEW)
- /canon_explorer.html — explore the 100 concrete cells
- /number_theory.html — visual structure explorer
- /composite_lore.html — tri-voice viewer
- /composite_lore_combined.html — 7-voice × 8-version viewer (478 lores)
- /lore_explorer.html — filterable lore browser
- /polyformalism.html — 6-port canary pin documentation
