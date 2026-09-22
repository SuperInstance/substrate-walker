"""
Multi-model research brainstorm
Each model gets the same prompt about substrate-walker
Outputs are combined to find common themes and unique insights
"""

import os
import sys
import json
import asyncio
from collections import Counter
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat, parallel_chat

PROMPT = """Substrate Walker is a 3D ASCII cyberpunk city game running on Rust + WebAssembly + WebGL. Each building is a canon cell. The agent (frontal cortex) only fires on critical moments. We just added JEPA-style next-cell prediction and tournament scoring.

Question: What is the single most impactful feature we could add next?

Constraints:
- Must work in browser (Rust/WASM + JS)
- Must respect the frontal-cortex pattern (no API spam)
- Should be surprising or delightful, not boring

Answer in 2-3 sentences. Be specific about what to build and why."""

MODELS = [
    ("deepinfra", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
    ("deepinfra", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
    ("deepinfra", "google/gemma-3-27b-it"),
    ("deepinfra", "mistralai/Mistral-Small-3.2-24B-Instruct-2506"),
    ("deepseek", "deepseek-chat"),
]


async def brainstorm():
    calls = [
        {"provider": p, "messages": [{"role": "user", "content": PROMPT}], "model": m,
         "max_tokens": 200, "temperature": 0.85}
        for p, m in MODELS
    ]
    responses = await parallel_chat(calls)

    print("=== Substrate Walker Research Brainstorm ===\n")
    for (provider, model), response in zip(MODELS, responses):
        print(f"\n[{model}]")
        print(response[:500])
        print("---")

    # Find common keywords
    all_text = " ".join(r.lower() for r in responses)
    keywords = ["npc", "dialogue", "music", "audio", "save", "load",
                "multiplayer", "share", "narrative", "story",
                "weather", "time", "day", "night",
                "procedural", "generation", "diffusion",
                "memory", "persistence",
                "visual", "ascii", "art",
                "agent", "ai", "llm"]
    counts = {k: all_text.count(k) for k in keywords}
    print("\n=== Keyword Counts ===")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        if v > 0:
            print(f"  {k}: {v}")

    # Save
    out_dir = Path(__file__).parent / "research"
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "brainstorm_results.json", "w") as f:
        json.dump({
            "prompt": PROMPT,
            "responses": [{"model": m, "response": r} for (p, m), r in zip(MODELS, responses)],
            "keyword_counts": counts,
        }, f, indent=2)
    print(f"\nSaved to {out_dir}/brainstorm_results.json")


if __name__ == "__main__":
    asyncio.run(brainstorm())
