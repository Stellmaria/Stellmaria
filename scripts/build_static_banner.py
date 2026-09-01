from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "lofi-master-v3"
OUTPUT = ROOT / "assets" / "stellmaria-banner.jpg"


def build() -> None:
    parts = sorted(SOURCE_DIR.glob("part*.b64"))
    if not parts:
        raise RuntimeError(f"No source chunks in {SOURCE_DIR}")

    encoded = "".join(path.read_text(encoding="utf-8").strip() for path in parts)
    source = Image.open(io.BytesIO(base64.b64decode(encoded, validate=True))).convert("RGB")

    # Keep the master crisp while avoiding an absurdly heavy profile payload.
    if source.width > 1800:
        height = round(source.height * 1800 / source.width)
        source = source.resize((1800, height), Image.Resampling.LANCZOS)

    source = ImageEnhance.Sharpness(source).enhance(1.08)
    source.save(
        OUTPUT,
        format="JPEG",
        quality=95,
        subsampling=0,
        optimize=True,
        progressive=True,
    )


if __name__ == "__main__":
    build()
