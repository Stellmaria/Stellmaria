from __future__ import annotations

import base64
import io
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "lofi-master-v3"
OUTPUT = ROOT / "assets" / "lofi-cat-live.gif"

WIDTH = 1200
HEIGHT = 400
FRAME_COUNT = 14
WINDOW = (744, 0, 1084, 279)
TITLE = (38, 55, 440, 207)
EYE = (752, 122, 804, 169)
MUG_CENTER = (430, 285)


def _load_source() -> Image.Image:
    parts = sorted(SOURCE_DIR.glob("part*.b64"))
    if not parts:
        raise RuntimeError(f"No source chunks in {SOURCE_DIR}")
    encoded = "".join(path.read_text(encoding="utf-8").strip() for path in parts)
    raw = base64.b64decode(encoded, validate=True)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _blink_layer(base: Image.Image, strength: float) -> Image.Image:
    """Close the visible eye without moving or deforming the cat's head."""
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    x1, y1, x2, y2 = EYE

    # Sample local fur so the eyelid belongs to the cat instead of looking painted on.
    sample = base.crop((x1, y1 - 8, x2, y1 + 5)).resize((x2 - x1, y2 - y1))
    sample = sample.filter(ImageFilter.GaussianBlur(2.2)).convert("RGBA")
    sample.putalpha(int(215 * strength))
    layer.alpha_composite(sample, (x1, y1))

    draw = ImageDraw.Draw(layer)
    cy = y1 + 26
    width = max(2, round(7 * strength))
    draw.arc(
        (x1 + 5, cy - 10, x2 - 4, cy + 9),
        start=194,
        end=344,
        fill=(41, 35, 47, int(250 * strength)),
        width=width,
    )
    draw.arc(
        (x1 + 7, cy - 8, x2 - 7, cy + 7),
        start=196,
        end=342,
        fill=(207, 185, 219, int(65 * strength)),
        width=1,
    )
    return layer


def build() -> None:
    source = _load_source()
    if source.size != (WIDTH, HEIGHT):
        source = source.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    # Keep the master crisp. The old builder blurred the monitor by painting a second
    # fake code layer over it and moved cut-out paw crops around. Neither happens here.
    base = ImageEnhance.Sharpness(source).enhance(1.08)
    base = ImageEnhance.Contrast(base).enhance(1.015)

    rng = random.Random(27)
    rain_drops = [
        (
            rng.randint(WINDOW[0] + 5, WINDOW[2] - 5),
            rng.randint(WINDOW[1] - 180, WINDOW[3]),
            rng.randint(10, 22),
            rng.randint(9, 17),
            rng.randint(35, 72),
        )
        for _ in range(38)
    ]

    frames: list[Image.Image] = []
    blink_strength = {5: 0.45, 6: 1.0, 7: 0.45}

    for index in range(FRAME_COUNT):
        phase = 2 * math.pi * index / FRAME_COUNT
        frame = base.convert("RGBA")

        # Blink is deliberately short and visible. Nothing else on the cat is warped.
        strength = blink_strength.get(index)
        if strength:
            frame = Image.alpha_composite(frame, _blink_layer(base, strength))

        # Rain is clipped strictly to the exterior window panes.
        rain = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rain)
        for drop_index, (x, y0, length, speed, alpha) in enumerate(rain_drops):
            height = WINDOW[3] - WINDOW[1] + 80
            y = ((y0 - WINDOW[1]) + index * speed + (drop_index % 4) * 7) % height
            y += WINDOW[1] - 40
            if WINDOW[1] - 10 <= y <= WINDOW[3]:
                rd.line((x, y, x - 4, y + length), fill=(175, 195, 255, alpha), width=1)

        rain_mask = Image.new("L", (WIDTH, HEIGHT), 0)
        mask_draw = ImageDraw.Draw(rain_mask)
        mask_draw.rectangle((744, 0, 820, 132), fill=255)
        mask_draw.rectangle((930, 0, 1084, 250), fill=255)
        rain.putalpha(ImageChops.multiply(rain.getchannel("A"), rain_mask))
        frame = Image.alpha_composite(frame, rain)

        # Stronger, slow steam so it remains visible after GIF quantization.
        steam = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        st = ImageDraw.Draw(steam)
        for wisp in range(4):
            t = (index / FRAME_COUNT + wisp / 4) % 1
            y = MUG_CENTER[1] - 8 - int(t * 78)
            x = MUG_CENTER[0] + int(math.sin(t * 2 * math.pi + wisp * 0.8) * 10)
            opacity = max(0, min(125, int(145 * (1 - abs(t - 0.45) / 0.55))))
            st.arc(
                (x - 13, y - 18, x + 13, y + 18),
                200,
                344,
                fill=(239, 229, 247, opacity),
                width=3,
            )
        frame = Image.alpha_composite(frame, steam.filter(ImageFilter.GaussianBlur(1.1)))

        # A restrained light sweep across the existing title, no text redraw.
        shimmer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        sh = ImageDraw.Draw(shimmer)
        sweep_x = TITLE[0] - 95 + int((TITLE[2] - TITLE[0] + 185) * index / FRAME_COUNT)
        sh.polygon(
            [
                (sweep_x, TITLE[1]),
                (sweep_x + 28, TITLE[1]),
                (sweep_x + 96, TITLE[3]),
                (sweep_x + 68, TITLE[3]),
            ],
            fill=(255, 241, 255, 28),
        )
        frame = Image.alpha_composite(frame, shimmer.filter(ImageFilter.GaussianBlur(10)))

        twinkle = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        td = ImageDraw.Draw(twinkle)
        for star_index, (x, y) in enumerate(((70, 55), (370, 54), (423, 105), (1020, 64))):
            pulse = 0.5 + 0.5 * math.sin(phase + star_index * 1.15)
            radius = 1 + int(2 * pulse)
            opacity = int(32 + 100 * pulse)
            td.line((x - radius * 2, y, x + radius * 2, y), fill=(234, 204, 255, opacity))
            td.line((x, y - radius * 2, x, y + radius * 2), fill=(234, 204, 255, opacity))
        frame = Image.alpha_composite(frame, twinkle)

        # Tiny light breathing only. No monitor or keyboard repainting.
        frame = ImageEnhance.Brightness(frame.convert("RGB")).enhance(
            1 + 0.006 * math.sin(phase)
        )
        frames.append(frame)

    # Palette is derived primarily from the untouched master so monitor details survive.
    palette = base.quantize(
        colors=256,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.FLOYDSTEINBERG,
    )
    paletted = [
        frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG)
        for frame in frames
    ]
    paletted[0].save(
        OUTPUT,
        save_all=True,
        append_images=paletted[1:],
        duration=120,
        loop=0,
        optimize=False,
        disposal=2,
    )


if __name__ == "__main__":
    build()
