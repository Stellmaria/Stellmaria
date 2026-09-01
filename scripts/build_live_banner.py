"""Build a self-contained animated SVG version of the profile banner."""

from __future__ import annotations

import base64
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "stellmaria-banner-hd.png"
OUTPUT = ROOT / "assets" / "stellmaria-banner-live.svg"
WIDTH = 2172
HEIGHT = 724


def falling_rain() -> str:
    drops = (
        (1450, 28, 42, 5.4, 0.0), (1516, 66, 50, 6.2, 1.1),
        (1648, 18, 36, 5.8, 2.2), (1718, 44, 54, 6.6, 0.7),
        (1787, 20, 44, 5.1, 3.0), (1852, 78, 38, 6.0, 1.8),
        (1930, 35, 58, 5.5, 2.7), (1990, 91, 42, 6.4, 0.4),
        (1608, 160, 40, 5.9, 1.4), (1695, 132, 52, 6.3, 2.5),
        (1775, 184, 36, 5.6, 0.9), (1874, 146, 48, 6.1, 3.4),
        (1958, 178, 34, 5.3, 2.0),
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
        'M735 486 C713 451 752 430 732 389 C720 365 738 343 754 325',
        'M758 489 C786 455 749 429 770 393 C788 365 770 343 786 317',
        'M708 492 C687 466 715 444 699 414 C690 394 701 374 712 356',
    )
    return "".join(
        f'<path d="{path}" fill="none" stroke="#e2d7ff" stroke-width="4" stroke-linecap="round" opacity="0">'
        f'<animateTransform attributeName="transform" type="translate" values="0 14;0 -22" dur="{7 + index * .7}s" begin="-{index * 2.2}s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;.2;.25;.08;0" keyTimes="0;.18;.46;.8;1" dur="7s" repeatCount="indefinite"/>'
        '</path>'
        for index, path in enumerate(paths)
    )


def build() -> str:
    encoded_banner = base64.b64encode(SOURCE.read_bytes()).decode("ascii")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Animated Stellmaria late-night coding scene">
  <defs>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <radialGradient id="neonPulse"><stop stop-color="#e9bcff" stop-opacity=".34"/><stop offset=".52" stop-color="#b564ff" stop-opacity=".08"/><stop offset="1" stop-color="#9d55ff" stop-opacity="0"/></radialGradient>
  </defs>
  <image width="{WIDTH}" height="{HEIGHT}" href="data:image/png;base64,{encoded_banner}"/>
  <g aria-label="ambient rain">{falling_rain()}</g>
  <g aria-label="rising steam" filter="url(#softGlow)">{steam()}</g>
  <ellipse cx="388" cy="228" rx="390" ry="166" fill="url(#neonPulse)" opacity=".12">
    <animate attributeName="opacity" values=".08;.18;.1;.16;.08" dur="8s" repeatCount="indefinite"/>
  </ellipse>
  <g filter="url(#softGlow)">
    <circle cx="117" cy="86" r="10" fill="#f3d6ff" opacity=".16"><animate attributeName="opacity" values=".08;.42;.12;.34;.08" dur="5.4s" repeatCount="indefinite"/></circle>
    <circle cx="667" cy="101" r="12" fill="#f3d6ff" opacity=".16"><animate attributeName="opacity" values=".08;.35;.12;.48;.08" dur="6.2s" begin="-1.4s" repeatCount="indefinite"/></circle>
    <circle cx="713" cy="316" r="7" fill="#f3d6ff" opacity=".12"><animate attributeName="opacity" values=".06;.45;.08;.3;.06" dur="4.8s" begin="-2s" repeatCount="indefinite"/></circle>
  </g>
  <path d="M1412 267 Q1427 280 1444 267" fill="none" stroke="#1c1720" stroke-width="10" stroke-linecap="round" opacity="0">
    <animate attributeName="opacity" values="0;0;0;.82;.82;0;0" keyTimes="0;.62;.66;.675;.695;.715;1" dur="11s" repeatCount="indefinite"/>
  </path>
</svg>'''
    ET.fromstring(svg)
    return svg


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT}")
