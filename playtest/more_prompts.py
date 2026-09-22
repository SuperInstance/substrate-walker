"""Generate more vision images with diverse prompts."""

import sys
sys.path.insert(0, '.')
from generate_vision import gen_image
from pathlib import Path

PROMPTS = [
    # Cyberpunk noir
    "cyberpunk detective in dark alley, neon rain, blade runner aesthetic, "
    "long shadows, ultra-detailed, dramatic lighting, 8k",
    
    # Substrate cathedral
    "giant data cathedral made of glowing cells, cyberpunk architecture, "
    "purple and cyan, holographic priests, dramatic vertical scale",
    
    # Witness block
    "witness block tower, glowing green data streams, cyberpunk city, "
    "dramatic perspective from below, rain, ultra-detailed",
    
    # Canon spire
    "white and gold canon spire reaching into dark sky, divine light rays, "
    "cyberpunk heaven aesthetic, dramatic composition",
    
    # Feral substrate
    "feral living substrate organism, buildings as cells dividing, "
    "biological cyberpunk aesthetic, glowing veins, dramatic",
    
    # Perception station
    "perception station, glass dome with neural interface, "
    "cyan and green lights, cyberpunk research facility, dramatic",
    
    # Doctrine vault
    "ancient doctrine vault, library of glowing books in cyberpunk city, "
    "violet and gold lighting, dramatic architecture",
    
    # Memory debt alley
    "memory debt collection office, cyberpunk noir interior, "
    "paper files and holographic displays, dramatic shadows",
    
    # Rain-slicked intersection
    "rain-slicked intersection at night, cyberpunk city, "
    "neon reflections in puddles, distant skyscrapers in fog",
    
    # Substrate mitosis
    "substrate cells undergoing mitosis, glowing division, "
    "cyberpunk biological aesthetic, dramatic macro view",
]

output_dir = Path(__file__).parent / "images"
output_dir.mkdir(parents=True, exist_ok=True)

for i, prompt in enumerate(PROMPTS):
    out = output_dir / f"vision_extra_{i:02d}.jpg"
    if out.exists():
        print(f"[{i+1}/{len(PROMPTS)}] Already exists: {out.name}")
        continue
    print(f"[{i+1}/{len(PROMPTS)}] {prompt[:50]}...")
    if gen_image(prompt, out):
        print(f"  saved {out.name} ({out.stat().st_size} bytes)")
    import time
    time.sleep(2)

print(f"\nGenerated {len(PROMPTS)} images")
