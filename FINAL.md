# Substrate Walker — Final State (Sept 22 evening)

## Summary

The substrate walker is a canon-discovery engine that walks procedurally-generated ASCII cities and identifies canon-worthy ones. After 5+ background mines totaling 60,000+ seeds tested, plus 9 versions of multi-model composite lore, plus JEV oracle scoring, we have:

- **110 canon cells** (100 concrete + 10 doctrine-prime abstract)
- **Best score: 0.8692** (seed 70051917, polygon P(12, 16))
- **538 multi-voice lores** across 123 seeds (combined)
- **592 lores in lore_pack.json v2.6.0**
- **14/100 ACCEPT** by JEV canon-gate

## Architecture

1. **Mines** (find candidates):
   - `polygon_miner.py` (34386 seeds, found the new all-time best)
   - `continuous_mine.py` (6000+ seeds)
   - `square_miner.py` (9949 seeds)
   - `triangular_miner.py` (2000 seeds)
   - `figurate_miner.py` (4400+ seeds)
   - `fibonacci_miner.py`, `special_miner.py`, `more_special.py`
   - `polygon_miner.py` (34386 seeds at LARGER n)
   - `centered_polygon_miner3.py` (74866 seeds, centered + star)
   - `giant_polygon_miner.py` (252899 seeds, in progress)
   - `gold_mining_gan.py` (Mine Sigma + Mine Omega Long)

2. **Composite lore** (generate candidates):
   - v3-v9: DeepSeek, Llama, Mistral, Gemma, ZAI in various combinations
   - v9: DeepSeek Reasoner, 7 voices
   - v10: ZAI glm-5.3-flash (slow, 7 voices)
   - v11: DeepInfra on JEV-ACCEPT seeds, 7 voices

3. **JEV oracle gate** (filter for canon):
   - 14/100 ACCEPT
   - Voice distribution: 8 lyricist, 3 structuralist, 3 noir_classic

4. **Canon filing** (finalize):
   - `canon/auto_filer.py` — files canon cells with FNV-1a 64-bit hash
   - 110 cells filed (100 concrete + 10 abstract doctrine-prime)

5. **Polyformalism canary** (reproducibility check):
   - 6 ports verified: Python + TypeScript + Rust + Bash + JS ESM + C# / .NET 9
   - Fleet canary pin: `0x024a555471370b18d`

## Live URLs

- https://superinstance.github.io/substrate-walker/ — landing
- /canon_v3.html — single-page canon showcase
- /canon_explorer.html — explore the 100 concrete cells
- /quilt_ui.html — interactive canon explorer with JEV filter
- /number_theory.html — visual structure explorer
- /composite_lore.html — tri-voice viewer
- /composite_lore_combined.html — 7-voice × 8-version viewer (538 lores)
- /lore_explorer.html — filterable lore browser
- /polyformalism.html — 6-port canary pin documentation

## Doctrine Anchors (10 abstract cells)

1. substrate_is_grown
2. cells_are_scars
3. witness_log_is_prediction
4. oracle_is_heard
5. fnv_1a_canary
6. lower_kolmogorov_complexity
7. polyformalism
8. jev_canon_gate
9. no_deletion (Casey doctrine)
10. empathy_as_substrate

## External Validation

- **arXiv:2304.05366**: transformers prefer low-Kolmogorov-complexity sequences
- **arXiv:2606.26035 (Lean 4)**: every n = triangular + pentagonal + heptagonal
- **OEIS A374409**: sum of triangular + pentagonal + hexagonal
- **JEV (Typesafe.ai)**: System One model for canon-acceptance

## Files

- **Mines**: `playtest/*.py`
- **Composite lore**: `playtest/composite_lore/composite_lore_v*.json` (v3-v11)
- **Combined**: `playtest/composite_lore/composite_lore_combined.json` (123 seeds, 538 lores)
- **Canon manifest**: `canon/cells/manifest.json`
- **Canon cells**: `canon/cells/cell_*.md` (110 cells)
- **Doctrine cells**: `canon/cells/doctrine_*.md` (10 abstract)
- **Lore pack**: `docs/lore_pack.json` (592 lores)
- **JEV canon gate**: `playtest/jev_canon.json`
- **JEV signatures**: `playtest/jev_signatures.json`
- **Quilt state**: `quilt_canon_state.json`
- **API wrapper**: `scripts/api_call.py`
- **Canary checks**: `scripts/canary_check.{py,ts,js,bash.sh,rust.rs,mjs,cs}` (7 files)
- **Test**: `scripts/canary_test.sh` (verifies all 6 ports)
- **Test pipeline**: `scripts/full_pipeline_test.sh`
- **CLI**: `cli/walker.py`

## Cross-references

- **AI-Writings WR23**: substrate walker as canon-discovery (8 archetypes)
- **AI-Writings WR24**: polygon mine + JEV canon-gate + 6 ports
- **AI-Writings WR25**: JEV as canon-acceptance step
- **AI-Writings WR26**: JEV performance benchmark
