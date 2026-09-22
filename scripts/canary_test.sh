#!/bin/bash
# Fleet canary check — 6 ports: Python + TypeScript + Rust + Bash + JS ESM + C#

echo "=== FLEET CANARY VERIFICATION (6 ports) ==="
echo

# Python
python3 /workspace/research/substrate-walker/scripts/canary_check.py
PY_EXIT=$?
echo

# TypeScript
if [ -f /workspace/research/substrate-walker/scripts/canary_check.js ]; then
    node /workspace/research/substrate-walker/scripts/canary_check.js | tail -8
    TS_EXIT=$?
else
    echo "TypeScript canary_check.js not found"
    TS_EXIT=1
fi
echo

# Rust
if [ -x /workspace/research/substrate-walker/scripts/canary_check_rust ]; then
    /workspace/research/substrate-walker/scripts/canary_check_rust | tail -2
    RUST_EXIT=$?
else
    echo "Rust canary_check_rust not found"
    RUST_EXIT=1
fi
echo

# Bash
if [ -x /workspace/research/substrate-walker/scripts/canary_check_bash.sh ]; then
    /workspace/research/substrate-walker/scripts/canary_check_bash.sh
    BASH_EXIT=$?
else
    echo "Bash canary_check_bash.sh not found"
    BASH_EXIT=1
fi
echo

# JS ESM
if [ -f /workspace/research/substrate-walker/scripts/canary_check.mjs ]; then
    node /workspace/research/substrate-walker/scripts/canary_check.mjs | tail -2
    JS_EXIT=$?
else
    echo "JS canary_check.mjs not found"
    JS_EXIT=1
fi
echo

# C#
if [ -x /workspace/research/substrate-walker/scripts/canary_check_cs ]; then
    /workspace/research/substrate-walker/scripts/canary_check_cs | tail -2
    CS_EXIT=$?
else
    echo "C# canary_check_cs not found"
    CS_EXIT=1
fi
echo

echo "=== Summary ==="
echo "Python: $PY_EXIT"
echo "TypeScript: $TS_EXIT"
echo "Rust: $RUST_EXIT"
echo "Bash: $BASH_EXIT"
echo "JS ESM: $JS_EXIT"
echo "C#: $CS_EXIT"

if [ $PY_EXIT -eq 0 ] && [ $TS_EXIT -eq 0 ] && [ $RUST_EXIT -eq 0 ] && [ $BASH_EXIT -eq 0 ] && [ $JS_EXIT -eq 0 ] && [ $CS_EXIT -eq 0 ]; then
    echo "All 6 ports agree — fleet canary pinned ✓"
    exit 0
else
    echo "FAILED"
    exit 1
fi
