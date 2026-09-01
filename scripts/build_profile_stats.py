from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile-stats.svg"
USERNAME = os.environ.get("PROFILE_USERNAME", "Stellmaria")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"

LANG_COLORS = {
    "Java": "#b07219",
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "CSS": "#663399",
    "Shell": "#89e051",
    "Kotlin": "#A97BFF",
    "C#": "#178600",
    "C++": "#f34b7d",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "PLpgSQL": "#70b7ff",
}
FALLBACK_COLORS = ["#d8b4fe", "#9a83f5", "#efa5d1", "#70b7ff", "#f2b184", "#77d8c9"]


def headers() -> dict[str, str]:
    result = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "stellmaria-profile-stats",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        result["Authorization"] = f"Bearer {TOKEN}"
    return result


def request_json(url: str, *, data: dict[str, Any] | None = None) -> Any:
    body = None
    req_headers = headers()
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=req_headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)


def contribution_total() -> int | None:
    if not TOKEN:
        return None
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar { totalContributions }
        }
      }
    }
    """
    try:
        payload = request_json(
            f"{API}/graphql",
            data={"query": query, "variables": {"login": USERNAME}},
        )
        return int(payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"])
    except (KeyError, TypeError, ValueError, urllib.error.URLError):
        return None


def fetch_profile() -> tuple[dict[str, Any], list[dict[str, Any]], Counter[str]]:
    user = request_json(f"{API}/users/{USERNAME}")
    repos = request_json(f"{API}/users/{USERNAME}/repos?per_page=100&sort=updated&direction=desc&type=public")
    owned = [repo for repo in repos if not repo.get("fork")]
    owned.sort(key=lambda repo: (int(repo.get("stargazers_count", 0)), repo.get("pushed_at") or ""), reverse=True)

    languages: Counter[str] = Counter()
    for repo in owned[:30]:
        try:
            language_map = request_json(f"{API}/repos/{repo['owner']['login']}/{repo['name']}/languages")
        except urllib.error.URLError:
            continue
        for language, byte_count in language_map.items():
            languages[language] += int(byte_count)

    return user, owned, languages


def txt(x: int, y: int, value: str, *, size: int, fill: str, weight: int = 400, anchor: str = "start", family: str = "ui-monospace,SFMono-Regular,Menlo,monospace") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def build_svg() -> str:
    user, repos, languages = fetch_profile()
    stars = sum(int(repo.get("stargazers_count", 0)) for repo in repos)
    contributions = contribution_total()
    updated = datetime.now(UTC).strftime("%Y-%m-%d")

    total_language_bytes = sum(languages.values())
    top_languages = languages.most_common(6)
    metrics = [
        ("PUBLIC REPOS", str(int(user.get("public_repos", len(repos))))),
        ("FOLLOWERS", str(int(user.get("followers", 0)))),
        ("TOTAL STARS", str(stars)),
        ("YEAR CONTRIBUTIONS", f"{contributions:,}" if contributions is not None else "public"),
    ]

    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="340" viewBox="0 0 920 340" role="img" aria-label="GitHub profile pulse">',
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0a0a15"/><stop offset=".55" stop-color="#11101f"/><stop offset="1" stop-color="#181126"/></linearGradient>'
        '<linearGradient id="accent" x1="0" x2="1"><stop stop-color="#d8b4fe"/><stop offset=".48" stop-color="#9a83f5"/><stop offset="1" stop-color="#efa5d1"/></linearGradient>'
        '<filter id="glow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '</defs>',
        '<rect x="1" y="1" width="918" height="338" rx="26" fill="url(#bg)" stroke="#352847"/>',
        '<circle cx="53" cy="39" r="2" fill="#d5b4ff"/><circle cx="853" cy="42" r="1.5" fill="#efa5d1"/><circle cx="885" cy="294" r="2" fill="#8e76ca"/>',
        txt(42, 48, "GITHUB PULSE", size=17, fill="#f4edff", weight=700),
        txt(42, 72, f"public snapshot · refreshed {updated}", size=11, fill="#8f829f"),
    ]

    xs = [42, 251, 460, 669]
    widths = [197, 197, 197, 209]
    for (label, value), x, width in zip(metrics, xs, widths):
        svg.append(
            f'<g transform="translate({x} 96)"><rect width="{width}" height="88" rx="18" fill="#141221" stroke="#382c4b"/>'
            f'{txt(18, 31, label, size=10, fill="#a897bd", weight=700)}'
            f'{txt(18, 65, value, size=27, fill="#f4edff", weight=700, family="Inter,Segoe UI,sans-serif")}'
            '</g>'
        )

    svg.append(txt(42, 222, "TOP PUBLIC LANGUAGES", size=10, fill="#a897bd", weight=700))
    svg.append('<rect x="42" y="239" width="836" height="14" rx="7" fill="#201a2d"/>')

    cursor = 42.0
    if total_language_bytes > 0:
        for index, (language, byte_count) in enumerate(top_languages):
            share = byte_count / total_language_bytes
            width = max(4.0, 836.0 * share)
            color = LANG_COLORS.get(language, FALLBACK_COLORS[index % len(FALLBACK_COLORS)])
            svg.append(f'<rect x="{cursor:.1f}" y="239" width="{width:.1f}" height="14" rx="4" fill="{color}" opacity=".9"/>')
            cursor += width

        legend_positions = [(42, 284), (225, 284), (408, 284), (42, 310), (225, 310), (408, 310)]
        for index, ((language, byte_count), (x, y)) in enumerate(zip(top_languages, legend_positions)):
            share = 100.0 * byte_count / total_language_bytes
            color = LANG_COLORS.get(language, FALLBACK_COLORS[index % len(FALLBACK_COLORS)])
            svg.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{color}"/>')
            svg.append(txt(x + 17, y, f"{language}  {share:.1f}%", size=11, fill="#cbbfd7"))
    else:
        svg.append(txt(42, 286, "language data will appear after the next refresh", size=11, fill="#80748d"))

    svg.append(txt(878, 313, "owned public repositories", size=10, fill="#6f647c", anchor="end"))
    svg.append('<rect x="42" y="326" width="836" height="2" rx="1" fill="url(#accent)" opacity=".45" filter="url(#glow)"/>')
    svg.append('</svg>')
    return "".join(svg)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        svg = build_svg()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not refresh profile stats: {exc}") from exc
    OUTPUT.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
