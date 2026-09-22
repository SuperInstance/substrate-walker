# Substrate Walker — Lore Benchmark

## Purpose

A standardized way to score cyberpunk noir lores against multiple criteria.
The composite score is the substrate-walker equivalent of a "canonicity" check.

## Criteria (each /10)

| Criterion | Description | Weight |
|-----------|-------------|--------|
| **Atmosphere** | Does it evoke a cyberpunk noir mood? | 2.0 |
| **Image** | Does it create a vivid visual? | 1.5 |
| **Brevity** | Is it concise? (≤40 chars ideal) | 1.0 |
| **Texture** | Does it have sensory detail (rain, neon, etc.)? | 1.5 |
| **Voice** | Does it sound like noir? | 1.0 |
| **Substrate** | Does it reference substrate doctrine? | 1.5 |
| **Specificity** | Is it specific (not generic)? | 1.0 |
| **Witness** | Does it feel like a record of something? | 0.5 |
| **Total** | Sum | 10.0 |

## Sample Scores (current top 5)

| Lore | Atm | Img | Brv | Tex | Voi | Sub | Spe | Wit | Total |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-------|
| "Rain-soaked streets, neon haze, and a femme fatale's whisper in the darkness" | 9.5 | 9.0 | 5.0 | 9.5 | 9.5 | 7.0 | 9.0 | 8.0 | 6.65 |
| "Rain pours down on streets of New Erebo" | 8.0 | 7.5 | 9.0 | 8.5 | 8.0 | 5.0 | 8.5 | 6.0 | 6.05 |
| "Rain-soaked streets reflected city's neon despair" | 9.0 | 9.0 | 7.0 | 9.0 | 8.5 | 5.0 | 8.5 | 7.0 | 6.30 |
| "Rain-soaked streets. Shadows hide secrets" | 8.0 | 8.0 | 9.5 | 8.0 | 8.5 | 5.0 | 7.0 | 7.0 | 5.90 |
| "Rain pours on the streets of Neo-Tokyo" | 8.0 | 7.5 | 9.0 | 8.0 | 7.5 | 5.0 | 9.0 | 6.0 | 5.75 |

## Implementation

The benchmark is computed by `playtest/benchmark.py`:

```python
def benchmark_lore(lore: str) -> Dict:
    return {
        "atmosphere": score_atmosphere(lore),  # 0-10
        "image": score_image(lore),
        "brevity": score_brevity(lore),
        "texture": score_texture(lore),
        "voice": score_voice(lore),
        "substrate": score_substrate(lore),
        "specificity": score_specificity(lore),
        "witness": score_witness(lore),
    }

def composite(b: Dict) -> float:
    return sum(b[k] * weight[k] for k, weight in CRITERIA.items())
```

## Application

Run the benchmark on all 485 lores in cache, find the top 50 by composite
score, and use those for the canonicity canon.

