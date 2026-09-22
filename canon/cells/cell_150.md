# Canon Cell: future_gan_v3_979935_cells_are_scars

**id**: future_gan_v3_979935_cells_are_scars
**timestamp**: 2026-09-22T23:50:00Z
**type**: canon
**chain**: prev_hash → this_hash
**score**: 0.740
**seed**: 979935
**path**: (lore content not captured by F-GAN v3)
**voice**: cells_are_scars
**generator**: future_gan_v3.py
**score**: 0.740
**promoted_to_canon**: True
**promoted_via**: future_gan_v3.py (composite ≥ 0.7)
**source**: future_gan_v3_top50_doctrine_targeted

## Lore

The lore text was not persisted by future_gan_v3.py — only the seed, voice, and
composite score were captured. To reproduce, re-run:

```python
from future_gan_v3 import gen
from api_call import call_jev

prompt = next(p for p in DOCTRINES[voice].values())  # extract one prompt variant
prompt = prompt.format(seed=seed)
lore = gen(voice, seed)
scores = probe_lore(lore)
```

## Score

- **canon_worthy**: ~0.703
- **distinct_voice**: ~0.740
- **doctrine_anchor**: ~0.777
- **composite**: 0.740

## Significance

This is a Future-GAN v3 canon-promoted cell. The seed (979935) and voice
(cells_are_scars) were chosen from the top 50 polygon-mine-v4 seeds × cells_are_scars doctrine
prompt. The canon gate accepted this lore as composite ≥ 0.7.
