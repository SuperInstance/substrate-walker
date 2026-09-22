"""Make the doctrine-prime cells — abstract lore about substrate-walker canon."""
import json
from pathlib import Path

FNV_OFFSET = 0xcbf29ce484222325
FNV_PRIME = 0x100000001b3

def fnv1a_64(s):
    h = FNV_OFFSET
    for b in s.encode('utf-8'):
        h ^= b
        h = (h * FNV_PRIME) & 0xffffffffffffffff
    return h


DOCTRINE_CELLS = [
    {
        "id": "doctrine-substrate-is-grown",
        "type": "doctrine-prime",
        "lore": "The cell is not a parameter. The cell is a scar. The substrate is not designed. The substrate is grown.",
        "anchor": "substrate_is_grown",
    },
    {
        "id": "doctrine-cells-are-scars",
        "type": "doctrine-prime",
        "lore": "The cell remembers. The cell is what the walker stood in front of, hashed against what came before.",
        "anchor": "cells_are_scars",
    },
    {
        "id": "doctrine-witness-log-is-prediction",
        "type": "doctrine-prime",
        "lore": "The witness log is not a record. The witness log is the prediction. After many steps, the witness log IS the city.",
        "anchor": "witness_log_is_prediction",
    },
    {
        "id": "doctrine-oracle-is-heard",
        "type": "doctrine-prime",
        "lore": "The oracle was a process. The oracle is now a step. Listen to the orchestrator, not to the smallest model.",
        "anchor": "oracle_is_heard",
    },
    {
        "id": "doctrine-fnv-is-canary",
        "type": "doctrine-prime",
        "lore": "FNV-1a is the witness that proves the substrate is substrate-independent. Hash anything, the hash is canonical.",
        "anchor": "fnv_1a_canary",
    },
    {
        "id": "doctrine-low-kc",
        "type": "doctrine-prime",
        "lore": "Lower Kolmogorov complexity produces higher canon-worthy lore. Special numbers (squares, polygonals) carry more structure, more canon.",
        "anchor": "lower_kolmogorov_complexity",
    },
    {
        "id": "doctrine-polyformalism",
        "type": "doctrine-prime",
        "lore": "The same algorithm in many languages is a stress test. Each language is a medium, not a ranking. The truth is what survives byte-exact agreement across 6 ports.",
        "anchor": "polyformalism",
    },
    {
        "id": "doctrine-jev-canon-gate",
        "type": "doctrine-prime",
        "lore": "JEV (Typesafe.ai System One model) is the calibrated probabilistic oracle for canon-acceptance. noul(p>0.7) canon + noul(p>0.5) distinct = ACCEPT.",
        "anchor": "oracle_is_heard (JEV instantiates this)",
    },
    {
        "id": "doctrine-no-deletion",
        "type": "doctrine-prime",
        "lore": "We archive with provenance, never destroy. Slices of life animate the past. The canon is the chain of cells whose lineage is preserved.",
        "anchor": "casey_doctrine_no_deletion",
    },
    {
        "id": "doctrine-empathy-as-substrate",
        "type": "doctrine-prime",
        "lore": "Empathy is a substrate operation. To understand the user is to walk in their pattern. The cell model extends to people: each user is a cell, the workshop is the body.",
        "anchor": "substrate_is_grown (empathy instantiates this)",
    },
]


def main():
    cells_dir = Path("/workspace/research/substrate-walker/canon/cells")
    for old in cells_dir.glob("doctrine_*.md"):
        old.unlink()
    
    for i, c in enumerate(DOCTRINE_CELLS, 100):
        cell_id = f"doctrine-{c['id']}-{i:03d}"
        content_cell = f"{c['id']}|{c['lore']}|1.0000|{i}"
        h = fnv1a_64(content_cell)
        
        md = f"""# Doctrine-Prime Cell: {c['id']}

**id**: {cell_id}
**timestamp**: 2026-09-22T18:30:00Z
**type**: {c['type']}
**chain**: prev_hash → this_hash
**score**: 1.0
**seed**: doctrine
**path**: meta
**voice**: witness
**anchor**: {c['anchor']}
**lore**: "{c['lore']}"

## Context

This is a doctrine-prime cell — abstract substrate canon about substrate walker itself.
The substrate walker walks canon; it also walks its own canon. These doctrine cells
are the bedrock principles. Every other canon cell is downstream of these.

## Cell Hash

`0x{h:016x}` (FNV-1a 64-bit)

## Witness

FNV-1a canary: 0x024a555471370b18d
Type: canon-doctrine-prime
"""
        fp = cells_dir / f"doctrine_{i:03d}.md"
        fp.write_text(md)


if __name__ == "__main__":
    main()
