from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "engineering-toolkit-live.svg"

DEVICON = "https://raw.githubusercontent.com/devicons/devicon/master/icons"
SIMPLE = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons"

PANELS = [
    {
        "title": "LANGUAGES & WEB",
        "accent": "#d8b4fe",
        "icons": [
            ("Java", f"{DEVICON}/java/java-original.svg"),
            ("Python", f"{DEVICON}/python/python-original.svg"),
            ("JavaScript", f"{DEVICON}/javascript/javascript-original.svg"),
            ("HTML5", f"{DEVICON}/html5/html5-original.svg"),
            ("CSS3", f"{DEVICON}/css3/css3-original.svg"),
            ("Bash", f"{DEVICON}/bash/bash-original.svg"),
            ("PowerShell", f"{DEVICON}/powershell/powershell-original.svg"),
        ],
        "lines": [
            "Java 17 · Python 3.13 · JavaScript · SQL / PLpgSQL",
            "backend-first · scripting · static web · automation",
            "public + private repository signal",
        ],
    },
    {
        "title": "BACKEND & APIs",
        "accent": "#efa5d1",
        "icons": [
            ("Spring", f"{DEVICON}/spring/spring-original.svg"),
            ("Hibernate", f"{DEVICON}/hibernate/hibernate-original.svg"),
            ("Thymeleaf", f"{DEVICON}/thymeleaf/thymeleaf-original.svg"),
            ("OpenAPI", f"{DEVICON}/openapi/openapi-original.svg"),
            ("Telegram", f"{SIMPLE}/telegram.svg"),
        ],
        "lines": [
            "Spring Boot · Security · Data JPA · Hibernate · Thymeleaf",
            "REST / OpenAPI · aiogram 3 · Telethon · Flask · aiohttp",
            "Telegram automation · async service boundaries",
        ],
    },
    {
        "title": "DATA & PERSISTENCE",
        "accent": "#9a83f5",
        "icons": [
            ("PostgreSQL", f"{DEVICON}/postgresql/postgresql-original.svg"),
            ("Redis", f"{DEVICON}/redis/redis-original.svg"),
            ("SQLite", f"{DEVICON}/sqlite/sqlite-original.svg"),
            ("Liquibase", f"{DEVICON}/liquibase/liquibase-original.svg"),
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
            ("Gradle", f"{DEVICON}/gradle/gradle-original.svg"),
            ("Maven", f"{DEVICON}/maven/maven-original.svg"),
            ("JUnit", f"{DEVICON}/junit/junit-original.svg"),
            ("GitHub Actions", f"{DEVICON}/githubactions/githubactions-original.svg"),
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
            ("Docker", f"{DEVICON}/docker/docker-original.svg"),
            ("Linux", f"{DEVICON}/linux/linux-original.svg"),
            ("Android", f"{DEVICON}/android/android-original.svg"),
            ("Git", f"{DEVICON}/git/git-original.svg"),
            ("IntelliJ", f"{DEVICON}/intellij/intellij-original.svg"),
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
        "icons": [],
        "lines": [
            "OpenAI Responses API · Structured Outputs · image providers",
            "Ollama · Qwen VL · Pillow · cryptography · PyYAML",
            "mitmproxy · fallback pipelines · provider routing",
        ],
    },
]


def fetch_svg(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "stellmaria-profile-builder"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def namespace_svg(svg: str, prefix: str) -> tuple[str, str]:
    viewbox_match = re.search(r'viewBox="([^"]+)"', svg)
    viewbox = viewbox_match.group(1) if viewbox_match else "0 0 128 128"
    ids = re.findall(r'id="([^"]+)"', svg)
    for old in ids:
        new = f"{prefix}-{old}"
        svg = svg.replace(f'id="{old}"', f'id="{new}"')
        svg = svg.replace(f'url(#{old})', f'url(#{new})')
        svg = svg.replace(f'href="#{old}"', f'href="#{new}"')
        svg = svg.replace(f'xlink:href="#{old}"', f'xlink:href="#{new}"')
    inner_match = re.search(r"<svg[^>]*>(.*)</svg>\s*$", svg, re.S)
    if not inner_match:
        raise ValueError("Could not extract SVG body")
    inner = re.sub(r"<title>.*?</title>", "", inner_match.group(1), flags=re.S)
    return viewbox, inner


def icon_markup(name: str, url: str, x: float, y: float, index: int) -> str:
    raw = fetch_svg(url)
    prefix = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") + f"-{index}"
    viewbox, inner = namespace_svg(raw, prefix)
    if "simple-icons" in url:
        inner = inner.replace("<path ", '<path fill="#26A5E4" ')
    return (
        f'<g transform="translate({x} {y})">'
        '<rect width="50" height="50" rx="13" fill="#171423" stroke="#3c3050"/>'
        f'<svg x="9" y="9" width="32" height="32" viewBox="{viewbox}" preserveAspectRatio="xMidYMid meet">{inner}</svg>'
        f'<text x="25" y="67" text-anchor="middle" fill="#a99bb8" font-family="Inter,Segoe UI,sans-serif" font-size="8.5">{name}</text>'
        '</g>'
    )


def animated_lines(lines: list[str], x: float, y: float, width: float) -> str:
    duration = 12
    parts: list[str] = []
    for idx, line in enumerate(lines):
        begin = idx * 4
        parts.append(
            f'<text x="{x + width / 2}" y="{y}" text-anchor="middle" fill="#b9a9c9" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10.5" opacity="0">'
            f'{line}'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.78;1" dur="4s" begin="{begin}s" repeatCount="indefinite"/>'
            '</text>'
        )
    return "".join(parts)


def build() -> str:
    width = 920
    height = 705
    panel_w = 405
    panel_h = 172
    left = 42
    top = 108
    gap_x = 28
    gap_y = 22

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Animated engineering toolkit">',
        '<defs>',
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#080914"/><stop offset=".5" stop-color="#100d1d"/><stop offset="1" stop-color="#1b1027"/></linearGradient>',
        '<linearGradient id="edge" x1="0" x2="1"><stop stop-color="#d8b4fe"/><stop offset=".5" stop-color="#8f7cf7"/><stop offset="1" stop-color="#efa5d1"/></linearGradient>',
        '<filter id="glow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '</defs>',
        '<rect x="1" y="1" width="918" height="703" rx="28" fill="url(#bg)" stroke="#39294d"/>',
        '<circle cx="69" cy="45" r="2" fill="#d8b4fe"><animate attributeName="opacity" values=".2;1;.2" dur="3.2s" repeatCount="indefinite"/></circle>',
        '<circle cx="842" cy="48" r="1.7" fill="#efa5d1"><animate attributeName="opacity" values="1;.15;1" dur="4.3s" repeatCount="indefinite"/></circle>',
        '<text x="46" y="48" fill="#f6efff" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="20" font-weight="700">ENGINEERING TOOLKIT</text>',
        '<text x="46" y="73" fill="#9f90ae" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10.5">derived from 15 owned repositories · private names stay private</text>',
        '<text x="874" y="49" text-anchor="end" fill="#c7b4da" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10">STACK SIGNAL</text>',
        '<rect x="760" y="62" width="114" height="2" rx="1" fill="url(#edge)" opacity=".7" filter="url(#glow)"><animate attributeName="x" values="760;790;760" dur="5s" repeatCount="indefinite"/><animate attributeName="width" values="114;84;114" dur="5s" repeatCount="indefinite"/></rect>',
    ]

    icon_index = 0
    for idx, panel in enumerate(PANELS):
        row = idx // 2
        col = idx % 2
        x = left + col * (panel_w + gap_x)
        y = top + row * (panel_h + gap_y)
        accent = panel["accent"]
        svg.extend([
            f'<g transform="translate({x} {y})">',
            f'<rect width="{panel_w}" height="{panel_h}" rx="22" fill="#13101f" stroke="#3d2e51"/>',
            f'<rect x="18" y="18" width="4" height="18" rx="2" fill="{accent}"><animate attributeName="opacity" values=".35;1;.35" dur="3.6s" begin="{idx * .35}s" repeatCount="indefinite"/></rect>',
            f'<text x="32" y="32" fill="#f0e7fb" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" font-weight="700">{panel["title"]}</text>',
            '<circle cx="382" cy="23" r="1.7" fill="#c4a5ef"><animate attributeName="opacity" values=".2;1;.2" dur="4s" repeatCount="indefinite"/></circle>',
        ])
        icons = panel["icons"]
        if icons:
            start_x = 22
            usable = 360
            step = usable / max(1, len(icons) - 1) if len(icons) > 1 else 0
            for j, (name, url) in enumerate(icons):
                ix = start_x + j * step
                svg.append(icon_markup(name, url, ix, 52, icon_index))
                icon_index += 1
        else:
            pills = ["OpenAI", "Ollama / Qwen VL", "Pillow", "cryptography", "mitmproxy"]
            px = 22
            for pidx, pill in enumerate(pills):
                pw = 58 + len(pill) * 3.7
                svg.append(
                    f'<g transform="translate({px} {62 + (pidx % 2) * 42})">'
                    f'<rect width="{pw:.0f}" height="28" rx="14" fill="#1d1729" stroke="#4a365f"/>'
                    f'<text x="{pw / 2:.1f}" y="18" text-anchor="middle" fill="#d8c8e8" font-family="Inter,Segoe UI,sans-serif" font-size="10">{pill}</text>'
                    '</g>'
                )
                px += pw + 9
                if px > 320:
                    px = 22
        svg.append(animated_lines(panel["lines"], 12, 157, panel_w - 24))
        svg.append('</g>')

    svg.extend([
        '<rect x="76" y="677" width="768" height="2" rx="1" fill="url(#edge)" opacity=".48" filter="url(#glow)"><animate attributeName="x" values="76;126;76" dur="6s" repeatCount="indefinite"/><animate attributeName="width" values="768;668;768" dur="6s" repeatCount="indefinite"/></rect>',
        '<text x="460" y="693" text-anchor="middle" fill="#776a87" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9">systems · data · automation · delivery · AI integration</text>',
        '</svg>',
    ])
    return "".join(svg)


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT}")
