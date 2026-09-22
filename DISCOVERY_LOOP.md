# Canon Discovery Loop — How Substrate Walker Generates Canon

*A guide for agents and humans who want to integrate canon discovery into their own
workflows.*

## TL;DR

```python
import json
import os
import sys

sys.path.insert(0, "/path/to/substrate-walker/scripts")
from api_call import call_jev, call_deepinfra, call_deepseek

lore = generate_lore_via_llm(prompt)
scores = probe_with_jev(lore)
if scores["composite"] >= 0.7:
    file_as_canon_cell(lore, scores)
```

That's the entire canon discovery loop. The rest of this document explains
each step.

## The Loop

```
[1] Generate lore draft (LLM)
   ↓
[2] JEV composite probe (3 nouls)
   ↓
[3] JEV doctrine-anchor probe (1 choice)
   ↓
[4] If composite ≥ 0.7: file as canon cell
   ↓
[5] Optional: stability re-probe for canon-stable cells
```

Each step is small and modular. You can integrate any step into your own agent.

## Step 1: Generate Lore Draft

The lore draft should be:
- 100-200 words (medium density)
- Cyberpunk-noir style (neon, rain, chrome, debt)
- Image-rich (specific sensory detail)
- Doctrine-anchored (weave one or more of the 5 doctrines)

Best generators (in order of canon-promotion rate):
1. **DeepSeek Reasoner** (~80% promotion rate) — uses reasoning to plan canon
2. **DeepInfra Llama-3.1-8B-Turbo** (~10-20% promotion rate) — fast, cheap
3. **ZAI glm-5.3-flash** (great for long-form essays, ~50% promotion)
4. **Hand-written** (variable, depends on writer)

For prompt patterns, see `EXAMPLES.md` in the polyvocoder docs.

## Step 2: JEV Composite Probe

```python
state = f"Quilt substrate walker canon lore:\n\n{lore[:1500]}"
questions = {
    "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir for Quilt substrate walker?"},
    "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
    "doctrine_anchor": {"type": "noul", "instructions": "Anchored to substrate walker doctrine?"},
}
result = call_jev(state, questions, timeout=60)
answers = result["answers"]
composite = (
    answers["canon_worthy"]["noul"]
    + answers["distinct_voice"]["noul"]
    + answers["doctrine_anchor"]["noul"]
) / 3
```

**Cost**: ~$0.04/1M input tokens. A 200-word lore is ~300 tokens = $0.012.

## Step 3: JEV Doctrine-Anchor Probe

```python
doctrine_questions = {
    "primary_doctrine": {
        "type": "choice",
        "instructions": "Which canonical doctrine does this lore most strongly anchor to?",
        "criteria": {
            "witness_log_is_prediction": "the witness log is shown to be predicting the canon",
            "oracle_is_heard": "the canon gate is shown to make an audible signal",
            "cells_are_scars": "each cell is shown to be a scar from earlier witness cycles",
            "canon_gate_is_chord": "the canon gate is shown as a chord the city can hear",
            "substrate_quantum": "the substrate is shown to be quantum in nature"
        },
        "choices": ["witness_log_is_prediction", "oracle_is_heard", "cells_are_scars", "canon_gate_is_chord", "substrate_quantum"]
    }
}
result = call_jev(state, doctrine_questions, timeout=60)
primary = result["answers"]["primary_doctrine"]["choice"]
```

## Step 4: File Canon Cell

```python
manifest_path = "/path/to/substrate-walker/canon/cells/manifest.json"
manifest = json.load(open(manifest_path))
new_rank = len(manifest["entries"]) + 1
cell_path = f"/path/to/substrate-walker/canon/cells/cell_{new_rank}.md"

cell_content = f"""# Canon Cell: {lore_title}

**id**: {cell_id}
**timestamp**: {datetime.utcnow().isoformat()}Z
**type**: canon
**chain**: prev_hash → this_hash
**score**: {composite:.3f}
**seed**: {seed}
**path**: {lore_path}
**voice**: {voice}
**generator**: {generator}
**jev_canon_worthy**: {canon_worthy:.2f}
**jev_distinct_voice**: {distinct_voice:.2f}
**jev_doctrine_anchor**: {doctrine_anchor:.2f}
**primary_doctrine**: {primary}
**promoted_to_canon**: True

## Lore

{lore}
"""

cell_path.write_text(cell_content)

manifest["entries"].append({...})
manifest["total_cells"] = len(manifest["entries"])
json.dump(manifest, open(manifest_path, "w"), indent=2)
```

## Step 5: Stability Re-Probe

For canon-stable cells (cells that survive independent re-probe), run JEV a second
time and check that composite ≥ 0.7 again.

```python
scores_2 = composite_probe_via_jev(lore)
is_stable = (scores["composite"] >= 0.7 and scores_2["composite"] >= 0.7)
```

Current canon-stable count: 9 cells (rank 124, 125, 128, 138, 139, 140, 141, 142, 143).

## Voice Variations

Different voices emphasize different doctrines:
- WITNESS: oracle_is_heard + cells_are_scars (most canonical)
- STRUCTURALIST: canon_gate_is_chord (architectural)
- NARRATIVIST: witness_log_is_prediction (first-person prediction)
- FUTURIST: substrate_quantum (prophecy)
- COSMIC_HORROR: cells_are_scars (eldritch)
- PHILOSOPHICAL: oracle_is_heard (meditative)
- LYRICIST: cells_are_scars + canon_gate_is_chord (poetic)
- NOIR_CLASSIC: cells_are_scars (hard-boiled)

## Auto-Promoter Pattern

The substrate walker has an auto-promoter that watches a `lore_inbox/` directory:

```bash
# Drop a lore file in lore_inbox/ as Markdown
python3 lore_auto_promoter.py --once    # process all pending files
python3 lore_auto_promoter.py --watch   # continuously watch
```

The auto-promoter:
1. Reads each `.md` file in `lore_inbox/`
2. Extracts the lore (text between `## Lore` markers)
3. Probes via JEV
4. If composite ≥ 0.7, files as a canon cell
5. Marks the file as processed (`.processed`)

This is the easiest integration pattern. Drop lore files, get canon cells.

## A2A Integration

Other agents can:
1. Read the canon archive at `canon/lore_pack.json` (JSON)
2. Read doctrine assignments at `canon/FULL_DOCTRINE_PROBE.json` (JSON)
3. Read stability results at `canon/STABILITY_PROBE_RESULTS.json` (JSON)
4. Browse via `canon/lore_explorer.html` (interactive)
5. Subscribe to new canon cells (future API)

## Further Reading

- `DOCTRINE_PAPER.md` — Full canonical reference for the 5 doctrines
- `polyvocoder/docs/WHITEPAPER.md` — Multi-modal canon extension
- `polyvocoder-bindings/README.md` — TypeScript integration

