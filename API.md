# Substrate Walker — API Documentation

## Core Algorithms

### `playtest_v2.render_view(seed, x, y, angle, w=80, h=30) -> (view, densities)`

Render an ASCII view of the city at seed.

### `playtest_v2.score_view(view, densities) -> float`

Score a rendered city. Higher = more canon-worthy.

### `canon.fnv1a_64(s) -> int`

FNV-1a 64-bit hash of string `s`. Fleet canary pin.

### `canon.score_seed(seed) -> float`

Full scoring pipeline: render at multiple angles, take best.

### `canon.canon_cell(seed, lore, score, voice) -> dict`

Create a canon cell dict with FNV-1a hash.

## API Wrapper (`scripts/api_call.py`)

### `call_zai(messages, model="glm-5.3-flash", max_tokens=2000)`

Call ZAI chat API. ZAI has reasoning_content leak; use `max_tokens ≥ 200`.

### `call_deepseek(messages, model="deepseek-chat")`

Call DeepSeek chat. Has `deepseek-chat` and `deepseek-reasoner`.

### `call_kimi(messages, model="moonshot-v1-8k")`

Call Kimi chat. Reasoner models need `max_tokens ≥ 6000` for doctrinal.

### `call_deepinfra(messages, model="meta-llama/Meta-Llama-3.1-8B-Instruct")`

Call DeepInfra (multiple models available).

### `call_jev(state, questions, model="jev-latest")`

Call JEV (Typesafe.ai System One). Returns Choice/Score/Noul answers.

## JEV question types

```python
questions = {
    "is_canon": {"type": "noul", "instructions": "Is this canon-worthy?"},
    "best_voice": {"type": "choice", "instructions": "Which voice?",
                   "criteria": {"a": "first option", "b": "second option"}},
    "density": {"type": "score", "instructions": "Concrete density?",
                "criteria": [{"level": "low", "score": 0.0},
                             {"level": "med", "score": 0.5},
                             {"level": "high", "score": 1.0}]}
}
```

## CLI walker (`cli/walker.py`)

```bash
python3 cli/walker.py list 10           # top 10 canon
python3 cli/walker.py walk 70051917     # show city + lore
python3 cli/walker.py minteral          # show miner stats
python3 cli/walker.py canon             # show canon manifest
python3 cli/walker.py composite 70051917  # multi-voice for seed
```
