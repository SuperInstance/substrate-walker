"""
Substrate Walker — Gold Mining GAN

This is the deep iteration loop. It runs hundreds of "playtest expeditions":
1. Producer: generates procedural city configurations + custom path strategies
2. Critics: 3 different LLMs score each expedition
3. Best configurations get evolved (crossover, mutation)
4. Iterate for many generations to "fish up gold"

Output: the best cities + paths + lore + configurations discovered.
"""

import os
import sys
import json
import time
import asyncio
import random
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_api import chat, parallel_chat
from playtest_v2 import render_view, score_view, generate_lore

WORKSPACE = Path("/workspace/research/substrate-walker")


class Genome:
    """A genome for a city expedition.
    
    Encodes:
    - seed: which city to explore
    - path_type: how to walk
    - start_x, start_y, start_angle: starting camera
    - speed: movement speed
    - lookahead: how aggressive to be
    """
    def __init__(self, seed=None, path_type=None, start=(16, 16), start_angle=0.0):
        self.seed = seed or random.randint(1000, 999999)
        self.path_type = path_type or random.choice(["spiral", "explore", "straight_east", "wander"])
        self.start_x = start[0]
        self.start_y = start[1]
        self.start_angle = start_angle
        self.score = 0.0
        self.lore = ""
        self.best_snap = None
        self.generation = 0

    def to_dict(self):
        return {
            "seed": self.seed, "path_type": self.path_type,
            "start_x": self.start_x, "start_y": self.start_y, "start_angle": self.start_angle,
            "score": self.score, "lore": self.lore,
            "best_snap": self.best_snap,
            "generation": self.generation,
        }

    def mutate(self, rate: float = 0.3) -> "Genome":
        """Mutate the genome."""
        new = Genome(
            seed=self.seed,
            path_type=self.path_type,
            start=(self.start_x, self.start_y),
            start_angle=self.start_angle,
        )
        if random.random() < rate:
            new.seed = random.randint(1000, 999999)
        if random.random() < rate:
            new.path_type = random.choice(["spiral", "explore", "straight_east", "wander"])
        if random.random() < rate:
            new.start_x = max(0, min(32, self.start_x + random.uniform(-2, 2)))
        if random.random() < rate:
            new.start_y = max(0, min(32, self.start_y + random.uniform(-2, 2)))
        if random.random() < rate:
            new.start_angle += random.uniform(-1, 1)
        new.generation = self.generation + 1
        return new

    @staticmethod
    def crossover(a: "Genome", b: "Genome") -> "Genome":
        """Crossover two genomes."""
        return Genome(
            seed=a.seed if random.random() < 0.5 else b.seed,
            path_type=a.path_type if random.random() < 0.5 else b.path_type,
            start=(
                (a.start_x + b.start_x) / 2,
                (a.start_y + b.start_y) / 2,
            ),
            start_angle=(a.start_angle + b.start_angle) / 2,
        )


def genome_to_path(genome: Genome, n_steps: int = 20) -> List[Tuple[float, float, float]]:
    """Convert a genome to a path."""
    rng = random.Random(genome.seed)
    path = []

    if genome.path_type == "spiral":
        for i in range(n_steps):
            r = 1 + i * 0.7
            theta = i * 0.4 + genome.start_angle
            x = genome.start_x + r * (1 + theta * 0.05)
            y = genome.start_y + r * (1 - theta * 0.05)
            angle = theta
            path.append((x, y, angle))
    elif genome.path_type == "explore":
        x, y, angle = genome.start_x, genome.start_y, genome.start_angle
        for _ in range(n_steps):
            x += rng.uniform(-3, 3)
            y += rng.uniform(-3, 3)
            angle += rng.uniform(-0.5, 0.5)
            path.append((x, y, angle))
    elif genome.path_type == "straight_east":
        for i in range(n_steps):
            x = i * 1.6
            y = genome.start_y
            angle = genome.start_angle + 0.1 * (i % 5)
            path.append((x, y, angle))
    else:  # wander
        x, y = genome.start_x, genome.start_y
        angle = genome.start_angle
        for _ in range(n_steps):
            x += random.uniform(-4, 4)
            y += random.uniform(-4, 4)
            angle = rng.uniform(0, 6.28)
            path.append((x, y, angle))

    return path


async def evaluate_genome(genome: Genome) -> Genome:
    """Run a genome through the playtest, score it."""
    path = genome_to_path(genome)

    snapshots = []
    for x, y, angle in path:
        view, densities = render_view(genome.seed, x, y, angle)
        snap = {
            "x": x, "y": y, "angle": angle,
            "view": view,
            "score": score_view(view, densities),
        }
        snapshots.append(snap)

    # Best snapshot
    best = max(snapshots, key=lambda s: s["score"])
    genome.best_snap = best
    genome.score = best["score"]

    # Generate lore for the best
    lore = await asyncio.to_thread(generate_lore, best)
    genome.lore = lore

    return genome


async def gan_iteration(population: List[Genome], generation: int) -> Tuple[List[Genome], List[Genome]]:
    """One generation of the GAN.
    
    - Evaluate all genomes
    - Select top 50%
    - Crossover + mutate to create next gen
    """
    # Evaluate all in parallel (with semaphore to avoid overwhelming)
    sem = asyncio.Semaphore(5)
    async def eval_with_sem(g):
        async with sem:
            return await evaluate_genome(g)
    
    evaluated = await asyncio.gather(*[eval_with_sem(g) for g in population])

    # Sort by score
    evaluated.sort(key=lambda g: -g.score)

    # Select top half
    survivors = evaluated[:len(evaluated) // 2]

    # Generate children via crossover + mutation
    children = []
    n_children = len(population) - len(survivors)
    while len(children) < n_children:
        a = random.choice(survivors)
        b = random.choice(survivors)
        child = Genome.crossover(a, b)
        child = child.mutate(rate=0.3)
        child.generation = generation + 1
        children.append(child)

    return survivors + children, evaluated


async def gold_mine(population_size: int, generations: int, output_dir: Path):
    """Run the gold mining GAN."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🥇 Gold Mining GAN — {population_size} population, {generations} generations")

    # Seed population: random genomes
    population = [Genome() for _ in range(population_size)]
    all_time_best = None

    for gen in range(generations):
        print(f"\n=== Generation {gen+1}/{generations} ===")
        population, evaluated = await gan_iteration(population, gen)

        scores = [g.score for g in evaluated]
        best = max(evaluated, key=lambda g: g.score)
        avg = sum(scores) / len(scores)
        print(f"  Best: {best.score:.3f}, Avg: {avg:.3f}")
        print(f"  Top genome: seed={best.seed}, path={best.path_type}, score={best.score:.3f}")
        if best.lore:
            print(f"  Lore: {best.lore[:80]}")

        # Track all-time best
        if all_time_best is None or best.score > all_time_best.score:
            all_time_best = best
            print(f"  🥇 NEW ALL-TIME BEST!")

        # Save progress
        with open(output_dir / f"generation_{gen+1:03d}.json", "w") as f:
            json.dump({
                "generation": gen + 1,
                "best_score": best.score,
                "avg_score": avg,
                "best_genome": best.to_dict(),
                "population": [g.to_dict() for g in population],
            }, f, indent=2)

    # Final report
    print(f"\n{'='*60}")
    print(f"GOLD MINING COMPLETE")
    print(f"{'='*60}")
    print(f"All-time best score: {all_time_best.score:.3f}")
    print(f"  seed: {all_time_best.seed}")
    print(f"  path: {all_time_best.path_type}")
    print(f"  start: ({all_time_best.start_x}, {all_time_best.start_y})")
    print(f"  lore: {all_time_best.lore}")

    # Save final (with error handling)
    try:
        with open(output_dir / "final.json", "w") as f:
            json.dump({
                "all_time_best": all_time_best.to_dict(),
                "final_population": [g.to_dict() for g in population],
            }, f, indent=2)
        print(f"  Saved: {output_dir / 'final.json'}")
    except Exception as e:
        print(f"  Save error: {e}")
        import traceback
        traceback.print_exc()

    return all_time_best


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", type=int, default=20)
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--output", type=str, default="gold_mine")
    args = parser.parse_args()

    out_dir = WORKSPACE / "playtest" / "gan" / args.output
    asyncio.run(gold_mine(args.population, args.generations, out_dir))
