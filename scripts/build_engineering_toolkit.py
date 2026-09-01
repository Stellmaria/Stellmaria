from __future__ import annotations

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "engineering-toolkit-live.svg"
SIMPLE = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons"

PANELS = [
    {
        "title": "LANGUAGES & WEB",
        "accent": "#d8b4fe",
        "icons": [
            ("Java", "openjdk", "#437291"),
            ("Python", "python", "#3776AB"),
            ("JavaScript", "javascript", "#F7DF1E"),
            ("HTML5", "html5", "#E34F26"),
            ("CSS", "css", "#663399"),
            ("PowerShell", "powershell", "#5391FE"),
        ],
        "lines": [
            "Java 17 · Python 3.13 · JavaScript · SQL / PLpgSQL",
            "HTML5 · CSS3 · Bash · PowerShell · automation scripts",
            "backend-first engineering across public and private work",
        ],
    },
    {
        "title": "BACKEND & APIs",
        "accent": "#efa5d1",
        "icons": [
            ("Spring", "spring", "#6DB33F"),
            ("Hibernate", "hibernate", "#59666C"),
            ("OpenAPI", "openapiinitiative", "#6BA539"),
            ("Telegram", "telegram", "#26A5E4"),
            ("Flask", "flask", "#F5F5F5"),
        ],
        "lines": [
            "Spring Boot · MVC · Security · Data JPA · Hibernate",
            "REST / OpenAPI · aiogram 3 · Telethon · Flask · aiohttp",
            "async services · integrations · Telegram automation",
        ],
    },
    {
        "title": "DATA & PERSISTENCE",
        "accent": "#9a83f5",
        "icons": [
            ("PostgreSQL", "postgresql", "#4169E1"),
            ("Redis", "redis", "#FF4438"),
            ("SQLite", "sqlite", "#5BA4CF"),
            ("Liquibase", "liquibase", "#2962FF"),
        ],
        "lines": [
            "PostgreSQL 14–16 · Redis · SQLite · JDBC · asyncpg",
            "QueryDSL · Liquibase · Flyway · migrations",
            "durable state · transactional workflows · backup / restore",
        ],
    },
    {
        "title": "BUILD, TEST & QUALITY",
        "accent": "#caa8ff",
        "icons": [
            ("Gradle", "gradle", "#8DD6F9"),
            ("Maven", "apachemaven", "#C71A36"),
            ("JUnit", "junit5", "#25A162"),
            ("Actions", "githubactions", "#2088FF"),
        ],
        "lines": [
            "JUnit 5 · Mockito · Spring Test · Testcontainers",
            "unittest · pytest · Ruff · CI/CD · security gates",
            "QA automation · secret scanning · fail-closed verification",
        ],
    },
    {
        "title": "PLATFORM & AUTOMATION",
        "accent": "#a98df8",
        "icons": [
            ("Docker", "docker", "#2496ED"),
            ("Linux", "linux", "#FCC624"),
            ("Android", "android", "#3DDC84"),
            ("Git", "git", "#F05032"),
            ("IntelliJ", "intellijidea", "#F5F5F5"),
        ],
        "lines": [
            "Docker Compose · Linux · systemd · GHCR · GitHub Actions",
            "Redroid · ADB · Frida · SSH tunnels · PowerShell",
            "production deploy · rollback · observability · Trivy / SBOM",
        ],
    },
    {
        "title": "AI, MEDIA & INTEGRATION",
        "accent": "#f0a9d4",
        "icons": [
            ("OpenAI", "openai", "#F5F5F5"),
            ("Ollama", "ollama", "#F5F5F5"),
        ],
        "lines": [
            "OpenAI Responses API · Structured Outputs · image providers",
            "Ollama · Qwen VL · Pillow · cryptography · PyYAML",
            "mitmproxy · fallback pipelines · provider routing",
        ],
    },
]


def fetch_simple_icon(slug: str) -> str | None:
    url = f"{SIMPLE}/{slug}.svg"
    request = urllib.request.Request(url, headers={"User-Agent": "stellmaria-profile-builder"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except Exception:
        return None
    match = re.search(r'<path[^>]*d="([^"]+)"', raw)
    return match.group(1) if match else None


def icon_markup(name: str, slug: str, color: str, x: float, y: float) -> str:
    path = fetch_simple_icon(slug)
    safe_name = html.escape(name)
    parts = [
        f'<g transform="translate({x:.1f} {y:.1f})">',
        '<rect width="50" height="62" rx="13" fill="#171423" stroke="#3c3050"/>',
    ]
    if path:
        parts.append(
            f'<g transform="translate(10 8) scale(1.25)"><path d="{path}" fill="{color}"/></g>'
        )
    else:
        initial = html.escape(name[:2].upper())
        parts.extend([
            f'<circle cx="25" cy="24" r="15" fill="{color}" opacity=".18"/>',
            f'<text x="25" y="28" text-anchor="middle" fill="{color}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10" font-weight="700">{initial}</text>',
        ])
    parts.extend([
        f'<text x="25" y="54" text-anchor="middle" fill="#a99bb8" font-family="Inter,Segoe UI,sans-serif" font-size="7.7">{safe_name}</text>',
        '</g>',
    ])
    return "".join(parts)


def animated_lines(lines: list[str], y: float) -> str:
    timings = [
        ("0;1;1;0;0", "0;.04;.29;.34;1"),
        ("0;0;1;1;0;0", "0;.32;.36;.62;.67;1"),
        ("0;0;1;1;0", "0;.65;.69;.95;1"),
    ]
    out: list[str] = []
    for line, (values, key_times) in zip(lines, timings):
        out.append(
            f'<text x="202.5" y="{y}" text-anchor="middle" fill="#b9a9c9" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.4" opacity="0">'
            f'{html.escape(line)}'
            f'<animate attributeName="opacity" values="{values}" keyTimes="{key_times}" dur="12s" repeatCount="indefinite"/>'
            '</text>'
        )
    return "".join(out)


def build() -> str:
    width = 920
    height = 725
    panel_w = 405
    panel_h = 176
    left = 42
    top = 104
    gap_x = 28
    gap_y = 20

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Animated engineering toolkit">',
        '<defs>',
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#080914"/><stop offset=".5" stop-color="#100d1d"/><stop offset="1" stop-color="#1b1027"/></linearGradient>',
        '<linearGradient id="edge" x1="0" x2="1"><stop stop-color="#d8b4fe"/><stop offset=".5" stop-color="#8f7cf7"/><stop offset="1" stop-color="#efa5d1"/></linearGradient>',
        '<filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '</defs>',
        '<rect x="1" y="1" width="918" height="723" rx="28" fill="url(#bg)" stroke="#39294d"/>',
        '<circle cx="69" cy="43" r="2" fill="#d8b4fe"><animate attributeName="opacity" values=".2;1;.2" dur="3.2s" repeatCount="indefinite"/></circle>',
        '<circle cx="842" cy="46" r="1.7" fill="#efa5d1"><animate attributeName="opacity" values="1;.15;1" dur="4.3s" repeatCount="indefinite"/></circle>',
        '<text x="46" y="47" fill="#f6efff" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="20" font-weight="700">ENGINEERING TOOLKIT</text>',
        '<text x="46" y="71" fill="#9f90ae" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10.5">derived from 15 owned repositories · private names stay private</text>',
        '<text x="874" y="47" text-anchor="end" fill="#c7b4da" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10">STACK SIGNAL</text>',
        '<rect x="760" y="61" width="114" height="2" rx="1" fill="url(#edge)" opacity=".72" filter="url(#glow)"><animate attributeName="x" values="760;790;760" dur="5s" repeatCount="indefinite"/><animate attributeName="width" values="114;84;114" dur="5s" repeatCount="indefinite"/></rect>',
    ]

    for idx, panel in enumerate(PANELS):
        row = idx // 2
        col = idx % 2
        x = left + col * (panel_w + gap_x)
        y = top + row * (panel_h + gap_y)
        accent = panel["accent"]
        svg.extend([
            f'<g transform="translate({x} {y})">',
            f'<rect width="{panel_w}" height="{panel_h}" rx="22" fill="#13101f" stroke="#3d2e51"><animate attributeName="stroke" values="#3d2e51;{accent};#3d2e51" dur="8s" begin="{idx * 1.1}s" repeatCount="indefinite"/></rect>',
            f'<rect x="18" y="16" width="4" height="18" rx="2" fill="{accent}"><animate attributeName="opacity" values=".3;1;.3" dur="3.6s" begin="{idx * .35}s" repeatCount="indefinite"/></rect>',
            f'<text x="32" y="30" fill="#f0e7fb" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11.5" font-weight="700">{html.escape(panel["title"])}</text>',
            '<circle cx="382" cy="23" r="1.7" fill="#c4a5ef"><animate attributeName="opacity" values=".2;1;.2" dur="4s" repeatCount="indefinite"/></circle>',
        ])
        icons = panel["icons"]
        count = len(icons)
        if count:
            total_width = count * 50
            available_gap = max(0, 355 - total_width)
            step = 50 + (available_gap / max(1, count - 1))
            start_x = 25
            for j, (name, slug, color) in enumerate(icons):
                svg.append(icon_markup(name, slug, color, start_x + j * step, 48))
        svg.append(animated_lines(panel["lines"], 154))
        svg.append('</g>')

    svg.extend([
        '<rect x="76" y="697" width="768" height="2" rx="1" fill="url(#edge)" opacity=".48" filter="url(#glow)"><animate attributeName="x" values="76;126;76" dur="6s" repeatCount="indefinite"/><animate attributeName="width" values="768;668;768" dur="6s" repeatCount="indefinite"/></rect>',
        '<text x="460" y="714" text-anchor="middle" fill="#776a87" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9">systems · data · automation · delivery · AI integration</text>',
        '</svg>',
    ])
    result = "".join(svg)
    ET.fromstring(result)
    return result


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT}")
