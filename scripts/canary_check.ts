// Substrate Walker — TypeScript Fleet Canary Pin
// Verifies FNV-1a 64-bit matches across Python, TypeScript, Rust.

const FNV_OFFSET_64 = 0xcbf29ce484222325n;
const FNV_PRIME_64 = 0x100000001b3n;
const MASK_64 = 0xffffffffffffffffn;

function fnv1a_64(s: string): bigint {
  let h = FNV_OFFSET_64;
  const bytes = new TextEncoder().encode(s);
  for (const b of bytes) {
    h = BigInt(h ^ BigInt(b));
    h = (h * FNV_PRIME_64) & MASK_64;
  }
  return h;
}

const CANARY_INPUT = "café Δ 日本語";
const FLEET_CANARY = "0x024a555471370b18d";

const vectors: [string, string, string][] = [
  [CANARY_INPUT, FLEET_CANARY, "fleet canary"],
  ["witness log is the prediction", "0x176137b542efe82a", "witness-log doctrine"],
  ["abc", "0xe71fa2190541574b", "FNV-1a 64 reference"],
  ["", "0xcbf29ce484222325", "empty string"],
  ["foobar", "0x85944171f73967e8", "FNV-1a 64 reference"],
  ["a", "0xaf63dc4c8601ec8c", "FNV-1a 64 single char"],
];

let allPass = true;
console.log("=== FLEET CANARY CHECK (substrate-walker TypeScript) ===");

for (const [input, expected, label] of vectors) {
  const h = fnv1a_64(input);
  const hHex = "0x" + h.toString(16).padStart(16, "0");
  const expectedInt = BigInt(expected);
  const match = h === expectedInt;
  if (!match) allPass = false;
  console.log(`  ${match ? "✓" : "✗"} '${input.slice(0, 30)}': ${expected} == ${hHex} (${label})`);
}

console.log(`\nAll pass: ${allPass}`);
console.log(`Fleet canary: ${FLEET_CANARY} == 0x${fnv1a_64(CANARY_INPUT).toString(16).padStart(16, "0")}`);

if (!allPass) process.exit(1);
