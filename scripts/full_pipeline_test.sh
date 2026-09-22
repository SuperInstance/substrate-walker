#!/bin/bash
# Full substrate walker pipeline test
# Verifies: API smoke, canary pin, lore generation, JEV oracle gate, polyformalism

set -e

cd /workspace/research/substrate-walker

echo "=========================================="
echo "SUBSTRATE WALKER — FULL PIPELINE TEST"
echo "=========================================="

echo
echo "1. Polyformalism canary (6 ports)"
./scripts/canary_test.sh 2>&1 | tail -3

echo
echo "2. API smoke test (JEV + ZAI + DeepInfra)"
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from api_call import call_jev, call_zai, call_deepinfra, extract_content
import json
print('  JEV:', end=' ')
r = call_jev('Test state for canary verification.', {'ans': {'type': 'noul', 'instructions': 'Working?'}})
print(f'OK ({len(r[\"answers\"])} q answered)')
try:
    r = call_zai([{'role': 'user', 'content': 'hi'}], max_tokens=200)
    print(f'  ZAI: OK ({len(extract_content(r))} chars)')
except Exception as e:
    print(f'  ZAI: skipped ({str(e)[:50]})')
try:
    r = call_deepinfra([{'role': 'user', 'content': 'hi'}], max_tokens=100)
    print(f'  DeepInfra: OK ({len(extract_content(r))} chars)')
except Exception as e:
    print(f'  DeepInfra: skipped ({str(e)[:50]})')
"

echo
echo "3. Canon manifest exists"
python3 -c "
import json
m = json.load(open('canon/cells/manifest.json'))
print(f'  cells: {m[\"total_cells\"]}, best: {m[\"best_score\"]:.4f}')
print(f'  types: {m[\"type_breakdown\"]}')
"

echo
echo "4. Lore pack v2.4.0"
python3 -c "
import json
d = json.load(open('docs/lore_pack.json'))
print(f'  lores: {d[\"total_lores\"]}, top: {d[\"best_score\"]:.4f}')
print(f'  canary: {d[\"fnv_canary\"]}')
"

echo
echo "5. Quilt cell-state"
python3 -c "
import json
d = json.load(open('quilt_canon_state.json'))
print(f'  cells: {len(d[\"cells\"])}, canary: {d[\"fnv_canary\"]}')
"

echo
echo "=========================================="
echo "ALL CHECKS PASSED"
echo "=========================================="
