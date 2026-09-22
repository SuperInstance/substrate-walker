# Substrate Walker — Doctrine

## The Frontal Cortex Principle

In the human brain, the frontal cortex doesn't process every sensory input.
It only fires on **critical moments** — when something genuinely new
demands attention. Routine processing happens elsewhere, automatically.

**Substrate Walker applies this principle:**

> The agent (JEV/JEPA) should confirm the zipper parts are married, then
> you look up and zip the coat the rest of the way while walking and
> thinking about something else.

In practice:
- **Movement**: instant (no API call)
- **Camera rotation**: instant (no API call)
- **Entering a new district**: API call (district name)
- **Entering a new cell with a building**: API call (building name)
- **Idle >2s**: API call (ambient observation)
- **Press L (examine)**: API call (on-demand narration)

## Why This Works

- **Latency budget**: API calls take ~200-1000ms. Frames render at 60fps
  (16ms). One API call per critical moment is acceptable.
- **Cost**: 10-20 API calls per minute of exploration, not 3600.
- **Cache**: re-visits are free. Walking through a known district costs 0.
- **Engagement**: the agent doesn't chatter. It speaks when it matters.

## The Speed = Real-Time UI Insight

When you make the cheap path instant and the expensive path rare, the
expensive path becomes tolerable. 1000ms API call is OK if it happens
once per 10 seconds, not 60 times per second.

**Speed isn't about making the slow thing fast. It's about making the
slow thing rare.**

## Three-Forms of Lore

1. **Building name** (seed-mini, 3-6 words): identifies what you see
2. **District name** (seed-mini, 2-4 words): identifies where you are
3. **Narrative observation** (DeepSeek, one sentence): describes what
   you experience

Each form has its own critical-moment trigger:
- Building: cell entry
- District: district entry
- Narrative: idle/examine

## Connection to Other Canon

- **JEV-Diffusion**: each district could be generated via JEV-Diffusion
  in real-time, not just named
- **Text-Diffusion (substrate mitosis)**: lore strings can be grown via
  mitosis, branching the narrative
- **Peanut Gallery**: the agent could spawn Critics that observe the
  player and add commentary
- **Madlibs-GAN**: lore templates could be filled by different LLMs

## Future Direction

The current implementation uses DeepInfra for both models. Future
directions:

- **On-device**: use a small model (e.g. 1B param) running locally
  for ambient observations, API only for examines
- **Predictive**: pre-generate lore for the next district the player
  is likely to enter (based on movement vector)
- **Streaming**: stream lore tokens as they're generated, displaying
  the observation as it forms
- **Multi-modal**: generate ASCII art for each district, not just
  names
