"""Build a self-contained animated SVG version of the profile banner."""

from __future__ import annotations

import base64
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "stellmaria-banner-hd.png"
OUTPUT = ROOT / "assets" / "stellmaria-banner-live.svg"
WIDTH = 2172
HEIGHT = 724


def falling_rain() -> str:
    drops = (
        (1462, 16, 42, 5.4, 0.0), (1528, 40, 50, 6.2, 1.1),
        (1626, 18, 36, 5.8, 2.2), (1735, 22, 54, 6.6, 0.7),
        (1795, 12, 44, 5.1, 3.0), (1860, 46, 38, 6.0, 1.8),
        (1925, 26, 58, 5.5, 2.7), (1985, 40, 42, 6.4, 0.4),
        (1698, 112, 40, 5.9, 1.4), (1778, 106, 52, 6.3, 2.5),
        (1860, 118, 36, 5.6, 0.9), (1950, 108, 48, 6.1, 3.4),
    )
    return "".join(
        f'<line x1="{x}" y1="{y}" x2="{x - 8}" y2="{y + length}" '
        'stroke="#a7c8ff" stroke-width="1.45" stroke-linecap="round" opacity=".24">'
        f'<animateTransform attributeName="transform" type="translate" values="0 -160;0 260" dur="{duration}s" begin="-{delay}s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;.25;.25;0" keyTimes="0;.08;.84;1" dur="6s" repeatCount="indefinite"/>'
        '</line>'
        for x, y, length, duration, delay in drops
    )


def steam() -> str:
    paths = (
        'M735 494 C728 469 746 448 738 423 C729 394 746 372 738 344',
        'M751 493 C764 470 747 447 758 420 C770 392 753 370 766 342',
        'M766 492 C780 465 763 443 774 417 C785 392 775 369 786 351',
        'M742 488 C751 467 739 447 747 429 C754 409 748 388 757 370',
    )
    return "".join(
        f'<path d="{path}" fill="none" stroke="#eee6ff" stroke-width="2.1" stroke-linecap="round" opacity="0">'
        f'<animateTransform attributeName="transform" type="translate" values="0 7;0 -17" dur="{8.4 + index * .65}s" begin="-{index * 1.7}s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;.045;.13;.05;0" keyTimes="0;.18;.48;.8;1" dur="8.4s" repeatCount="indefinite"/>'
        '</path>'
        for index, path in enumerate(paths)
    )


def digital_clock(value: str) -> str:
    """Render a compact seven-segment clock that matches the desk display."""
    segments = {
        "0": "ab cdef".replace(" ", ""), "1": "bc", "2": "abged", "3": "abgcd",
        "4": "fgbc", "5": "afgcd", "6": "afgecd", "7": "abc", "8": "abcdefg", "9": "abfgcd",
    }
    positions = {
        "a": ((3, 0), (14, 0)), "b": ((17, 3), (17, 11)), "c": ((17, 16), (17, 24)),
        "d": ((3, 27), (14, 27)), "e": ((0, 16), (0, 24)), "f": ((0, 3), (0, 11)),
        "g": ((3, 13.5), (14, 13.5)),
    }
    x = 1212
    parts: list[str] = []
    for char in value:
        if char == ":":
            parts.append(f'<circle cx="{x + 3}" cy="550" r="1.8" fill="#bc89ff"/><circle cx="{x + 3}" cy="562" r="1.8" fill="#bc89ff"/>')
            x += 10
            continue
        for segment in segments[char]:
            (x1, y1), (x2, y2) = positions[segment]
            parts.append(
                f'<line x1="{x + x1}" y1="{541 + y1}" x2="{x + x2}" y2="{541 + y2}" '
                'stroke="#bd8cff" stroke-width="2.7" stroke-linecap="round"/>'
            )
        x += 21
    return "".join(parts)


def build() -> str:
    encoded_banner = base64.b64encode(SOURCE.read_bytes()).decode("ascii")
    minsk_time = datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Animated Stellmaria late-night coding scene">
  <defs>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="steamBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4"/></filter>
    <radialGradient id="neonPulse"><stop stop-color="#e9bcff" stop-opacity=".34"/><stop offset=".52" stop-color="#b564ff" stop-opacity=".08"/><stop offset="1" stop-color="#9d55ff" stop-opacity="0"/></radialGradient>
    <radialGradient id="moonGlow"><stop stop-color="#f1d6ff" stop-opacity=".55"/><stop offset=".38" stop-color="#b66eff" stop-opacity=".22"/><stop offset="1" stop-color="#8044d5" stop-opacity="0"/></radialGradient>
    <radialGradient id="lampGlow"><stop stop-color="#fff2b6" stop-opacity=".8"/><stop offset=".25" stop-color="#ffc768" stop-opacity=".35"/><stop offset="1" stop-color="#ff9f40" stop-opacity="0"/></radialGradient>
    <clipPath id="windowOnly"><path d="M1436 0H1902V92H1436ZM1674 101H1902V315H1787V217H1674Z"/></clipPath>
  </defs>
  <image width="{WIDTH}" height="{HEIGHT}" href="data:image/png;base64,{encoded_banner}"/>
  <g aria-label="ambient rain" clip-path="url(#windowOnly)">{falling_rain()}</g>
  <g aria-label="living city windows" clip-path="url(#windowOnly)">
    <rect x="1436" y="0" width="466" height="315" fill="#7a9fff" opacity=".02"><animate attributeName="opacity" values=".01;.08;.025;.1;.01" dur="6.4s" repeatCount="indefinite"/></rect>
    <g fill="#d6b5ff" opacity=".18">
      <rect x="1707" y="164" width="9" height="15" rx="2"><animate attributeName="opacity" values=".1;.9;.25;.75;.1" dur="4.2s" repeatCount="indefinite"/></rect>
      <rect x="1762" y="209" width="9" height="14" rx="2"><animate attributeName="opacity" values=".2;.85;.12;.72;.2" dur="5.1s" begin="-1.5s" repeatCount="indefinite"/></rect>
      <rect x="1825" y="156" width="10" height="16" rx="2"><animate attributeName="opacity" values=".15;.78;.22;.95;.15" dur="3.8s" begin="-2.2s" repeatCount="indefinite"/></rect>
      <rect x="1872" y="241" width="8" height="13" rx="2"><animate attributeName="opacity" values=".15;.9;.2;.72;.15" dur="4.7s" begin="-.8s" repeatCount="indefinite"/></rect>
    </g>
  </g>
  <g aria-label="rising steam" filter="url(#steamBlur)">{steam()}</g>
  <ellipse cx="388" cy="228" rx="390" ry="166" fill="url(#neonPulse)" opacity=".12">
    <animate attributeName="opacity" values=".08;.18;.1;.16;.08" dur="8s" repeatCount="indefinite"/>
  </ellipse>
  <g aria-label="twinkling stars" fill="#f8dfff" filter="url(#softGlow)">
    <path d="M117 67l5 14 14 5-14 5-5 14-5-14-14-5 14-5Z" opacity=".14"><animate attributeName="opacity" values=".1;.78;.18;.66;.1" dur="3.6s" repeatCount="indefinite"/></path>
    <path d="M667 78l6 17 17 6-17 6-6 17-6-17-17-6 17-6Z" opacity=".14"><animate attributeName="opacity" values=".12;.7;.14;.9;.12" dur="4.1s" begin="-1.1s" repeatCount="indefinite"/></path>
  </g>
  <g aria-label="cat blink">
    <path d="M1412 267 Q1427 280 1444 267" fill="none" stroke="#1c1720" stroke-width="10" stroke-linecap="round" opacity="0">
      <animate attributeName="opacity" values="0;0;.88;.88;0;0;.88;.88;0" keyTimes="0;.2;.225;.25;.275;.61;.635;.66;1" dur="5.8s" repeatCount="indefinite"/>
    </path>
  </g>
  <g aria-label="glowing desk star" filter="url(#softGlow)">
    <circle cx="880" cy="556" r="78" fill="url(#moonGlow)" opacity=".1"><animate attributeName="opacity" values=".06;.52;.14;.42;.06" dur="3.6s" repeatCount="indefinite"/></circle>
    <path d="M880 519l10 26 28 10-28 10-10 28-10-28-28-10 28-10Z" fill="#f1d5ff" opacity=".12"><animate attributeName="opacity" values=".08;.75;.16;.62;.08" dur="3.1s" begin="-.6s" repeatCount="indefinite"/></path>
  </g>
  <g aria-label="glowing hoodie crescent" filter="url(#softGlow)">
    <circle cx="1655" cy="557" r="78" fill="url(#moonGlow)" opacity=".08"><animate attributeName="opacity" values=".04;.4;.1;.48;.04" dur="4.8s" repeatCount="indefinite"/></circle>
  </g>
  <g aria-label="animated moon globe" filter="url(#softGlow)">
    <circle cx="2055" cy="505" r="96" fill="url(#moonGlow)" opacity=".12"><animate attributeName="opacity" values=".08;.42;.15;.5;.08" dur="5.5s" repeatCount="indefinite"/></circle>
    <circle cx="2055" cy="505" r="61" fill="none" stroke="#dfbbff" stroke-width="2" opacity=".15"><animate attributeName="opacity" values=".08;.52;.12;.44;.08" dur="4.6s" begin="-1.5s" repeatCount="indefinite"/></circle>
  </g>
  <g aria-label="glowing shelf lantern" filter="url(#softGlow)">
    <circle cx="2077" cy="297" r="75" fill="url(#lampGlow)" opacity=".08"><animate attributeName="opacity" values=".04;.55;.12;.42;.04" dur="2.8s" repeatCount="indefinite"/></circle>
    <ellipse cx="2077" cy="298" rx="11" ry="39" fill="#ffd46f" opacity=".12"><animate attributeName="opacity" values=".05;.85;.16;.68;.05" dur="2.2s" repeatCount="indefinite"/></ellipse>
  </g>
  <g aria-label="Minsk time" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" text-anchor="middle">
    <rect x="1207" y="537" width="110" height="35" rx="4" fill="#101028" opacity=".56"/>
    <g filter="url(#softGlow)">{digital_clock(minsk_time)}</g>
  </g>
</svg>'''
    ET.fromstring(svg)
    return svg


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT}")
