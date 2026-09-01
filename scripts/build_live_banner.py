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
    minsk_time = datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Animated Stellmaria late-night coding scene">
  <defs>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <radialGradient id="neonPulse"><stop stop-color="#e9bcff" stop-opacity=".34"/><stop offset=".52" stop-color="#b564ff" stop-opacity=".08"/><stop offset="1" stop-color="#9d55ff" stop-opacity="0"/></radialGradient>
    <radialGradient id="moonGlow"><stop stop-color="#f1d6ff" stop-opacity=".55"/><stop offset=".38" stop-color="#b66eff" stop-opacity=".22"/><stop offset="1" stop-color="#8044d5" stop-opacity="0"/></radialGradient>
    <clipPath id="windowOnly"><path d="M1436 0H1902V92H1436ZM1674 101H1902V315H1787V217H1674Z"/></clipPath>
  </defs>
  <image width="{WIDTH}" height="{HEIGHT}" href="data:image/png;base64,{encoded_banner}"/>
  <g aria-label="ambient rain" clip-path="url(#windowOnly)">{falling_rain()}</g>
  <g aria-label="rising steam" filter="url(#softGlow)">{steam()}</g>
  <ellipse cx="388" cy="228" rx="390" ry="166" fill="url(#neonPulse)" opacity=".12">
    <animate attributeName="opacity" values=".08;.18;.1;.16;.08" dur="8s" repeatCount="indefinite"/>
  </ellipse>
  <g aria-label="twinkling stars" fill="#f8dfff" filter="url(#softGlow)">
    <path d="M117 67l5 14 14 5-14 5-5 14-5-14-14-5 14-5Z" opacity=".14"><animate attributeName="opacity" values=".1;.78;.18;.66;.1" dur="3.6s" repeatCount="indefinite"/></path>
    <path d="M667 78l6 17 17 6-17 6-6 17-6-17-17-6 17-6Z" opacity=".14"><animate attributeName="opacity" values=".12;.7;.14;.9;.12" dur="4.1s" begin="-1.1s" repeatCount="indefinite"/></path>
    <path d="M713 303l4 11 11 4-11 4-4 11-4-11-11-4 11-4Z" opacity=".12"><animate attributeName="opacity" values=".08;.8;.1;.55;.08" dur="3.2s" begin="-2s" repeatCount="indefinite"/></path>
  </g>
  <g aria-label="cat blink">
    <path d="M1412 267 Q1427 280 1444 267" fill="none" stroke="#1c1720" stroke-width="10" stroke-linecap="round" opacity="0">
      <animate attributeName="opacity" values="0;0;.88;.88;0;0;.88;.88;0" keyTimes="0;.2;.225;.25;.275;.61;.635;.66;1" dur="5.8s" repeatCount="indefinite"/>
    </path>
  </g>
  <g aria-label="cat ear movement" fill="none" stroke-linecap="round">
    <path d="M1450 102Q1490 137 1539 232" stroke="#f3ad91" stroke-width="4" opacity=".34">
      <animateTransform attributeName="transform" type="rotate" values="0 1510 228;2.8 1510 228;0 1510 228" dur="3.4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".18;.62;.3;.18" dur="3.4s" repeatCount="indefinite"/>
    </path>
    <path d="M1538 150Q1572 178 1603 239" stroke="#f0b1d0" stroke-width="3.5" opacity=".3">
      <animateTransform attributeName="transform" type="rotate" values="0 1570 226;-3.2 1570 226;0 1570 226" dur="4.1s" begin="-1.3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".16;.58;.26;.16" dur="4.1s" begin="-1.3s" repeatCount="indefinite"/>
    </path>
  </g>
  <g aria-label="animated moon" filter="url(#softGlow)">
    <circle cx="2030" cy="492" r="91" fill="url(#moonGlow)" opacity=".12"><animate attributeName="opacity" values=".08;.35;.15;.42;.08" dur="5.5s" repeatCount="indefinite"/></circle>
    <circle cx="2030" cy="492" r="57" fill="none" stroke="#dfbbff" stroke-width="2" opacity=".15"><animate attributeName="opacity" values=".08;.48;.12;.38;.08" dur="4.6s" begin="-1.5s" repeatCount="indefinite"/></circle>
  </g>
  <g aria-label="Minsk time" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" text-anchor="middle">
    <rect x="1203" y="533" width="120" height="43" rx="5" fill="#0b0d26" opacity=".92"/>
    <text x="1263" y="565" fill="#b986ff" font-size="28" font-weight="700">{minsk_time}</text>
    <circle cx="1215" cy="544" r="1.8" fill="#edc1ff"><animate attributeName="opacity" values="1;.2;1" dur="1s" repeatCount="indefinite"/></circle>
  </g>
</svg>'''
    ET.fromstring(svg)
    return svg


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT}")
