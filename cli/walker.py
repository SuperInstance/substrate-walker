"""Substrate Walker Terminal — CLI that walks the canon.

Usage:
    python3 walker.py list                    # show top 50 canon cells
    python3 walker.py walk SEED               # walk seed, see lore
    python3 walker.py minteral                # mine random + special seeds
    python3 walker.py canon                   # show all canon cells
    python3 walker.py composite SEED          # multi-voice for one seed
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "playtest"))


def render_seed(seed, x=16, y=16, angle=0):
    from playtest_v2 import render_view
    return render_view(seed, x, y, angle)


def score_seed(seed, x=16, y=16, angle=0):
    from playtest_v2 import render_view, score_view
    view, densities = render_view(seed, x, y, angle)
    return score_view(view, densities)


def lore_seed(seed, x=16, y=16, angle=0):
    """Generate lore for one seed (local copy of generate_lore)."""
    import random
    view, densities = render_seed(seed, x, y, angle)
    
    archetypes = [
        "Rain pours down on {place}",
        "{place} is the kind of city that eats its young",
        "{mood} in {place}, where {character}",
        "The {object} on {street} remembers what you forgot",
        "{character} walked into {place} looking for {target}",
        "In {place}, the {time} belongs to no one",
    ]
    
    places = ["Neo-Tokyo", "New Eden", "the City-Delta", "Nightport", "Cyber-Tokyo", "Old Beijing", "the Walled City", "Sector 7"]
    moods = ["rain-slicked", "neon-drenched", "smog-choked", "midnight-quiet"]
    characters = ["a lone runner", "an ex-cop", "a hacker in mourning", "an AI that dreams of being human"]
    streets = ["Rainmaker Avenue", "Chrome Street", "The Sprawl", "Last Mile Boulevard"]
    objects = ["hologram", "neon sign", "burned-out chip", "vending machine", "broken drone"]
    times = ["two AM", "last hour", "longest minute"]
    targets = ["a name", "the truth", "the exit", "an old debt"]
    
    template = random.choice(archetypes)
    return template.format(
        place=random.choice(places),
        mood=random.choice(moods),
        character=random.choice(characters),
        object=random.choice(objects),
        street=random.choice(streets),
        time=random.choice(times),
        target=random.choice(targets),
    )


def cmd_list(args):
    """List top canon cells."""
    gm_path = Path(__file__).parent.parent / "playtest/great_moments.json"
    if not gm_path.exists():
        print("No great_moments.json — run mining first")
        return
    
    gm = json.load(open(gm_path))
    n = args.n or 20
    
    print(f"\n=== TOP {n} CANON CELLS ===\n")
    for m in gm[:n]:
        print(f"  #{m['rank']:3} seed {m['seed']:>9}  score {m['score']:.4f}  '{m['lore'][:60]}'")
    print()


def cmd_walk(args):
    """Walk a single seed."""
    seed = args.seed
    score = score_seed(seed, args.x, args.y, args.angle)
    lore = lore_seed(seed, args.x, args.y, args.angle)
    
    print(f"\n=== SEED {seed} ===")
    print(f"Position: ({args.x}, {args.y})")
    print(f"Score: {score:.4f}")
    print(f"Lore: {lore}\n")
    
    if args.show_view:
        view, densities = render_seed(seed, args.x, args.y, args.angle)
        print("ASCII view:")
        for row in view:
            print("  " + "".join(row))


def cmd_minteral(args):
    """Mine random + special seeds."""
    import random
    rng = random.Random(args.seed or 42)
    
    print(f"\n=== MINING {args.count} SEEDS ===")
    if args.special:
        print("(special numbers only)")
    else:
        print("(random)")
    
    results = []
    for i in range(args.count):
        if args.special:
            n = rng.randint(50, 9999)
            pick = rng.randint(0, 7)
            if pick == 0: seed = n * n
            elif pick == 1: seed = n * (n+1) // 2
            elif pick == 2: seed = n * (3*n - 1) // 2
            elif pick == 3: seed = n * (2*n - 1)
            elif pick == 4: seed = n * (5*n - 3) // 2
            elif pick == 5: seed = 2**rng.randint(3, 20)
            elif pick == 6: seed = int(f"1{rng.randint(10**5, 10**7)}")
            else: seed = n
        else:
            seed = rng.randint(100000, 9999999)
        
        score = score_seed(seed)
        lore = lore_seed(seed)
        results.append((seed, score, lore))
    
    results.sort(key=lambda x: -x[1])
    print(f"\nTop 10:")
    for i, (seed, score, lore) in enumerate(results[:10], 1):
        print(f"  {i:2}. seed {seed:>9}  score {score:.4f}  '{lore[:60]}'")


def cmd_canon(args):
    """Show canon manifest."""
    manifest_path = Path(__file__).parent.parent / "canon/cells/manifest.json"
    if not manifest_path.exists():
        print("No manifest.json")
        return
    
    m = json.load(open(manifest_path))
    print(f"\n=== CANON MANIFEST ===")
    print(f"Version: {m['version']}")
    print(f"Total cells: {m['total_cells']}")
    print(f"Best score: {m['best_score']}")
    print(f"Type breakdown:")
    for t, c in m.get("type_breakdown", {}).items():
        print(f"  {t}: {c}")
    print(f"\nLatest 10 cells:")
    for e in m["entries"][-10:]:
        print(f"  {e['rank']:3} seed {e['seed']:>9}  {e['type']:14}  score {e['score']:.4f}")
        print(f"       '{e['lore'][:70]}'")


def cmd_composite(args):
    """Generate multi-voice for one seed."""
    seed = args.seed
    
    print(f"\n=== MULTI-VOICE COMPOSITE — seed {seed} ===\n")
    
    view, densities = render_seed(seed, args.x, args.y, args.angle)
    view_text = "\n".join("".join(row) for row in view)
    
    sys.path.insert(0, "/workspace/research/api-orchestra")
    from multi_api import chat
    
    prompts = {
        "structuralist": f"""Cyberpunk noir ARCHITECT. City cell:

{view_text}

ONE sentence (15-25 words). Focus on architecture. No preamble.""",
        "narrativist": f"""Cyberpunk noir CHARACTER walking:

{view_text}

ONE first-person sentence (15-25 words). Sensory detail. No preamble.""",
        "futurist": f"""Cyberpunk noir PROPHET. The city as living being:

{view_text}

ONE prophetic sentence (15-25 words). Make it breathe, dream, eat, speak. No preamble.""",
    }
    
    for voice, prompt in prompts.items():
        print(f"[{voice:14}] ", end='', flush=True)
        try:
            result = chat(
                provider="deepseek",
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=180,
            )
            lore = ""
            if isinstance(result, dict):
                lore = result.get("content", "")
            elif isinstance(result, str):
                lore = result
            
            if lore:
                print(f"\n  {lore.strip().replace(chr(10), ' ')}")
            else:
                print("(empty)")
        except Exception as e:
            print(f"error: {e}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Substrate Walker Terminal")
    sub = parser.add_subparsers(dest="command", help="Command")
    
    p_list = sub.add_parser("list", help="List top canon cells")
    p_list.add_argument("--n", type=int, default=20, help="How many to show")
    p_list.set_defaults(func=cmd_list)
    
    p_walk = sub.add_parser("walk", help="Walk a single seed")
    p_walk.add_argument("seed", type=int, help="Seed to walk")
    p_walk.add_argument("--x", type=int, default=16)
    p_walk.add_argument("--y", type=int, default=16)
    p_walk.add_argument("--angle", type=int, default=0)
    p_walk.add_argument("--show-view", action="store_true")
    p_walk.set_defaults(func=cmd_walk)
    
    p_mine = sub.add_parser("minteral", help="Mine random/special seeds")
    p_mine.add_argument("--count", type=int, default=200)
    p_mine.add_argument("--seed", type=int, default=42)
    p_mine.add_argument("--special", action="store_true", help="Use special numbers only")
    p_mine.set_defaults(func=cmd_minteral)
    
    p_canon = sub.add_parser("canon", help="Show canon manifest")
    p_canon.set_defaults(func=cmd_canon)
    
    p_comp = sub.add_parser("composite", help="Multi-voice composite for one seed")
    p_comp.add_argument("seed", type=int, help="Seed")
    p_comp.add_argument("--x", type=int, default=16)
    p_comp.add_argument("--y", type=int, default=16)
    p_comp.add_argument("--angle", type=int, default=0)
    p_comp.set_defaults(func=cmd_composite)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
