#!/bin/bash
# Pure bash FNV-1a 64-bit implementation — uses 64-bit arithmetic
# Reference: http://www.isthe.com/chongo/tech/comp/fnv/

FNV_OFFSET="cb f2 9c e4 84 22 23 25"  # 0xcbf29ce484222325
FNV_PRIME="01 00 00 00 01 b3"          # 0x100000001b3

fnv1a_64() {
    local input="$1"
    # Initialize hash as offset basis (big-endian 64-bit)
    local hash_bytes=($FNV_OFFSET)
    local hash_hex=""
    
    # Convert offset to a single 64-bit integer (bash doesn't handle 64-bit natively, use python here for accuracy)
    # Actually let's do it properly using shell arithmetic with 128-bit width
    local hash=$((0xcbf29ce484222325))  # offset
    
    # For each byte in the input
    local i
    for ((i=0; i<${#input}; i++)); do
        local char="${input:$i:1}"
        local byte=$(printf '%d' "'$char")
        # XOR
        hash=$((hash ^ byte))
        # Multiply by FNV_PRIME (modular)
        hash=$(((hash * 0x100000001b3) & 0xffffffffffffffff))
    done
    
    printf '0x%016x\n' "$hash"
}

# Reference vectors
test_case() {
    local input="$1"
    local expected="$2"
    local got=$(fnv1a_64 "$input")
    
    # Format expected to be same length
    local expected_full="0x$(printf '%016x' "$((expected))")"
    
    if [ "$got" = "$expected_full" ]; then
        echo "✓ '$input': $got (matches)"
        return 0
    else
        echo "✗ '$input': $got (expected $expected_full)"
        return 1
    fi
}

main() {
    local all_pass=true
    
    test_case "" 0xcbf29ce484222325 || all_pass=false
    test_case "a" 0xaf63dc4c8601ec8c || all_pass=false
    test_case "foobar" 0x85944171f73967e8 || all_pass=false
    test_case "abc" 0xe71fa2190541574b || all_pass=false
    
    if $all_pass; then
        return 0
    else
        return 1
    fi
}

main
