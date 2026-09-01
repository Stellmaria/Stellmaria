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

PALETTE = ["#c7a2ff", "#9575ff", "#ef9dcc", "#70b7ff", "#f2b184", "#77d8c9"]
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
}


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
        return int(
            payload["data"]["user"]["contributionsCollection"]["contributionCalendar"][
                "totalContributions"
            ]
        )
    except (KeyError, TypeError, ValueError, urllib.error.URLError):
        return None


def fetch_profile() -> tuple[dict[str, Any], list[dict[str, Any]], Counter[str]]:
    user = request_json(f"{API}/users/{USERNAME}")
    repos = request_json(
        f"{API}/users/{USERNAME}/repos?per_page=100&sort=updated&direction=desc&type=public"
    )
    owned = [repo for repo in repos if not repo.get("fork")]
    owned.sort(
        key=lambda repo: (
            int(repo.get("stargazers_count", 0)),
            repo.get("pushed_at") or "",
        ),
        reverse=True,
    )

    languages: Counter[str] = Counter()
    for repo in owned[:30]:
        try:
            language_map = request_json(
                f"{API}/repos/{repo['owner']['login']}/{repo['name']}/languages"
            )
        except urllib.error.URLError:
            continue
        for language, byte_count in language_map.items():
            languages[language] += int(byte_count)

    return user, owned, languages


def text(x: int, y: int, value: str, *, size: int, fill: str, weight: int = 400, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def build_svg() -> str:
    user, repos, languages = fetch_profile()
    stars = sum(int(repo.get("stargazers_count", 0)) for repo in repos)
    forks = sum(int(repo.get("forks_count", 0)) for repo in repos)
    contributions = contribution_total()
    updated = datetime.now(UTC).strftime("%Y-%m-%d")

    total_language_bytes = sum(languages.values())
    top_languages = languages.most_common(6)

    cards = [
        ("PUBLIC REPOS", str(int(user.get("public_repos", len(repos))))),
        ("FOLLOWERS", str(int(user.get("followers", 0)))),
        ("TOTAL STARS", str(stars)),
        ("YEAR CONTRIBUTIONS", str(contributions) if contributions is not None else "public"),
    ]

    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="326" viewBox="0 0 920 326" role="img" aria-label="GitHub pulse">',
        '<defs><linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#0b0b18"/><stop offset="1" stop-color="#171126"/></linearGradient>'
        '<linearGradient id="shine" x1="0" x2="1"><stop stop-color="#c7a2ff"/><stop offset=".55" stop-color="#9575ff"/><stop offset="1" stop-color="#ef9dcc"/></linearGradient></defs>',
        '<rect x="1" y="1" width="918" height="324" rx="24" fill="url(#bg)" stroke="#34254d"/>',
        '<circle cx="858" cy="42" r="2" fill="#f0a8d5"/><circle cx="884" cy="67" r="1.5" fill="#9270d4"/><circle cx="63" cy="291" r="1.5" fill="#c7a2ff"/>',
        text(42, 48, "GITHUB PULSE", size=18, fill="#efe6ff", weight=700),
        text(42, 72, f"public profile snapshot · refreshed {updated}", size=12, fill="#9788ad"),
    ]

    card_x = [42, 248, 454, 660]
    card_w = [194, 194, 194, 216]
    for (label, value), x, width in zip(cards, card_x, card_w):
        svg.append(
            f'<g transform="translate({x} 96)"><rect width="{width}" height="78" rx="16" fill="#141222" stroke="#392a53"/>'
            f'{text(18, 29, label, size=11, fill="#9d8caf")}'
            f'{text(18, 59, value, size=25, fill="#f1e8ff", weight=700)}'
            '</g>'
        )

    svg.extend(
        [
            text(42, 210, "TOP PUBLIC LANGUAGES", size=13, fill="#cdbbea", weight=700),
            '<rect x="42" y="228" width="834" height="15" rx="7.5" fill="#211a31"/>',
        ]
    )

    cursor = 42.0
    if total_language_bytes > 0:
        for index, (language, byte_count) in enumerate(top_languages):
            share = byte_count / total_language_bytes
            width = max(4.0, 834.0 * share)
            color = LANG_COLORS.get(language, PALETTE[index % len(PALETTE)])
            svg.append(
                f'<rect x="{cursor:.1f}" y="228" width="{width:.1f}" height="15" rx="3" fill="{color}" opacity=".92"/>'
            )
            cursor += width

        legend_x = 42
        legend_y = 270
        for index, (language, byte_count) in enumerate(top_languages):
            share = 100.0 * byte_count / total_language_bytes
            color = LANG_COLORS.get(language, PALETTE[index % len(PALETTE)])
            if index == 3:
                legend_x = 42
                legend_y = 296
            svg.append(f'<circle cx="{legend_x + 5}" cy="{legend_y - 4}" r="5" fill="{color}"/>')
            svg.append(text(legend_x + 17, legend_y, f"{language} {share:.1f}%", size=11, fill="#c6bad6"))
            legend_x += 184
    else:
        svg.append(text(42, 270, "language data will appear after the next refresh", size=11, fill="#7f718f"))

    svg.append(text(876, 310, f"{forks} forks across owned public repos", size=10, fill="#756982", anchor="end"))
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
