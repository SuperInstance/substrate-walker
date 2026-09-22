#!/usr/bin/env python3
"""
substrate-walker :: canary_check.py

Fleet canary validator. Confirms substrate-walker agrees with the pinned
FNV-1a 64-bit fleet canary across Python and TypeScript-style implementations.

Fleet canary:  fnv1a-64('café Δ 日本語') = 0x024a555471370b18d
Pinned across 15 substrate-* fleet packages (canary-pin, attest, witness-log,
foundation, traverse, contest, delegate, merger, revoke, withdraw, membership,
bundle, three-forms-of-evidence, three-forms-of-forgetting, opcode-canon).

This file adds substrate-walker to that canary-pinning fleet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

# ──────────────────────────────────────────────────────────────────────────────
# FNV-1a 64-bit constants (https://datatracker.ietf.org/doc/html/draft-eastlake-fnv)
# ──────────────────────────────────────────────────────────────────────────────
FNV_OFFSET_64: int = 0xCBF29CE484222325
FNV_PRIME_64: int = 0x100000001B3
MASK_64: int = 0xFFFFFFFFFFFFFFFF  # keep arithmetic in unsigned 64-bit


# ──────────────────────────────────────────────────────────────────────────────
# Python-style: native int, byte iteration over UTF-8
# ──────────────────────────────────────────────────────────────────────────────
def fnv1a_64_py(s: str) -> int:
    """Canonical FNV-1a 64-bit over UTF-8 bytes. Native Python ints."""
    h = FNV_OFFSET_64
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * FNV_PRIME_64) & MASK_64
    return h


# ──────────────────────────────────────────────────────────────────────────────
# TypeScript-style: BigInt literal constants, explicit BigInt() casts at every
# XOR / mul step, then bit-mask via & MASK. Mirrors the substrate-canary-pin
# index.js implementation so cross-language determinism is provable.
# ──────────────────────────────────────────────────────────────────────────────
def _big(val: int) -> "int-like":  # local alias; Python int is unbounded
    return val


def fnv1a_64_ts_style(s: str) -> int:
    """FNV-1a 64-bit mirroring the TS BigInt implementation in substrate-canary-pin."""
    FNV_OFFSET = _big(0xCBF29CE484222325)
    FNV_PRIME = _big(0x100000001B3)
    MASK = _big(0xFFFFFFFFFFFFFFFF)
    h = FNV_OFFSET
    # TS does: bytes = Buffer.from(s, 'utf-8'); for i in range(len): ...
    # Math is identical, but we keep the explicit cast shape so the diff vs the
    # JS source is one-to-one for code review.
    raw = s.encode("utf-8")
    i = 0
    while i < len(raw):
        h = (h ^ _big(raw[i])) & MASK
        h = (h * FNV_PRIME) & MASK
        i += 1
    return int(h)


# ──────────────────────────────────────────────────────────────────────────────
# Test vectors — pinned across the fleet
# ──────────────────────────────────────────────────────────────────────────────
FLEET_CANARY_INPUT = "café Δ 日本語"
FLEET_CANARY_HASH = 0x024A555471370B18D

KNOWN_VECTORS: list[tuple[str, int, str]] = [
    ("café Δ 日本語",                    0x024A555471370B18D, "fleet canary (substrate-* fleet pin)"),
    ("witness log is the prediction",   0x176137B542EFE82A, "witness-log doctrine canary"),
    ("abc",                             0xE71FA21905473374, "FNV-1a 64 reference vector"),
    ("",                                0xCBF29CE484222325, "empty string → FNV_OFFSET"),
    ("foobar",                          0x85944171F73967E8, "FNV-1a 64 reference vector"),
]


def hex16(h: int) -> str:
    return f"0x{h & MASK_64:016x}"


def run_vector(input_str: str, expected: int, label: str,
               py_fn: Callable[[str], int], ts_fn: Callable[[str], int]) -> dict:
    py_h = py_fn(input_str) & MASK_64
    ts_h = ts_fn(input_str) & MASK_64
    return {
        "input": input_str,
        "label": label,
        "expected_hex": hex16(expected),
        "py_hash": hex16(py_h),
        "ts_style_hash": hex16(ts_h),
        "py_match": py_h == expected,
        "ts_style_match": ts_h == expected,
        "cross_port_agree": py_h == ts_h,
    }


def main() -> int:
    print(f"substrate-walker :: fleet canary check")
    print(f"   FNV_OFFSET = {hex16(FNV_OFFSET_64)}")
    print(f"   FNV_PRIME  = {hex(FNV_PRIME_64)}")
    print()

    rows: list[dict] = []
    all_py_ok = True
    all_ts_ok = True
    all_cross_ok = True

    for s, expected, label in KNOWN_VECTORS:
        r = run_vector(s, expected, label, fnv1a_64_py, fnv1a_64_ts_style)
        rows.append(r)
        status = "OK " if (r["py_match"] and r["ts_style_match"] and r["cross_port_agree"]) else "FAIL"
        print(f"  [{status}] {label}")
        print(f"          input    : {r['input']!r}")
        print(f"          expected : {r['expected_hex']}")
        print(f"          py_hash  : {r['py_hash']}   match={r['py_match']}")
        print(f"          ts_hash  : {r['ts_style_hash']}   match={r['ts_style_match']}")
        print(f"          cross-port agree : {r['cross_port_agree']}")
        all_py_ok = all_py_ok and r["py_match"]
        all_ts_ok = all_ts_ok and r["ts_style_match"]
        all_cross_ok = all_cross_ok and r["cross_port_agree"]

    # Fleet pin summary
    fleet_match = rows[0]["py_match"] and rows[0]["ts_style_match"]
    print()
    print(f"Fleet canary pin : {FLEET_CANARY_INPUT!r} → {hex16(FLEET_CANARY_HASH)}")
    print(f"   substrate-walker matches fleet : {fleet_match}")

    report = {
        "package": "substrate-walker",
        "version": "1.0.0",
        "purpose": "fleet canary pin — substrate-walker joins the pinned fleet",
        "algorithm": "FNV-1a 64-bit",
        "constants": {
            "FNV_OFFSET_64": f"0x{FNV_OFFSET_64:016x}",
            "FNV_PRIME_64":  f"0x{FNV_PRIME_64:x}",
            "MASK_64":       f"0x{MASK_64:016x}",
        },
        "fleet_canary": {
            "input":  FLEET_CANARY_INPUT,
            "hash":   hex16(FLEET_CANARY_HASH),
            "match":  fleet_match,
        },
        "vectors": rows,
        "summary": {
            "total":      len(rows),
            "py_match":   sum(1 for r in rows if r["py_match"]),
            "ts_match":   sum(1 for r in rows if r["ts_style_match"]),
            "cross_port": sum(1 for r in rows if r["cross_port_agree"]),
            "all_ok":     all_py_ok and all_ts_ok and all_cross_ok and fleet_match,
        },
    }

    out_path = Path(__file__).parent / "canary_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print()
    print(f"Report written: {out_path}")
    print(f"Summary: {report['summary']}")

    return 0 if report["summary"]["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
