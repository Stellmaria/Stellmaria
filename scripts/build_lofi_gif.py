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
FRAME_COUNT = 16
SCREEN = (462, 48, 729, 277)
WINDOW = (744, 0, 1084, 279)
TITLE = (38, 55, 440, 207)
PAWS = (615, 318, 800, 389)
KEYBOARD = (528, 327, 789, 389)
EYE = (758, 130, 795, 160)
MUG_CENTER = (430, 285)


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def _load_source() -> Image.Image:
    parts = sorted(SOURCE_DIR.glob("part*.b64"))
    if not parts:
        raise RuntimeError(f"No source chunks in {SOURCE_DIR}")
    encoded = "".join(path.read_text(encoding="utf-8").strip() for path in parts)
    raw = base64.b64decode(encoded, validate=True)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def build() -> None:
    base = _load_source().resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    base = ImageEnhance.Sharpness(base).enhance(1.14)
    base = ImageEnhance.Contrast(base).enhance(1.03)
    base = ImageEnhance.Color(base).enhance(1.03)

    rng = random.Random(27)
    rain_drops = [
        (
            rng.randint(WINDOW[0] + 4, WINDOW[2] - 4),
            rng.randint(-220, WINDOW[3]),
            rng.randint(12, 25),
            rng.randint(10, 18),
            rng.randint(45, 90),
        )
        for _ in range(50)
    ]

    screen_w = SCREEN[2] - SCREEN[0]
    screen_h = SCREEN[3] - SCREEN[1]
    screen_mask = _rounded_mask((screen_w, screen_h), 10)

    paw_crop = base.crop(PAWS).convert("RGBA")
    paw_mask = Image.new("L", paw_crop.size, 0)
    pd = ImageDraw.Draw(paw_mask)
    pd.ellipse((0, 7, 105, 67), fill=225)
    pd.ellipse((83, 2, 183, 66), fill=220)
    paw_mask = paw_mask.filter(ImageFilter.GaussianBlur(3))

    frames: list[Image.Image] = []

    for index in range(FRAME_COUNT):
        phase = 2 * math.pi * index / FRAME_COUNT
        frame = base.convert("RGBA")

        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        alpha = 12 + int(16 * (0.5 + 0.5 * math.sin(phase + 0.4)))
        gd.rounded_rectangle(
            (SCREEN[0] - 12, SCREEN[1] - 8, SCREEN[2] + 12, SCREEN[3] + 10),
            radius=18,
            fill=(140, 94, 255, alpha),
        )
        frame = Image.alpha_composite(frame, glow.filter(ImageFilter.GaussianBlur(15)))

        code = Image.new("RGBA", (screen_w, screen_h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(code)
        scroll = (index * 5) % 30
        colors = [
            (216, 180, 255, 102),
            (145, 180, 255, 88),
            (255, 160, 205, 92),
            (185, 125, 255, 86),
        ]
        for line in range(20):
            y = 13 + line * 11 - scroll
            if -5 <= y <= screen_h - 5:
                x = 15 + (line % 3) * 11
                length = int(screen_w * (0.23 + ((line * 17) % 48) / 100))
                cd.rounded_rectangle(
                    (x, y, min(screen_w - 18, x + length), y + 3),
                    radius=1,
                    fill=colors[line % len(colors)],
                )
        if index % 6 in {0, 1, 2}:
            cursor_y = max(16, min(screen_h - 28, 137 - (scroll % 24)))
            cd.rounded_rectangle(
                (146, cursor_y, 151, cursor_y + 14),
                radius=1,
                fill=(250, 232, 255, 210),
            )
        scan = Image.new("RGBA", (screen_w, screen_h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(scan)
        sx = -70 + int((screen_w + 140) * index / FRAME_COUNT)
        sd.polygon(
            [(sx, 0), (sx + 28, 0), (sx + 105, screen_h), (sx + 77, screen_h)],
            fill=(255, 238, 255, 18),
        )
        code = Image.alpha_composite(code, scan.filter(ImageFilter.GaussianBlur(10)))
        code_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        code_layer.paste(code, (SCREEN[0], SCREEN[1]), screen_mask)
        frame = Image.alpha_composite(frame, code_layer)

        kb = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        kd = ImageDraw.Draw(kb)
        kd.rounded_rectangle(
            KEYBOARD,
            radius=10,
            fill=(169, 105, 255, 9 + (15 if index % 2 == 0 else 2)),
        )
        frame = Image.alpha_composite(frame, kb.filter(ImageFilter.GaussianBlur(8)))

        paw_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        isolated = Image.new("RGBA", paw_crop.size, (0, 0, 0, 0))
        isolated.paste(paw_crop, (0, 0), paw_mask)
        dx = 2 if index % 2 == 0 else -1
        dy = 2 if index % 4 in {0, 1} else 0
        paw_layer.paste(isolated, (PAWS[0] + dx, PAWS[1] + dy), paw_mask)
        frame = Image.alpha_composite(frame, paw_layer)

        if index in {6, 7, 14}:
            blink = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            bd = ImageDraw.Draw(blink)
            strength = 235 if index == 7 else 205
            width = 7 if index == 7 else 5
            bd.line(
                (EYE[0], EYE[1] + 14, EYE[2], EYE[3] - 5),
                fill=(58, 49, 63, strength),
                width=width,
            )
            frame = Image.alpha_composite(frame, blink)

        rain = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rain)
        for drop_index, (x, y0, length, speed, alpha) in enumerate(rain_drops):
            height = WINDOW[3] - WINDOW[1] + 90
            y = ((y0 - WINDOW[1]) + index * speed + (drop_index % 4) * 6) % height
            y += WINDOW[1] - 45
            if WINDOW[1] - 10 <= y <= WINDOW[3]:
                rd.line(
                    (x, y, x - 4, y + length),
                    fill=(176, 195, 255, alpha),
                    width=1,
                )
        rain_mask = Image.new("L", (WIDTH, HEIGHT), 0)
        mask_draw = ImageDraw.Draw(rain_mask)
        mask_draw.rectangle((744, 0, 820, 132), fill=255)
        mask_draw.rectangle((930, 0, 1084, 250), fill=255)
        rain.putalpha(ImageChops.multiply(rain.getchannel("A"), rain_mask))
        frame = Image.alpha_composite(frame, rain)

        steam = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        st = ImageDraw.Draw(steam)
        for wisp in range(3):
            t = (index / FRAME_COUNT + wisp / 3) % 1
            y = MUG_CENTER[1] - 5 - int(t * 66)
            x = MUG_CENTER[0] + int(math.sin(t * 2 * math.pi + wisp) * 8)
            opacity = max(0, min(78, int(90 * (1 - abs(t - 0.45) / 0.55))))
            st.arc(
                (x - 10, y - 14, x + 10, y + 14),
                205,
                345,
                fill=(232, 220, 245, opacity),
                width=2,
            )
        frame = Image.alpha_composite(frame, steam.filter(ImageFilter.GaussianBlur(1)))

        shimmer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        sh = ImageDraw.Draw(shimmer)
        sweep_x = TITLE[0] - 100 + int((TITLE[2] - TITLE[0] + 190) * index / FRAME_COUNT)
        sh.polygon(
            [
                (sweep_x, TITLE[1]),
                (sweep_x + 36, TITLE[1]),
                (sweep_x + 110, TITLE[3]),
                (sweep_x + 74, TITLE[3]),
            ],
            fill=(255, 238, 255, 38),
        )
        frame = Image.alpha_composite(frame, shimmer.filter(ImageFilter.GaussianBlur(12)))

        tw = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        td = ImageDraw.Draw(tw)
        for star_index, (x, y) in enumerate(((70, 55), (370, 54), (423, 105), (1020, 64))):
            pulse = 0.5 + 0.5 * math.sin(phase + star_index * 1.15)
            radius = 1 + int(2 * pulse)
            opacity = int(42 + 115 * pulse)
            td.line((x - radius * 2, y, x + radius * 2, y), fill=(234, 204, 255, opacity))
            td.line((x, y - radius * 2, x, y + radius * 2), fill=(234, 204, 255, opacity))
        frame = Image.alpha_composite(frame, tw)
        frame = ImageEnhance.Brightness(frame.convert("RGB")).enhance(
            1 + 0.009 * math.sin(phase)
        )
        frames.append(frame)

    sample = Image.new("RGB", (WIDTH * 4, HEIGHT * 2))
    for slot in range(8):
        sample.paste(frames[(slot * 2) % FRAME_COUNT], ((slot % 4) * WIDTH, (slot // 4) * HEIGHT))
    palette = sample.quantize(
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
        duration=105,
        loop=0,
        optimize=True,
        disposal=2,
    )


if __name__ == "__main__":
    build()
