"""
Canon Composer
Uses multiple LLMs to write a canon cell from different perspectives,
then synthesizes into a final canon text.

Like a multi-author collaboration, but each author is a different LLM.
"""

import os
import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat, parallel_chat

TOPIC = "Substrate Walker — the canon of walking through canon cells"

PERSPECTIVES = {
    "structuralist": (
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "You are a structuralist. Focus on architecture, systems, and formal patterns. "
        "Write 3-4 sentences about the technical substrate of the concept."
    ),
    "narrativist": (
        "deepseek-chat",
        "You are a narrativist. Focus on story, voice, and meaning. "
        "Write 3-4 sentences about the human/subjective experience of the concept."
    ),
    "futurist": (
        "google/gemma-3-27b-it",
        "You are a futurist. Focus on implications, possibilities, and edge cases. "
        "Write 3-4 sentences about where the concept leads."
    ),
}


async def compose_canon(topic: str) -> dict:
    """Get 3 perspectives and synthesize."""
    prompt_base = f"Topic: {topic}\n\n"

    calls = []
    for name, (model, system) in PERSPECTIVES.items():
        calls.append({
            "provider": "deepinfra" if "meta-llama" in model or "gemma" in model else "deepseek",
            "messages": [{"role": "system", "content": system},
                        {"role": "user", "content": prompt_base + "Your perspective:"}],
            "model": model,
            "max_tokens": 200,
            "temperature": 0.75,
        })

    results = await parallel_chat(calls)

    # Synthesize
    perspectives = {}
    for (name, _), result in zip(PERSPECTIVES.items(), results):
        perspectives[name] = result

    # Final synthesis (using deepseek-chat)
    synthesis_prompt = f"""Three perspectives on: {topic}

STRUCTURALIST: {perspectives['structuralist']}

NARRATIVIST: {perspectives['narrativist']}

FUTURIST: {perspectives['futurist']}

Synthesize these into a unified canon text (5-7 sentences) that captures the essence."""

    synthesis = chat("deepseek",
                     [{"role": "user", "content": synthesis_prompt}],
                     model="deepseek-chat", max_tokens=400, temperature=0.7)

    return {
        "topic": topic,
        "perspectives": perspectives,
        "synthesis": synthesis,
    }


async def main():
    print(f"=== Canon Composer: {TOPIC} ===\n")
    result = await compose_canon(TOPIC)

    print("STRUCTURALIST:")
    print(result["perspectives"]["structuralist"][:300])
    print("\nNARRATIVIST:")
    print(result["perspectives"]["narrativist"][:300])
    print("\nFUTURIST:")
    print(result["perspectives"]["futurist"][:300])
    print("\n" + "=" * 60)
    print("SYNTHESIS:")
    print("=" * 60)
    print(result["synthesis"])

    # Save
    out_dir = Path(__file__).parent / "canon"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "composite_canon.md"

    with open(out_file, "w") as f:
        f.write(f"# Composite Canon: {TOPIC}\n\n")
        f.write("## Structuralist View\n\n")
        f.write(result["perspectives"]["structuralist"] + "\n\n")
        f.write("## Narrativist View\n\n")
        f.write(result["perspectives"]["narrativist"] + "\n\n")
        f.write("## Futurist View\n\n")
        f.write(result["perspectives"]["futurist"] + "\n\n")
        f.write("## Synthesis\n\n")
        f.write(result["synthesis"] + "\n")

    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    asyncio.run(main())
