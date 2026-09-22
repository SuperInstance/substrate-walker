#!/bin/bash
# Fleet canary check — runs both Python and TypeScript ports and verifies agreement

echo "=== FLEET CANARY VERIFICATION ==="
echo

# Python
python3 /workspace/research/substrate-walker/scripts/canary_check.py
PY_EXIT=$?

echo

# TypeScript (transpiled)
if [ -f /workspace/research/substrate-walker/scripts/canary_check.js ]; then
    node /workspace/research/substrate-walker/scripts/canary_check.js
    TS_EXIT=$?
else
    echo "TypeScript canary_check.js not found"
    TS_EXIT=1
fi

echo
echo "=== Summary ==="
echo "Python exit: $PY_EXIT"
echo "TypeScript exit: $TS_EXIT"

if [ $PY_EXIT -eq 0 ] && [ $TS_EXIT -eq 0 ]; then
    echo "Both ports agree — fleet canary pinned ✓"
    exit 0
else
    echo "FAILED — one or more ports don't agree"
    exit 1
fi
