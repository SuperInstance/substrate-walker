"""
Great Moments Gallery
Compiles the best lore + best views from all gold mine runs into a single gallery.
"""

import os
import sys
import json
from pathlib import Path

WORKSPACE = Path("/workspace/research/substrate-walker")
GAN_DIR = WORKSPACE / "playtest" / "gan"


def collect_great_moments():
    """Find all the best moments across runs."""
    moments = []

    for run_dir in sorted(GAN_DIR.glob("mine_*")):
        final_file = run_dir / "final.json"
        if not final_file.exists():
            continue

        try:
            data = json.load(open(final_file))
            best = data.get("all_time_best", {})
            if not best or not best.get("lore"):
                continue

            # Truncate view to first 5 lines for preview
            view = best.get("best_snap", {}).get("view", [])
            view_preview = "\n".join(view[:10]) if view else ""

            moments.append({
                "run": run_dir.name,
                "score": best.get("score", 0),
                "seed": best.get("seed"),
                "path_type": best.get("path_type"),
                "start_x": best.get("start_x"),
                "start_y": best.get("start_y"),
                "lore": best.get("lore"),
                "view_preview": view_preview,
            })
        except Exception as e:
            print(f"  Error reading {final_file}: {e}")

    # Sort by score
    moments.sort(key=lambda m: -m["score"])
    return moments


def render_gallery(moments):
    """Render a markdown gallery."""
    out = ["# 🥇 Great Moments — Substrate Walker Gold Mine\n\n"]
    out.append(f"Top {len(moments)} gameplay moments discovered by the GAN.\n\n")
    out.append("Each moment represents a specific city (seed) and walk pattern (path_type) ")
    out.append("that produced a beautiful view, evocative lore, and high score.\n\n")
    out.append("---\n\n")

    for i, moment in enumerate(moments, 1):
        out.append(f"## {i}. Seed {moment['seed']} ({moment['path_type']}) — Score {moment['score']:.3f}\n\n")
        out.append(f"**Lore**: _{moment['lore']}_\n\n")
        out.append("```\n")
        out.append(moment['view_preview'] + "\n")
        out.append("```\n\n")
        out.append(f"Run: `{moment['run']}`\n\n")
        out.append("---\n\n")

    return "".join(out)


def main():
    print("Compiling great moments...")
    moments = collect_great_moments()
    print(f"Found {len(moments)} great moments")

    gallery = render_gallery(moments)

    out_file = WORKSPACE / "playtest" / "GREAT_MOMENTS.md"
    out_file.write_text(gallery)
    print(f"Saved to {out_file}")

    # Also save JSON
    json_file = WORKSPACE / "playtest" / "great_moments.json"
    json_file.write_text(json.dumps(moments, indent=2))
    print(f"Saved to {json_file}")

    # Print top 10
    print("\n=== Top 10 Great Moments ===")
    for i, m in enumerate(moments[:10], 1):
        print(f"{i}. seed={m['seed']:6} ({m['path_type']:14}) score={m['score']:.3f}")
        print(f"   lore: {m['lore'][:80]}")


if __name__ == "__main__":
    main()
