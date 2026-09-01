from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

BG_TOP = (8, 9, 20)
BG_BOTTOM = (27, 16, 39)
CARD = (20, 17, 33)
CARD_BORDER = (58, 45, 76)
TEXT = (244, 237, 255)
MUTED = (161, 145, 177)
VIOLET = (216, 180, 254)
PURPLE = (143, 124, 247)
PINK = (239, 165, 209)


def _font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf",
        ]
        if mono and bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        ]
        if mono
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _background(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), BG_TOP + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(3))
        draw.line((0, y, width, y), fill=color + (255,))
    return image


def _centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font, fill) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    x = xy[0] - (box[2] - box[0]) / 2
    draw.text((x, xy[1]), text, font=font, fill=fill)


def _glow_text(base: Image.Image, xy: tuple[int, int], text: str, font, color, radius: int = 8) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    box = gdraw.textbbox((0, 0), text, font=font)
    x = xy[0] - (box[2] - box[0]) / 2
    gdraw.text((x, xy[1]), text, font=font, fill=color + (120,))
    glow = glow.filter(ImageFilter.GaussianBlur(radius))
    base.alpha_composite(glow)
    draw = ImageDraw.Draw(base)
    draw.text((x, xy[1]), text, font=font, fill=color + (255,))


def _save_gif(frames: list[Image.Image], path: Path, duration: int) -> None:
    rgb = [frame.convert("RGB") for frame in frames]
    rgb[0].save(
        path,
        save_all=True,
        append_images=rgb[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def build_intro() -> None:
    width, height = 920, 190
    title_font = _font(31, bold=True)
    mono = _font(13, mono=True)
    small = _font(11)
    messages = [
        "Java Backend Developer",
        "systems · data · infrastructure · automation",
        "building resilient systems after dark",
    ]
    frames: list[Image.Image] = []
    total = 30
    for i in range(total):
        phase = 2 * math.pi * i / total
        frame = _background(width, height)
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=26, outline=(53, 40, 71, 255), width=1)

        for x, y, offset in [(66, 38, 0.0), (856, 42, 1.6), (116, 137, 2.7), (806, 132, 4.0)]:
            alpha = int(70 + 170 * (0.5 + 0.5 * math.sin(phase + offset)))
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=VIOLET + (alpha,))

        _glow_text(frame, (460, 42), "Stellmaria", title_font, TEXT, 7)

        slot = (i // 10) % len(messages)
        local = i % 10
        message = messages[slot]
        reveal = min(len(message), max(1, int(len(message) * min(1.0, (local + 2) / 7))))
        visible = message[:reveal]
        box = draw.textbbox((0, 0), visible, font=mono)
        x = 460 - (box[2] - box[0]) / 2
        draw.text((x, 94), visible, font=mono, fill=(216, 200, 234, 255))
        if local % 2 == 0:
            cursor_x = x + (box[2] - box[0]) + 5
            draw.rounded_rectangle((cursor_x, 95, cursor_x + 6, 111), radius=1, fill=VIOLET + (255,))

        _centered(draw, (460, 135), "backend · systems · data · automation", small, MUTED + (255,))

        line_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ld = ImageDraw.Draw(line_layer)
        ld.rounded_rectangle((115, 163, 805, 165), radius=1, fill=(87, 66, 112, 180))
        sweep = 115 + int((690 - 110) * (i / total))
        ld.rounded_rectangle((sweep, 162, min(805, sweep + 110), 166), radius=2, fill=VIOLET + (180,))
        line_layer = line_layer.filter(ImageFilter.GaussianBlur(2))
        frame.alpha_composite(line_layer)
        frames.append(frame)
    _save_gif(frames, ASSETS / "intro-live.gif", 105)


def build_signature() -> None:
    width, height = 920, 230
    title_font = _font(17, bold=True, mono=True)
    label_font = _font(10, bold=True, mono=True)
    heading_font = _font(15, bold=True)
    body_font = _font(11)
    subtitle_font = _font(11, mono=True)
    cards = [
        ("01 / SYSTEMS", "Reliable by design", "clear boundaries · predictable behavior"),
        ("02 / CRAFT", "Simple on purpose", "readable code · calm interfaces"),
        ("03 / DELIVERY", "Ship, observe, refine", "automation · feedback · iteration"),
    ]
    subtitles = [
        "thoughtful systems · quiet details · deliberate delivery",
        "design for failure · simplify the boundary · observe the result",
        "build quietly · ship carefully · refine from real signals",
    ]
    positions = [(42, 96), (331, 96), (620, 96)]
    frames: list[Image.Image] = []
    total = 30
    for i in range(total):
        frame = _background(width, height)
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=26, outline=(53, 40, 71, 255), width=1)
        draw.text((42, 31), "DEVELOPER SIGNATURE", font=title_font, fill=TEXT + (255,))
        active = (i // 10) % 3
        draw.text((42, 61), subtitles[active], font=subtitle_font, fill=(173, 156, 191, 255))

        for idx, ((x, y), (label, heading, body)) in enumerate(zip(positions, cards)):
            is_active = idx == active
            if is_active:
                glow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow)
                gd.rounded_rectangle((x - 3, y - 3, x + 261, y + 91), radius=21, outline=VIOLET + (150,), width=4)
                glow = glow.filter(ImageFilter.GaussianBlur(8))
                frame.alpha_composite(glow)
            border = VIOLET + (255,) if is_active else CARD_BORDER + (255,)
            fill = (24, 19, 38, 255) if is_active else CARD + (255,)
            draw.rounded_rectangle((x, y, x + 258, y + 88), radius=18, fill=fill, outline=border, width=2 if is_active else 1)
            draw.text((x + 18, y + 17), label, font=label_font, fill=(196, 171, 226, 255))
            draw.text((x + 18, y + 40), heading, font=heading_font, fill=TEXT + (255,))
            draw.text((x + 18, y + 63), body, font=body_font, fill=(148, 136, 164, 255))

        # Animated footer rail.
        draw.rounded_rectangle((42, 207, 878, 209), radius=1, fill=(78, 58, 101, 220))
        sweep = 42 + int(730 * (i / total))
        draw.rounded_rectangle((sweep, 206, min(878, sweep + 105), 210), radius=2, fill=PINK + (220,))
        frames.append(frame)
    _save_gif(frames, ASSETS / "dev-signature-live.gif", 110)


def build_afterglow() -> None:
    width, height = 920, 104
    title_font = _font(12, bold=True, mono=True)
    body_font = _font(11)
    frames: list[Image.Image] = []
    total = 24
    for i in range(total):
        phase = 2 * math.pi * i / total
        frame = _background(width, height)
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=22, outline=(48, 36, 64, 255), width=1)
        alpha = int(90 + 150 * (0.5 + 0.5 * math.sin(phase)))
        draw.ellipse((122, 50, 126, 54), fill=VIOLET + (alpha,))
        draw.ellipse((794, 50, 798, 54), fill=PINK + (255 - alpha // 2,))
        _centered(draw, (460, 33), "LIVE PROFILE SIGNAL", title_font, TEXT + (255,))
        _centered(draw, (460, 56), "code · dream · create · iterate", body_font, MUTED + (255,))
        draw.rounded_rectangle((285, 81, 635, 83), radius=1, fill=(67, 50, 88, 255))
        sweep = 285 + int(290 * (i / total))
        draw.rounded_rectangle((sweep, 80, min(635, sweep + 60), 84), radius=2, fill=PURPLE + (210,))
        frames.append(frame)
    _save_gif(frames, ASSETS / "afterglow-live.gif", 110)


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    build_intro()
    build_signature()
    build_afterglow()
    print("wrote intro-live.gif, dev-signature-live.gif, afterglow-live.gif")