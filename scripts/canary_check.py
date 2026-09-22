"""Substrate Walker — Fleet Canary Pin Check

Pins substrate-walker to the fleet canary:
FNV-1a 64-bit('café Δ 日本語') = 0x024a555471370b18d

This script verifies our FNV-1a implementation matches the rest of the
substrate-* fleet (15 ships pinned as of Sept 22, 2026), AND that
Python-style and TypeScript-style (BigInt) implementations produce the
same hash on every test vector — the cross-port determinism test.
"""
import json
import sys
from pathlib import Path

FNV_OFFSET_64 = 0xcbf29ce484222325
FNV_PRIME_64 = 0x100000001b3
MASK_64 = 0xffffffffffffffff

CANARY_INPUT = "café Δ 日本語"
FLEET_CANARY = "0x024a555471370b18d"


# ─────────────────────────────────────────────────────────────────────────────
# Python-style: native int, byte iteration. Same shape as the textbook.
# ─────────────────────────────────────────────────────────────────────────────
def fnv1a_64_py(s: str) -> int:
    """FNV-1a 64-bit — Python style (native int, byte iteration)."""
    h = FNV_OFFSET_64
    for b in s.encode('utf-8'):
        h ^= b
        h = (h * FNV_PRIME_64) & MASK_64
    return h


# ─────────────────────────────────────────────────────────────────────────────
# TypeScript-style: explicit BigInt literal constants, byte-index loop,
# bit-mask at every step. Mirrors substrate-canary-pin/index.js so a
# reviewer can diff the two implementations line-for-line.
# ─────────────────────────────────────────────────────────────────────────────
def fnv1a_64_ts(s: str) -> int:
    """FNV-1a 64-bit — TypeScript/BigInt style (matches index.js shape)."""
    FNV_OFFSET = 0xcbf29ce484222325  # BigInt in TS
    FNV_PRIME  = 0x100000001b3
    MASK       = 0xffffffffffffffff
    h = FNV_OFFSET
    raw = s.encode('utf-8')
    i = 0
    n = len(raw)
    while i < n:
        # In TS:  h = BigInt(h ^ BigInt(raw[i]))
        #         h = BigInt(h * FNV_PRIME)
        # Python int is unbounded, so we explicitly mask to 64 bits at each
        # step to match BigInt's fixed-width semantics.
        h = (h ^ raw[i]) & MASK
        h = (h * FNV_PRIME) & MASK
        i += 1
    return h


def main():
    """Run canary check and emit JSON report."""
    results = {
        "package": "substrate-walker",
        "version": "1.0.0",
        "purpose": "fleet canary pin — substrate-walker joins the pinned fleet",
        "algorithm": "FNV-1a 64-bit",
        "constants": {
            "FNV_OFFSET_64": hex(FNV_OFFSET_64),
            "FNV_PRIME_64": hex(FNV_PRIME_64),
            "MASK_64": hex(MASK_64),
        },
        "implementations": {
            "python_style": "fnv1a_64_py — native int, byte iteration",
            "typescript_style": "fnv1a_64_ts — BigInt-shape, byte-index loop, mask-at-each-step (mirrors substrate-canary-pin/index.js)",
        },
        "fleet_canary": {
            "input": CANARY_INPUT,
            "expected_hex": FLEET_CANARY,
        },
        "vectors": [],
        "cross_port_summary": {
            "py_match": 0,
            "ts_match": 0,
            "cross_port_agree": 0,
            "total": 0,
        },
    }

    all_pass = True

    # Reference vectors — verified against:
    #   • IETF draft-eastlake-fnv-07 Appendix C
    #   • ronshabi/fnv1a (x86-64 assembly) test vectors
    #   • substrate-canary-pin/index.js (cross-port)
    vectors = [
        ("café Δ 日本語",                    FLEET_CANARY,            "fleet canary (substrate-* fleet pin)"),
        ("witness log is the prediction",   "0x176137b542efe82a",    "witness-log doctrine canary"),
        ("",                                "0xcbf29ce484222325",    "empty string → FNV_OFFSET"),
        ("a",                               "0xaf63dc4c8601ec8c",    "FNV-1a 64 single char (IETF Appendix C)"),
        ("foobar",                          "0x85944171f73967e8",    "FNV-1a 64 reference (IETF Appendix C)"),
        ("abc",                             "0xe71fa2190541574b",    "FNV-1a 64 reference (IETF Appendix C)"),
    ]

    for input_str, expected, label in vectors:
        py_h   = fnv1a_64_py(input_str)
        ts_h   = fnv1a_64_ts(input_str)
        py_hex = f"0x{py_h:016x}"
        ts_hex = f"0x{ts_h:016x}"
        exp_int = int(expected, 16)
        py_ok  = (py_h == exp_int)
        ts_ok  = (ts_h == exp_int)
        cross  = (py_h == ts_h)
        if not (py_ok and ts_ok and cross):
            all_pass = False
        results["vectors"].append({
            "input": input_str,
            "label": label,
            "expected_hex": expected,
            "py_hash_hex":   py_hex,
            "ts_hash_hex":   ts_hex,
            "py_match":      py_ok,
            "ts_match":      ts_ok,
            "cross_port_agree": cross,
        })
        results["cross_port_summary"]["total"] += 1
        if py_ok:  results["cross_port_summary"]["py_match"] += 1
        if ts_ok:  results["cross_port_summary"]["ts_match"] += 1
        if cross:  results["cross_port_summary"]["cross_port_agree"] += 1

    # Fleet canary — compute and double-check both impls
    fleet_py = fnv1a_64_py(CANARY_INPUT)
    fleet_ts = fnv1a_64_ts(CANARY_INPUT)
    expected_fleet_int = int(FLEET_CANARY, 16)
    results["fleet_canary"]["py_hash_hex"] = f"0x{fleet_py:016x}"
    results["fleet_canary"]["ts_hash_hex"] = f"0x{fleet_ts:016x}"
    results["fleet_canary"]["py_match"] = (fleet_py == expected_fleet_int)
    results["fleet_canary"]["ts_match"] = (fleet_ts == expected_fleet_int)
    results["fleet_canary"]["cross_port_agree"] = (fleet_py == fleet_ts)
    results["fleet_canary"]["match"] = (
        results["fleet_canary"]["py_match"]
        and results["fleet_canary"]["ts_match"]
        and results["fleet_canary"]["cross_port_agree"]
    )
    if not results["fleet_canary"]["match"]:
        all_pass = False

    results["all_pass"] = all_pass

    # Write report
    report_path = Path(__file__).parent / "canary_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n=== FLEET CANARY CHECK (substrate-walker) ===")
    print(f"Algorithm : FNV-1a 64-bit (XOR-first)")
    print(f"Offset    : {hex(FNV_OFFSET_64)}")
    print(f"Prime     : {hex(FNV_PRIME_64)}")
    print()
    print(f"Fleet canary input : {CANARY_INPUT!r}")
    print(f"Fleet canary expect: {FLEET_CANARY}")
    print(f"  py_hash          : {results['fleet_canary']['py_hash_hex']}  match={results['fleet_canary']['py_match']}")
    print(f"  ts_hash          : {results['fleet_canary']['ts_hash_hex']}  match={results['fleet_canary']['ts_match']}")
    print(f"  cross-port agree : {results['fleet_canary']['cross_port_agree']}")
    print()
    cps = results["cross_port_summary"]
    print(f"Reference vectors ({cps['total']}):")
    print(f"  py_match          : {cps['py_match']}/{cps['total']}")
    print(f"  ts_match          : {cps['ts_match']}/{cps['total']}")
    print(f"  cross_port_agree  : {cps['cross_port_agree']}/{cps['total']}")
    for v in results["vectors"]:
        status = "✓" if (v["py_match"] and v["ts_match"] and v["cross_port_agree"]) else "✗"
        label = v['input'][:30] if v['input'] else "''"
        print(f"  {status} {label!r:32s} py={v['py_hash_hex']} ts={v['ts_hash_hex']} cross={v['cross_port_agree']}")
    print()
    print(f"All pass: {all_pass}")
    print(f"Report:  {report_path}")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
