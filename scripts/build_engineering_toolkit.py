from __future__ import annotations

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "engineering-toolkit-v2.svg"
SIMPLE_ICONS_REVISION = "8a040dd8e1f7d99d27827efd4089a5434fdb7b5c"
SIMPLE = f"https://raw.githubusercontent.com/simple-icons/simple-icons/{SIMPLE_ICONS_REVISION}/icons"

# These vectors are deliberately vendored. Some brands are not present in the
# current Simple Icons catalog, and a missing network asset must never degrade
# the generated profile to a letter placeholder again.
CUSTOM_ICONS = {
    "powershell": (
        '<path d="M23.181 2.974c.568 0 .923.463.792 1.035l-3.659 15.982c-.13.572-.697 1.035-1.265 1.035H.819c-.568 0-.923-.463-.792-1.035L3.686 4.009c.13-.572.697-1.035 1.265-1.035zm-8.375 9.346c.251-.394.227-.905-.09-1.243L9.122 5.125c-.38-.404-1.037-.407-1.466-.003-.429.402-.468 1.056-.088 1.46l4.662 4.96v.11l-7.42 5.374c-.45.327-.533.977-.187 1.453.346.476.991.597 1.44.27l8.229-5.91c.28-.196.438-.365.514-.52zm-2.796 4.399a.928.928 0 0 0-.934.923c0 .51.418.923.934.923h4.433a.928.928 0 0 0 .934-.923.928.928 0 0 0-.934-.923z" fill="{color}"/>'
    ),
    "querydsl": (
        '<circle cx="10" cy="10" r="6.5" fill="none" stroke="{color}" stroke-width="2"/>'
        '<path d="m14.7 14.7 5.1 5.1M7 10h6M10 7v6" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
        '<circle cx="4" cy="4" r="2" fill="{color}"/><circle cx="20" cy="6" r="2" fill="{color}"/>'
    ),
    "systemd": (
        '<path d="M7 3H3v18h4M17 3h4v18h-4" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
        '<circle cx="12" cy="12" r="4" fill="none" stroke="{color}" stroke-width="2"/>'
        '<path d="M12 5.5v2M12 16.5v2M5.5 12h2M16.5 12h2M7.4 7.4l1.4 1.4M15.2 15.2l1.4 1.4M16.6 7.4l-1.4 1.4M8.8 15.2l-1.4 1.4" stroke="{color}" stroke-width="1.5" stroke-linecap="round"/>'
    ),
    "openai": (
        '<path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654 2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z" fill="{color}"/>'
    ),
    "pillow": (
        '<path d="M5 7c0-2 2-3 4-2l3 1 3-1c2-1 4 0 4 2v10c0 2-2 3-4 2l-3-1-3 1c-2 1-4 0-4-2Z" fill="{color}" opacity=".2"/>'
        '<path d="M5 7c0-2 2-3 4-2l3 1 3-1c2-1 4 0 4 2v10c0 2-2 3-4 2l-3-1-3 1c-2 1-4 0-4-2ZM8 9c2 1 6 1 8 0M8 15c2-1 6-1 8 0" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "mitmproxy": (
        '<path d="M3 7h14m0 0-3.5-3.5M17 7l-3.5 3.5M21 17H7m0 0 3.5-3.5M7 17l3.5 3.5" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="4" cy="17" r="2" fill="{color}"/><circle cx="20" cy="7" r="2" fill="{color}"/>'
    ),
    "springsecurity": (
        '<path d="M12 2.5 20 5.7v5.4c0 5.2-3.3 8.7-8 10.4-4.7-1.7-8-5.2-8-10.4V5.7Z" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'
        '<path d="m8.5 12 2.2 2.2 4.9-5" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "telethon": (
        '<circle cx="12" cy="12" r="10" fill="{color}" opacity=".16"/>'
        '<path d="m5 11.5 13-6-4.7 13-2.5-5.1Z" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="m10.8 13.4 2.1-2.1" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>'
    ),
    "asyncpg": (
        '<ellipse cx="12" cy="5.6" rx="7.3" ry="3.1" fill="none" stroke="{color}" stroke-width="1.8"/>'
        '<path d="M4.7 5.6v6.1c0 1.7 3.3 3.1 7.3 3.1s7.3-1.4 7.3-3.1V5.6M4.7 11.7v6.1c0 1.7 3.3 3.1 7.3 3.1s7.3-1.4 7.3-3.1v-6.1" fill="none" stroke="{color}" stroke-width="1.8"/>'
    ),
    "servletjsp": (
        '<path d="M5 2.8h9.5l4.5 4.5v13.9H5Z" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/>'
        '<path d="M14.5 2.8v4.5H19M8 11h8M8 15h5.5" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "mockito": (
        '<circle cx="8" cy="10" r="4" fill="none" stroke="{color}" stroke-width="1.8"/>'
        '<circle cx="16" cy="14" r="4" fill="none" stroke="{color}" stroke-width="1.8"/>'
        '<path d="m10.7 12.7 2.6-1.4M6.8 10h2.4M14.8 14h2.4" fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round"/>'
    ),
    "testcontainers": (
        '<rect x="3.5" y="5" width="17" height="14" rx="2" fill="none" stroke="{color}" stroke-width="1.8"/>'
        '<path d="M8.5 5v14M14 5v14M3.5 10h17M3.5 14.5h17" fill="none" stroke="{color}" stroke-width="1.5"/>'
        '<path d="m16.4 18.6 1.4 1.4 2.8-3" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    "cryptography": (
        '<rect x="5" y="10" width="14" height="11" rx="2" fill="none" stroke="{color}" stroke-width="1.9"/>'
        '<path d="M8.5 10V7.7a3.5 3.5 0 0 1 7 0V10M12 14v3" fill="none" stroke="{color}" stroke-width="1.9" stroke-linecap="round"/>'
    ),
    "sshtunnel": (
        '<rect x="3" y="4.5" width="18" height="15" rx="2" fill="none" stroke="{color}" stroke-width="1.8"/>'
        '<path d="m7 9 3 3-3 3M12.5 15H17" fill="none" stroke="{color}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
}

PANELS = [
    {
        "title": "LANGUAGES & WEB",
        "accent": "#d8b4fe",
        "icons": [
            ("Java", "openjdk", "#437291"),
            ("Python", "python", "#3776AB"),
            ("JavaScript", "javascript", "#F7DF1E"),
            ("HTML5", "html5", "#E34F26"),
            ("CSS3", "css", "#663399"),
            ("PowerShell", "powershell", "#5391FE"),
        ],
        "lines": [
            "Java 8–17 · Python 3.12–3.14 · JavaScript · SQL / PLpgSQL",
            "HTML5 · CSS3 · jQuery · Bash · PowerShell",
            "backend-first engineering across public and private work",
        ],
    },
    {
        "title": "BACKEND & APIs",
        "accent": "#efa5d1",
        "icons": [
            ("Spring", "spring", "#6DB33F"),
            ("Security", "springsecurity", "#6DB33F"),
            ("Hibernate", "hibernate", "#59666C"),
            ("Servlet/JSP", "servletjsp", "#f6efff"),
            ("aiogram", "telegram", "#26A5E4"),
            ("Telethon", "telethon", "#8f7cf7"),
            ("Flask", "flask", "#F5F5F5"),
        ],
        "lines": [
            "Spring Boot · MVC · Security · Data JPA · Hibernate",
            "Jakarta Servlet · JSP · Thymeleaf · REST / OpenAPI",
            "aiogram 3 · Telethon · Flask · aiohttp · async services",
        ],
    },
    {
        "title": "DATA & PERSISTENCE",
        "accent": "#9a83f5",
        "icons": [
            ("PostgreSQL", "postgresql", "#4169E1"),
            ("asyncpg", "asyncpg", "#5BA4CF"),
            ("Redis", "redis", "#FF4438"),
            ("SQLite", "sqlite", "#5BA4CF"),
            ("Liquibase", "liquibase", "#2962FF"),
            ("Flyway", "flyway", "#CC0200"),
            ("QueryDSL", "querydsl", "#D8B4FE"),
        ],
        "lines": [
            "PostgreSQL 14–17 · Redis · SQLite · JDBC · asyncpg",
            "QueryDSL · Liquibase · Flyway · migrations · durable state",
            "transactional workflows · queues · backup / restore · query stats",
        ],
    },
    {
        "title": "BUILD, TEST & QUALITY",
        "accent": "#caa8ff",
        "icons": [
            ("Gradle", "gradle", "#8DD6F9"),
            ("Maven", "apachemaven", "#C71A36"),
            ("JUnit", "junit5", "#25A162"),
            ("Mockito", "mockito", "#a98df8"),
            ("T-containers", "testcontainers", "#8DD6F9"),
            ("pytest", "pytest", "#0A9EDC"),
            ("Ruff", "ruff", "#D7FF64"),
            ("Actions", "githubactions", "#2088FF"),
        ],
        "lines": [
            "JUnit 5 · Mockito · Spring Test · Testcontainers · pytest",
            "unittest · Ruff · CI/CD · security gates · regression checks",
            "QA automation · secret scanning · fail-closed delivery",
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
            ("systemd", "systemd", "#D8B4FE"),
            ("SSH tunnel", "sshtunnel", "#8f7cf7"),
        ],
        "lines": [
            "Docker Compose · Linux · systemd · GHCR · GitHub Actions",
            "Redroid · ADB · Frida · SSH tunnels · PowerShell",
            "non-root containers · rollback · backup / restore · Trivy / SBOM",
        ],
    },
    {
        "title": "AI, MEDIA & INTEGRATION",
        "accent": "#f0a9d4",
        "icons": [
            ("OpenAI", "openai", "#F5F5F5"),
            ("Ollama", "ollama", "#F5F5F5"),
            ("Qwen VL", "alibabacloud", "#FF6A00"),
            ("Pillow", "pillow", "#65B8C2"),
            ("crypto", "cryptography", "#d8b4fe"),
            ("PyYAML", "yaml", "#CB171E"),
            ("mitmproxy", "mitmproxy", "#D8B4FE"),
        ],
        "lines": [
            "OpenAI Responses API · Structured Outputs · image providers",
            "Ollama · Qwen VL · Pillow · cryptography · PyYAML",
            "mitmproxy · fallback pipelines · provider routing",
        ],
    },
]


def fetch_simple_icon(slug: str) -> str:
    url = f"{SIMPLE}/{slug}.svg"
    request = urllib.request.Request(url, headers={"User-Agent": "stellmaria-profile-builder"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"Unable to fetch required icon: {slug}") from exc
    match = re.search(r'<path[^>]*d="([^"]+)"', raw)
    if not match:
        raise RuntimeError(f"Required icon has no SVG path: {slug}")
    return match.group(1)


def icon_markup(
    name: str,
    slug: str,
    color: str,
    x: float,
    y: float,
    card_width: float,
    icon_scale: float,
    label_size: float,
) -> str:
    safe_name = html.escape(name)
    parts = [
        f'<g transform="translate({x:.1f} {y:.1f})">',
        f'<rect width="{card_width}" height="62" rx="13" fill="#171423" stroke="#3c3050"/>',
    ]
    icon_size = 24 * icon_scale
    icon_x = (card_width - icon_size) / 2
    custom = CUSTOM_ICONS.get(slug)
    if custom:
        parts.append(
            f'<g transform="translate({icon_x:.2f} 8) scale({icon_scale})">{custom.format(color=color)}</g>'
        )
    else:
        path = fetch_simple_icon(slug)
        parts.append(
            f'<g transform="translate({icon_x:.2f} 8) scale({icon_scale})"><path d="{path}" fill="{color}"/></g>'
        )
    parts.extend([
        f'<text x="{card_width / 2:.2f}" y="54" text-anchor="middle" fill="#a99bb8" font-family="Inter,Segoe UI,sans-serif" font-size="{label_size}">{safe_name}</text>',
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
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.15" opacity="0">'
            f'{html.escape(line)}'
            f'<animate attributeName="opacity" values="{values}" keyTimes="{key_times}" dur="12s" repeatCount="indefinite"/>'
            '</text>'
        )
    return "".join(out)


def build() -> str:
    width = 920
    height = 700
    panel_w = 405
    panel_h = 176
    left = 42
    top = 82
    gap_x = 28
    gap_y = 20

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Animated engineering toolkit">',
        '<defs>',
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#080914"/><stop offset=".5" stop-color="#100d1d"/><stop offset="1" stop-color="#1b1027"/></linearGradient>',
        '<linearGradient id="edge" x1="0" x2="1"><stop stop-color="#d8b4fe"/><stop offset=".5" stop-color="#8f7cf7"/><stop offset="1" stop-color="#efa5d1"/></linearGradient>',
        '<filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '</defs>',
        '<rect x="1" y="1" width="918" height="698" rx="28" fill="url(#bg)" stroke="#39294d"/>',
        '<circle cx="69" cy="43" r="2" fill="#d8b4fe"><animate attributeName="opacity" values=".2;1;.2" dur="3.2s" repeatCount="indefinite"/></circle>',
        '<circle cx="842" cy="46" r="1.7" fill="#efa5d1"><animate attributeName="opacity" values="1;.15;1" dur="4.3s" repeatCount="indefinite"/></circle>',
        '<text x="46" y="47" fill="#f6efff" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="20" font-weight="700">ENGINEERING TOOLKIT</text>',
        '<text x="874" y="47" text-anchor="end" fill="#c7b4da" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10">VERIFIED STACK · 6 DOMAINS</text>',
        '<rect x="742" y="60" width="132" height="2" rx="1" fill="url(#edge)" opacity=".72" filter="url(#glow)"><animate attributeName="x" values="742;782;742" dur="5s" repeatCount="indefinite"/><animate attributeName="width" values="132;92;132" dur="5s" repeatCount="indefinite"/></rect>',
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
        icon_count = len(icons)
        if icon_count <= 6:
            card_width, gap, icon_scale, label_size = 50.0, 11.0, 1.25, 7.2
        elif icon_count == 7:
            card_width, gap, icon_scale, label_size = 48.0, 5.0, 1.2, 6.7
        else:
            card_width, gap, icon_scale, label_size = 44.0, 3.0, 1.1, 6.05
        row_width = icon_count * card_width + (icon_count - 1) * gap
        start_x = (panel_w - row_width) / 2
        for j, (name, slug, color) in enumerate(icons):
            svg.append(
                icon_markup(
                    name,
                    slug,
                    color,
                    start_x + j * (card_width + gap),
                    48,
                    card_width,
                    icon_scale,
                    label_size,
                )
            )
        svg.append(animated_lines(panel["lines"], 154))
        svg.append('</g>')

    svg.extend([
        '<rect x="76" y="671" width="768" height="2" rx="1" fill="url(#edge)" opacity=".48" filter="url(#glow)"><animate attributeName="x" values="76;126;76" dur="6s" repeatCount="indefinite"/><animate attributeName="width" values="768;668;768" dur="6s" repeatCount="indefinite"/></rect>',
        '<text x="460" y="688" text-anchor="middle" fill="#776a87" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9">systems · data · automation · delivery · AI integration</text>',
        '</svg>',
    ])
    result = "".join(svg)
    ET.fromstring(result)
    return result


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT}")
