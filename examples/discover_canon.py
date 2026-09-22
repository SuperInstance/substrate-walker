"""Example: Discover canon from a prompt.

Run this script to generate lore variants and canon-promote the best ones.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from api_call import call_deepseek, call_jev


def generate_lore(prompt: str) -> str:
    """Generate lore via DeepSeek Reasoner."""
    full_prompt = f"""You are writing canon lore for the Quilt substrate walker.

Write 200 words of cyberpunk-noir WITNESS voice.

Doctrine anchor: oracle_is_heard (the canon gate is an audible signal).

{prompt}

Opening: 'The canon gate made itself heard.'
End: oracle heard; witness log accumulates.

DO NOT: explain, summarize, justify, or editorialize. ONLY show.
Output ONLY the lore text."""
    try:
        result = call_deepseek(
            [{"role": "user", "content": full_prompt}],
            max_tokens=3000,
            timeout=120,
        )
        if 'choices' in result:
            content = result['choices'][0]['message'].get('content', '')
            if not content:
                content = result['choices'][0]['message'].get('reasoning_content', '')
            return content
    except Exception as e:
        print(f"  ERROR: {e}")
    return ""


def probe_lore(lore: str) -> dict:
    """JEV composite probe."""
    try:
        result = call_jev(
            f"Quilt substrate walker canon lore (discover_canon.py):\n\n{lore[:1500]}",
            {
                "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
                "distinct_voice": {"type": "noul", "instructions": "Distinct voice?"},
                "doctrine_anchor": {"type": "noul", "instructions": "Doctrine-anchored?"},
            },
            timeout=60,
        )
        a = result.get("answers", {})
        return {
            "canon_worthy": a.get("canon_worthy", {}).get("noul", 0),
            "distinct_voice": a.get("distinct_voice", {}).get("noul", 0),
            "doctrine_anchor": a.get("doctrine_anchor", {}).get("noul", 0),
            "composite": (a.get("canon_worthy", {}).get("noul", 0) +
                          a.get("distinct_voice", {}).get("noul", 0) +
                          a.get("doctrine_anchor", {}).get("noul", 0)) / 3,
        }
    except Exception:
        return {"composite": 0, "promoted": False}


def file_canon_cell(lore: str, scores: dict) -> int:
    """File lore as canon cell."""
    manifest_path = Path(__file__).resolve().parent.parent / "canon" / "cells" / "manifest.json"
    manifest = json.load(open(manifest_path))
    new_rank = len(manifest["entries"]) + 1
    cell_path = manifest_path.parent / f"cell_{new_rank}.md"

    cell_path.write_text(f"""# Canon Cell: discovered-{new_rank}

**id**: discovered-{new_rank}
**timestamp**: 2026-09-22T23:30:00Z
**type**: canon
**chain**: prev_hash → this_hash
**score**: {scores['composite']:.3f}
**generator**: discover_canon.py
**jev_canon_worthy**: {scores['canon_worthy']:.2f}
**jev_distinct_voice**: {scores['distinct_voice']:.2f}
**jev_doctrine_anchor**: {scores['doctrine_anchor']:.2f}
**promoted_to_canon**: True

## Lore

{lore}
""")

    manifest['entries'].append({
        "rank": new_rank,
        "cell_id": f"discovered-{new_rank}",
        "path": f"canon/cells/cell_{new_rank}.md",
        "seed": "discover_canon",
        "score": scores['composite'],
        "lore": lore[:200] + "...",
        "voice": "witness",
        "type": "canon-discover-canon",
        "promoted_to_canon": True,
        "promoted_via": "discover_canon.py",
        "jev_canon_worthy": scores['canon_worthy'],
        "jev_distinct_voice": scores['distinct_voice'],
        "jev_doctrine_anchor": scores['doctrine_anchor'],
        "generator": "discover_canon.py",
        "timestamp": "2026-09-22T23:30:00Z",
    })

    manifest['total_cells'] = len(manifest['entries'])
    manifest['promoted_to_canon_count'] = sum(1 for e in manifest['entries'] if e.get('promoted_to_canon'))
    manifest['version'] = '2.19.0'

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return new_rank


def main():
    prompt = """Theme: The city's substrate remembered its quantum origins.

Write a canon lore where the canon gate opens its mouth at midnight and a hash
(0x4f0a7bc9) glows white against wet bricks."""

    print(f"Prompt: {prompt}\n")
    print("Generating lore via DeepSeek Reasoner...")
    lore = generate_lore(prompt)

    if not lore or len(lore) < 100:
        print("Generation failed.")
        return

    print(f"\nGenerated ({len(lore)} chars):")
    print(lore[:200])
    print("...")

    print("\nProbing via JEV...")
    scores = probe_lore(lore)
    print(f"  canon_worthy: {scores['canon_worthy']:.3f}")
    print(f"  distinct_voice: {scores['distinct_voice']:.3f}")
    print(f"  doctrine_anchor: {scores['doctrine_anchor']:.3f}")
    print(f"  composite: {scores['composite']:.3f}")

    if scores['composite'] >= 0.7:
        print("\n🌟 CANON! Filing as cell...")
        rank = file_canon_cell(lore, scores)
        print(f"  Filed as cell {rank}")
    else:
        print(f"\nNot canon (composite < 0.7)")


if __name__ == "__main__":
    main()
