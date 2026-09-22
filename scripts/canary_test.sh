#!/bin/bash
# Fleet canary check — runs Python, TypeScript, and Rust ports and verifies agreement

echo "=== FLEET CANARY VERIFICATION (Python + TypeScript + Rust) ==="
echo

# Python
python3 /workspace/research/substrate-walker/scripts/canary_check.py
PY_EXIT=$?

echo

# TypeScript
if [ -f /workspace/research/substrate-walker/scripts/canary_check.js ]; then
    node /workspace/research/substrate-walker/scripts/canary_check.js
    TS_EXIT=$?
else
    echo "TypeScript canary_check.js not found"
    TS_EXIT=1
fi

echo

# Rust
if [ -x /workspace/research/substrate-walker/scripts/canary_check_rust ]; then
    /workspace/research/substrate-walker/scripts/canary_check_rust
    RUST_EXIT=$?
else
    echo "Rust canary_check_rust not found"
    RUST_EXIT=1
fi

echo
echo "=== Summary ==="
echo "Python exit: $PY_EXIT"
echo "TypeScript exit: $TS_EXIT"
echo "Rust exit: $RUST_EXIT"

if [ $PY_EXIT -eq 0 ] && [ $TS_EXIT -eq 0 ] && [ $RUST_EXIT -eq 0 ]; then
    echo "All 3 ports agree — fleet canary pinned ✓"
    exit 0
else
    echo "FAILED — one or more ports don't agree"
    exit 1
fi
