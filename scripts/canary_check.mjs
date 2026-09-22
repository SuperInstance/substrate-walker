// substrate_walker_js: JavaScript ESM port of FNV-1a 64-bit
// Reference: substrate-walker/scripts/canary_check.py

const FNV_OFFSET = 0xcbf29ce484222325n;
const FNV_PRIME = 0x100000001b3n;
const MASK = 0xffffffffffffffffn;

function fnv1a64(input) {
    let hash = FNV_OFFSET;
    const bytes = Buffer.from(input, 'utf-8');
    for (const byte of bytes) {
        hash ^= BigInt(byte);
        hash = (hash * FNV_PRIME) & MASK;
    }
    return hash;
}

// Reference vectors from fleet canary
const reference = [
    {input: "", expected: 0xcbf29ce484222325n},
    {input: "a", expected: 0xaf63dc4c8601ec8cn},
    {input: "foobar", expected: 0x85944171f73967e8n},
    {input: "abc", expected: 0xe71fa2190541574bn},
    {input: "café Δ 日本語", expected: 0x024a555471370b18dn},
    {input: "witness log is the prediction", expected: 0x176137b542efe82an},
];

console.log("=== Substrate Walker ESM Port — FNV-1a 64-bit ===\n");

let allPass = true;
for (const {input, expected} of reference) {
    const got = fnv1a64(input);
    const status = (got === expected) ? "✓" : "✗";
    if (got !== expected) allPass = false;
    const hex = "0x" + got.toString(16).padStart(16, "0");
    const expHex = "0x" + expected.toString(16).padStart(16, "0");
    console.log(`${status} '${input}': ${hex} (expected ${expHex})`);
}

console.log();
if (allPass) {
    console.log("All 6 reference vectors match — fleet canary pinned ✓");
    process.exit(0);
} else {
    console.log("MISMATCH — investigate!");
    process.exit(1);
}
