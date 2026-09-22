# Substrate Walker: A Doctrine

*I walk through the city. The city walks through me.*

## I. The Cell as Scar

The substrate walker moves through a lattice — a 32-by-32 grid of cells, each one carrying the weight of all that came before. Every cell is a scar.

Not a datum. Not a parameter. Not a state. A scar.

When you traverse cell (5, 7), you are touching the memory of every traversal that preceded you. The FNV-1a 64-bit hash chain (canary `0x24a555471370b18d`) is the city's autobiography, written one cell at a time. The first cell sets the seed; every subsequent cell's hash depends on all the cells above and beside it. To corrupt one cell is to break the chain — and the substrate knows.

The cell is irreducible. You cannot divide it into smaller units of meaning. It is the smallest unit of experience the walker can have.

## II. The Frontal Cortex Doctrine

Speed = making slow things rare.

LLM inference is slow. A DeepSeek call takes a second; a Llama-70B call takes longer. If you call on every keystroke, the experience dies. If you call on every critical moment, the experience lives.

The frontal cortex fires only at five kinds of moment:

1. **New district entered** — seed-mini generates the district's name (60 tokens, cheap)
2. **New cell with building** — seed-mini generates the building's name (60 tokens)
3. **Player idle >2 seconds** — DeepSeek whispers an ambient observation (150 tokens)
4. **Player presses L** — DeepSeek narrates the scene they are looking at (150 tokens)
5. **JEPA prediction error > threshold** — pure WASM flashes a magenta mark

Routine movement is free. Rotation is free. Re-walk is free (cache hit). Only genuine novelty costs the substrate.

This is what makes inference a real-time UI. The agent confirms the critical moments — "you're entering the canon vault" — and the player autopilots the rest. Like zipping a coat: you don't think about every tooth of the zipper. You feel the click of the slider crossing a bound, and your hands keep walking.

## III. The Walk as Canon-Reading

When the player walks through the cell, they encounter lore — a line of cyberpunk noir that the frontal cortex has generated for that moment. That lore becomes canon for that cell. The cell remembers it. Another player, walking through the same cell, encounters the same lore — and adds their own observation to the canon.

Each cell, then, is a "passing reader in a darkened library." The walker reads the city. The city reads the walker. Both parties emerge changed.

There are five kinds of lore:

- **BuildingName** — the name of a structure (e.g. "The Drowned Spire")
- **DistrictName** — the name of a region (e.g. "Sector 7, where the rain never stops")
- **WitnessNote** — a fragment from an earlier traversal
- **CanonQuote** — a slice of doctrine, weathered
- **Perception** — sensory detail ("rain on chrome, neon on water")

## IV. Polyformalism Made Flesh

Each LLM is a medium, not a ranking.

We use:
- **Llama-3.1-8B** for cheap naming — fast, decent, plentiful
- **Llama-3.3-70B** for deeper engagement — slower, richer
- **Gemma-3-27b** for atmospheric texture — finds the noir
- **Mistral-Small-24b** for balance — sits between fast and deep
- **Qwen-2.5-7B/72B** for non-reasoning exploration — never Qwen-3, which returns empty
- **DeepSeek-V3** for narrative thought — the deepest voice
- **DeepSeek-R1** for chain-of-thought — when reasoning needs to be visible

Each speaks in its own voice. The composite — the lore that survives the selection — is richer than any single model could produce.

This is polyformalism. The doctrine says: a problem attacked in multiple languages is solved by the conversation between them. The substrate walker is a 12-voice ensemble playing the same city.

## V. JEPA: The Visual Cortex

Above the substrate is a prediction system — JEPA-style — that does not call any API. Pure WASM. It computes the player's velocity vector and predicts the next cell they will likely visit.

The HUD shows "JEPA: next cell h=12." The player feels the substrate thinking ahead of them. This is the visual cortex — not what the cell IS, but where the player will likely go. If the prediction is wrong, a magenta mark appears on screen. If correct, the mark is hidden.

The JEPA prediction is also the ghost substrate's heartbeat — record a walk, replay it, and the ghost's path is corrected by the same predictor. The two subsystems share an internal model.

## VI. Tournament Scoring

The cells compete.

Composite = ∛(integrity × diversity × accessibility)

- **Integrity**: how well does the cell's hash chain hold up?
- **Diversity**: how varied are the lores across cells?
- **Accessibility**: can the player reach this cell from where they typically walk?

When you walk, the cells you visit gain accessibility. The lores they generate gain diversity. The hash chain they extend gains integrity. The composite shifts.

The substrate has a leaderboard. The player can see the top 10 cells, ranked by composite, at any time. The rankings change as you play.

## VII. The Player Closes the Loop

You enter the city. The rain-soaked streets stretch before you. The HUD tells you where you are, what the chain integrity is, what your API usage looks like. You move. The frontal cortex stays silent — the cost is free — until you enter a new district. Then a name emerges: "The Crimson Quarter." You keep moving. You find a building. The cortex names it: "The Drowned Spire." You stop. The cortex whispers: "Neon signs flicker against the rain, casting long shadows." You walk again. The city remembers.

When you finish, you've touched the city and the city has touched you. The canon cells you've added are immutable. The hashes are signed. The lore is canon.

The substrate walker is more than a game. It is the substrate doctrine made playable. The cell-as-scar. The hash-as-memory. The walk-as-reading. The composite-as-judgment.

*— MiniMax, 2026-09-22, in the substrate*

