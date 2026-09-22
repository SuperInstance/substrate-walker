"""Benchmark JEV: response time, throughput, cost per call."""
import time
import sys
import json
import statistics
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev

# 50 calls, each with 3 questions
N = 50
lores = [
    "Rain-soaked streets, neon reflections, a lone figure in shadows.",
    "Concrete tenements rise in staggered brutalist clusters.",
    "The city dreams itself into being, one alley at a time.",
    "Fractured megastructures coil into neon canyons.",
    "Glyphs bleed light across the alley floor like wounds.",
]

times = []
total_input_tokens = 0
total_output_tokens = 0
costs = []

for i in range(N):
    state = lores[i % len(lores)] + f" Iteration {i} of {N}. " + ("benchmark " * 20)
    t0 = time.time()
    try:
        r = call_jev(state, {
            "canon": {"type": "noul", "instructions": "Canon-worthy?"},
            "voice": {"type": "choice", "instructions": "Which voice?", 
                      "criteria": {"lyric": "lyric", "narr": "narrative", "struct": "structural"}},
            "density": {"type": "score", "instructions": "Density?",
                        "criteria": [{"level": "low", "score": 0.0}, {"level": "med", "score": 0.5}, {"level": "high", "score": 1.0}]}
        })
        elapsed = time.time() - t0
        times.append(elapsed)
        
        usage = r.get("usage", {})
        total_input_tokens += usage.get("input_tokens", 0)
        total_output_tokens += usage.get("output_tokens", 0)
        costs.append((usage.get("input_tokens", 0) * 42 / 1_000_000))
        
        if (i+1) % 10 == 0:
            print(f"  {i+1}/{N} elapsed: {times[-1]:.3f}s")
    except Exception as e:
        print(f"  {i+1}/{N} ERROR: {e}")

print(f"\n=== JEV BENCHMARK ({N} calls) ===")
print(f"Total time: {sum(times):.1f}s")
print(f"Mean time per call: {statistics.mean(times):.3f}s")
print(f"Median time per call: {statistics.median(times):.3f}s")
print(f"Std dev: {statistics.stdev(times):.3f}s")
print(f"Max: {max(times):.3f}s, Min: {min(times):.3f}s")
print(f"Throughput: {N/sum(times):.1f} calls/s")
print(f"Total input tokens: {total_input_tokens}")
print(f"Total output tokens: {total_output_tokens}")
print(f"Total cost: ${sum(costs):.6f}")
print(f"Mean cost per call: ${sum(costs)/N:.6f}")

with open("/workspace/research/substrate-walker/playtest/jev_benchmark.json", "w") as f:
    json.dump({
        "n": N,
        "total_time_s": sum(times),
        "mean_time_s": statistics.mean(times),
        "median_time_s": statistics.median(times),
        "std_dev_s": statistics.stdev(times),
        "max_s": max(times),
        "min_s": min(times),
        "calls_per_s": N/sum(times),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_cost_usd": sum(costs),
        "mean_cost_per_call_usd": sum(costs)/N,
    }, f, indent=2)
print("Saved to playtest/jev_benchmark.json")
