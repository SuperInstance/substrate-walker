"""Generate SDXL-Lightning images of substrate-walker concepts via Cloudflare."""

import os
import sys
import json
import time
import urllib.request
import base64
from pathlib import Path
from typing import List

CF_ACCOUNT = "049ff5e84ecf636b53b162cbb580aae6"
CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")

MODEL = "@cf/bytedance/stable-diffusion-xl-lightning"

PROMPTS = [
    "cyberpunk city skyline at night, ASCII characters as buildings, neon violet and cyan, "
    "rain-slicked streets, foggy atmosphere, blade runner style, ultra-detailed, "
    "viewed from street level, 8k, dark moody lighting",

    "neon cathedral of the substrate, towering data structure as a building, "
    "purple and cyan glow, holographic interface panels, flying drones, "
    "futuristic cyberpunk aesthetic, dramatic lighting, photorealistic",

    "cyberpunk noir detective walking through ASCII-text city, "
    "long trenchcoat, holographic displays, rain reflections, "
    "blade runner style, ultra-detailed, dark and moody",

    "an ASCII art city viewed through a CRT terminal monitor, "
    "phosphor green text characters forming buildings, "
    "retro-futuristic cyberpunk aesthetic, scan lines, "
    "vaporwave colors, 8k detail",

    "neon-soaked memory palace, towers made of glowing text, "
    "substrate cells visible as data crystals, "
    "cyberpunk noir atmosphere, ultra-detailed, "
    "purple and orange lighting",

    "feral substrate organism, a living city that grows itself, "
    "buildings as cells dividing, mitosis-like structures, "
    "cyberpunk biological aesthetic, glowing veins, "
    "purple and cyan, dramatic",

    "rain-slicked cyberpunk alley, ASCII character walls, "
    "neon signs in katakana, fog, distant skyscrapers, "
    "noir atmosphere, ultra-detailed, photorealistic",

    "witness block, a tower of glowing green text and data, "
    "surrounded by swirling code, cyberpunk architecture, "
    "purple and green, dramatic lighting, 8k",

    "doctrinal vault, ancient library tower in cyberpunk city, "
    "glowing books, holographic scholars, "
    "violet and gold lighting, dramatic composition",

    "canon spire, the highest tower, white and gold, "
    "rays of light streaming down, cyberpunk heaven, "
    "ultra-detailed, dramatic, divine atmosphere",
]


def gen_image(prompt: str, output_path: Path):
    """Generate one image via Cloudflare SDXL-Lightning."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/{MODEL}"
    body = {"prompt": prompt}

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {CF_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            output_path.write_bytes(data)
            return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main(n: int = 4, output_dir: Path = None):
    if not CF_TOKEN:
        print("No CLOUDFLARE_TOKEN")
        return

    output_dir = output_dir or Path(__file__).parent / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {n} images via Cloudflare SDXL-Lightning")

    for i in range(min(n, len(PROMPTS))):
        prompt = PROMPTS[i]
        out = output_dir / f"vision_{i:02d}.jpg"
        print(f"  [{i+1}/{n}] {prompt[:60]}...")
        if gen_image(prompt, out):
            print(f"    saved {out} ({out.stat().st_size} bytes)")
        time.sleep(2)  # rate limit


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    main(n)
