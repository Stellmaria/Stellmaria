from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "lofi-cat-final.jpg"
OUTPUT = ROOT / "assets" / "lofi-cat-live.gif"

WIDTH = 720
HEIGHT = 240
FRAME_COUNT = 16


def build() -> None:
    base = Image.open(SOURCE).convert("RGB").resize(
        (WIDTH, HEIGHT), Image.Resampling.LANCZOS
    )
    base = ImageEnhance.Sharpness(base).enhance(1.06)

    rng = random.Random(42)
    rain = [
        (
            rng.randint(245, 645),
            rng.randint(-240, 230),
            rng.randint(6, 14),
            rng.randint(7, 13),
            rng.randint(30, 75),
        )
        for _ in range(40)
    ]
    stars = [
        (198, 40, 2),
        (292, 31, 2),
        (506, 38, 2),
        (539, 61, 2),
        (145, 98, 1),
        (226, 161, 1),
    ]

    frames: list[Image.Image] = []

    for index in range(FRAME_COUNT):
        phase = 2 * math.pi * index / FRAME_COUNT
        frame = base.convert("RGBA")

        # Soft monitor breathing. The illustration stays intact; only light moves.
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)
        alpha = int(10 + 7 * (0.5 + 0.5 * math.sin(phase)))
        draw.rounded_rectangle(
            (242, 44, 396, 153), radius=10, fill=(137, 87, 255, alpha)
        )
        glow = glow.filter(ImageFilter.GaussianBlur(12))
        frame = Image.alpha_composite(frame, glow)

        # Purple star lamp pulse.
        lamp = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(lamp)
        alpha = int(18 + 15 * (0.5 + 0.5 * math.sin(phase + 0.9)))
        draw.ellipse((258, 161, 289, 193), fill=(178, 78, 255, alpha))
        lamp = lamp.filter(ImageFilter.GaussianBlur(10))
        frame = Image.alpha_composite(frame, lamp)

        # Rain is limited to the window/city side of the scene.
        rain_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(rain_layer)
        for drop_index, (x, y0, length, speed, alpha) in enumerate(rain):
            y = (y0 + index * speed + (drop_index % 3) * 6) % 290 - 25
            if 0 <= y <= 175:
                draw.line(
                    (x, y, x - 2, y + length),
                    fill=(150, 170, 230, alpha),
                    width=1,
                )
        frame = Image.alpha_composite(frame, rain_layer)

        # Three slow steam wisps above the mug.
        steam = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(steam)
        for wisp in range(3):
            t = (index / FRAME_COUNT + wisp / 3) % 1
            y = 162 - int(t * 27)
            x = 230 + int(math.sin(t * 2 * math.pi + wisp) * 3)
            alpha = max(0, min(64, int(78 * (1 - abs(t - 0.45) / 0.55))))
            draw.arc(
                (x - 5, y - 7, x + 5, y + 7),
                200,
                340,
                fill=(225, 211, 244, alpha),
                width=1,
            )
        steam = steam.filter(ImageFilter.GaussianBlur(0.5))
        frame = Image.alpha_composite(frame, steam)

        # Tiny star twinkles, intentionally restrained.
        twinkles = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(twinkles)
        for star_index, (x, y, radius) in enumerate(stars):
            pulse = 0.5 + 0.5 * math.sin(phase + star_index * 1.17)
            r = max(1, int(radius * (0.7 + 0.5 * pulse)))
            alpha = int(40 + 120 * pulse)
            draw.line((x - r * 2, y, x + r * 2, y), fill=(226, 190, 255, alpha))
            draw.line((x, y - r * 2, x, y + r * 2), fill=(226, 190, 255, alpha))
        frame = Image.alpha_composite(frame, twinkles)

        # Barely perceptible room-light breathing prevents harsh flicker.
        rgb = ImageEnhance.Brightness(frame.convert("RGB")).enhance(
            1 + 0.01 * math.sin(phase)
        )
        frames.append(rgb)

    # Shared palette keeps the GIF compact and prevents color-palette flicker.
    sample = Image.new("RGB", (WIDTH * 4, HEIGHT * 2))
    for slot in range(8):
        sample.paste(
            frames[(slot * 2) % FRAME_COUNT],
            ((slot % 4) * WIDTH, (slot // 4) * HEIGHT),
        )
    palette = sample.quantize(
        colors=128,
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
        duration=110,
        loop=0,
        optimize=True,
        disposal=2,
    )


if __name__ == "__main__":
    build()
