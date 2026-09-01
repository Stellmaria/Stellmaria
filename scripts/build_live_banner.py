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
        '<animate attributeName="opacity" values="0;.08;.24;.1;0" keyTimes="0;.18;.48;.8;1" dur="8.4s" repeatCount="indefinite"/>'
        '</path>'
        for index, path in enumerate(paths)
    )


def build() -> str:
    encoded_banner = base64.b64encode(SOURCE.read_bytes()).decode("ascii")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Animated Stellmaria late-night coding scene">
  <defs>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="steamBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4"/></filter>
    <radialGradient id="neonPulse"><stop offset="0" stop-color="#f7d4ff" stop-opacity=".38"><animate attributeName="stop-color" values="#f7d4ff;#d9b6ff;#ffd0e8;#f7d4ff" dur="7s" repeatCount="indefinite"/></stop><stop offset=".52" stop-color="#b564ff" stop-opacity=".11"><animate attributeName="stop-color" values="#b564ff;#7f9cff;#ea7fbb;#b564ff" dur="7s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="#9d55ff" stop-opacity="0"/></radialGradient>
    <radialGradient id="moonGlow"><stop stop-color="#f1d6ff" stop-opacity=".55"/><stop offset=".38" stop-color="#b66eff" stop-opacity=".22"/><stop offset="1" stop-color="#8044d5" stop-opacity="0"/></radialGradient>
    <radialGradient id="warmLampGlow"><stop stop-color="#fff0b2" stop-opacity=".7"/><stop offset=".28" stop-color="#ffbd62" stop-opacity=".28"/><stop offset="1" stop-color="#ff914d" stop-opacity="0"/></radialGradient>
  </defs>
  <image width="{WIDTH}" height="{HEIGHT}" href="data:image/png;base64,{encoded_banner}"/>
  <g aria-label="rising steam" filter="url(#steamBlur)">{steam()}</g>
  <ellipse cx="388" cy="228" rx="390" ry="166" fill="url(#neonPulse)" opacity=".1">
    <animate attributeName="opacity" values=".06;.23;.09;.2;.06" dur="7s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="1026" cy="105" rx="148" ry="43" fill="url(#neonPulse)" opacity=".04">
    <animate attributeName="opacity" values=".025;.19;.06;.15;.025" dur="4.5s" repeatCount="indefinite"/>
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
    <circle cx="903" cy="590" r="74" fill="url(#moonGlow)" opacity=".04"><animate attributeName="opacity" values=".02;.26;.06;.22;.02" dur="3.8s" repeatCount="indefinite"/></circle>
  </g>
  <g aria-label="glowing hoodie crescent" filter="url(#softGlow)">
    <circle cx="1655" cy="557" r="78" fill="url(#moonGlow)" opacity=".08"><animate attributeName="opacity" values=".04;.4;.1;.48;.04" dur="4.8s" repeatCount="indefinite"/></circle>
  </g>
  <g aria-label="animated moon globe" filter="url(#softGlow)">
    <circle cx="2055" cy="505" r="112" fill="url(#moonGlow)" opacity=".14"><animate attributeName="opacity" values=".08;.56;.16;.62;.08" dur="5.5s" repeatCount="indefinite"/></circle>
    <circle cx="2055" cy="505" r="63" fill="none" stroke="#dfbbff" stroke-width="2" opacity=".16"><animate attributeName="opacity" values=".08;.62;.12;.54;.08" dur="4.6s" begin="-1.5s" repeatCount="indefinite"/></circle>
  </g>
  <g aria-label="glowing shelf lantern" filter="url(#softGlow)">
    <circle cx="2077" cy="300" r="69" fill="url(#warmLampGlow)" opacity=".03"><animate attributeName="opacity" values=".02;.2;.05;.16;.02" dur="3.4s" repeatCount="indefinite"/></circle>
  </g>
</svg>'''
    ET.fromstring(svg)
    return svg


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT}")
