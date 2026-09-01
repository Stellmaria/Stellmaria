from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PULSE_OUTPUT = ROOT / "assets" / "profile-stats.svg"
ACTIVITY_OUTPUT = ROOT / "assets" / "contribution-observatory.svg"
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


def txt(
    x: float,
    y: float,
    value: str,
    *,
    size: int,
    fill: str,
    weight: int = 400,
    anchor: str = "start",
    family: str = "ui-monospace,SFMono-Regular,Menlo,monospace",
) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
    )


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


def fetch_contribution_data() -> dict[str, Any]:
    empty = {
        "total": None,
        "restricted": None,
        "commits": None,
        "issues": None,
        "pull_requests": None,
        "reviews": None,
        "days": [],
    }
    if not TOKEN:
        return empty

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          restrictedContributionsCount
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                weekday
              }
            }
          }
        }
      }
    }
    """
    try:
        payload = request_json(
            f"{API}/graphql",
            data={"query": query, "variables": {"login": USERNAME}},
        )
        collection = payload["data"]["user"]["contributionsCollection"]
        calendar = collection["contributionCalendar"]
        days = [
            day
            for week in calendar.get("weeks", [])
            for day in week.get("contributionDays", [])
        ]
        return {
            "total": int(calendar.get("totalContributions", 0)),
            "restricted": int(collection.get("restrictedContributionsCount", 0)),
            "commits": int(collection.get("totalCommitContributions", 0)),
            "issues": int(collection.get("totalIssueContributions", 0)),
            "pull_requests": int(collection.get("totalPullRequestContributions", 0)),
            "reviews": int(collection.get("totalPullRequestReviewContributions", 0)),
            "days": days,
        }
    except (
        KeyError,
        TypeError,
        ValueError,
        urllib.error.URLError,
        json.JSONDecodeError,
    ):
        return empty


def metric_value(value: int | None) -> str:
    return f"{value:,}" if value is not None else "private"


def card_defs() -> str:
    return (
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop stop-color="#0a0a15"/><stop offset=".55" stop-color="#11101f"/>'
        '<stop offset="1" stop-color="#181126"/></linearGradient>'
        '<linearGradient id="accent" x1="0" x2="1">'
        '<stop stop-color="#d8b4fe"/><stop offset=".48" stop-color="#9a83f5"/>'
        '<stop offset="1" stop-color="#efa5d1"/></linearGradient>'
        '<filter id="glow"><feGaussianBlur stdDeviation="5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '</defs>'
    )


def build_pulse_svg(
    user: dict[str, Any],
    repos: list[dict[str, Any]],
    languages: Counter[str],
    contributions: dict[str, Any],
) -> str:
    updated = datetime.now(UTC).strftime("%Y-%m-%d")
    total_language_bytes = sum(languages.values())
    top_languages = languages.most_common(6)
    metrics = [
        ("PUBLIC REPOS", str(int(user.get("public_repos", len(repos))))),
        ("FOLLOWERS", str(int(user.get("followers", 0)))),
        ("FOLLOWING", str(int(user.get("following", 0)))),
        ("YEAR CONTRIBUTIONS", metric_value(contributions.get("total"))),
    ]

    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="340" '
        'viewBox="0 0 920 340" role="img" aria-label="GitHub profile pulse">',
        card_defs(),
        '<rect x="1" y="1" width="918" height="338" rx="26" fill="url(#bg)" stroke="#352847"/>',
        '<circle cx="53" cy="39" r="2" fill="#d5b4ff"/>'
        '<circle cx="853" cy="42" r="1.5" fill="#efa5d1"/>'
        '<circle cx="885" cy="294" r="2" fill="#8e76ca"/>',
        txt(42, 48, "GITHUB PULSE", size=17, fill="#f4edff", weight=700),
        txt(42, 72, f"public profile + contribution signal · refreshed {updated}", size=11, fill="#8f829f"),
    ]

    xs = [42, 251, 460, 669]
    widths = [197, 197, 197, 209]
    for (label, value), x, width in zip(metrics, xs, widths):
        svg.append(
            f'<g transform="translate({x} 96)">'
            f'<rect width="{width}" height="88" rx="18" fill="#141221" stroke="#382c4b"/>'
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
            svg.append(
                f'<rect x="{cursor:.1f}" y="239" width="{width:.1f}" height="14" '
                f'rx="4" fill="{color}" opacity=".9"/>'
            )
            cursor += width

        legend_positions = [
            (42, 284),
            (225, 284),
            (408, 284),
            (42, 310),
            (225, 310),
            (408, 310),
        ]
        for index, ((language, byte_count), (x, y)) in enumerate(
            zip(top_languages, legend_positions)
        ):
            share = 100.0 * byte_count / total_language_bytes
            color = LANG_COLORS.get(language, FALLBACK_COLORS[index % len(FALLBACK_COLORS)])
            svg.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{color}"/>')
            svg.append(
                txt(x + 17, y, f"{language}  {share:.1f}%", size=11, fill="#cbbfd7")
            )
    else:
        svg.append(
            txt(
                42,
                286,
                "language data will appear after the next refresh",
                size=11,
                fill="#80748d",
            )
        )

    svg.append(
        txt(
            878,
            313,
            "language mix is public-only; private work is summarized separately",
            size=9,
            fill="#6f647c",
            anchor="end",
        )
    )
    svg.append(
        '<rect x="42" y="326" width="836" height="2" rx="1" '
        'fill="url(#accent)" opacity=".45" filter="url(#glow)"/>'
    )
    svg.append("</svg>")
    return "".join(svg)


def heat_color(count: int, max_count: int) -> str:
    if count <= 0:
        return "#1b1728"
    if max_count <= 1:
        return "#d8b4fe"
    level = math.sqrt(count / max_count)
    if level < 0.25:
        return "#4c396b"
    if level < 0.45:
        return "#6f51a0"
    if level < 0.68:
        return "#9872d2"
    if level < 0.86:
        return "#bd91f0"
    return "#e0c0ff"


def build_activity_svg(contributions: dict[str, Any]) -> str:
    updated = datetime.now(UTC).strftime("%Y-%m-%d")
    days: list[dict[str, Any]] = list(contributions.get("days") or [])
    metrics = [
        ("CONTRIBUTIONS", metric_value(contributions.get("total"))),
        ("PRIVATE SIGNAL", metric_value(contributions.get("restricted"))),
        ("COMMITS", metric_value(contributions.get("commits"))),
        ("PULL REQUESTS", metric_value(contributions.get("pull_requests"))),
        ("REVIEWS", metric_value(contributions.get("reviews"))),
    ]

    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="330" '
        'viewBox="0 0 920 330" role="img" aria-label="Contribution observatory">',
        card_defs(),
        '<rect x="1" y="1" width="918" height="328" rx="26" fill="url(#bg)" stroke="#352847"/>',
        '<circle cx="53" cy="39" r="2" fill="#d5b4ff"/>'
        '<circle cx="852" cy="44" r="1.5" fill="#efa5d1"/>'
        '<circle cx="885" cy="286" r="2" fill="#8e76ca"/>',
        txt(42, 48, "CONTRIBUTION OBSERVATORY", size=17, fill="#f4edff", weight=700),
        txt(
            42,
            72,
            f"rolling GitHub activity · privacy-safe aggregate · refreshed {updated}",
            size=11,
            fill="#8f829f",
        ),
    ]

    xs = [42, 211, 380, 549, 718]
    widths = [157, 157, 157, 157, 160]
    for (label, value), x, width in zip(metrics, xs, widths):
        svg.append(
            f'<g transform="translate({x} 92)">'
            f'<rect width="{width}" height="66" rx="16" fill="#141221" stroke="#382c4b"/>'
            f'{txt(15, 24, label, size=8, fill="#a897bd", weight=700)}'
            f'{txt(15, 50, value, size=22, fill="#f4edff", weight=700, family="Inter,Segoe UI,sans-serif")}'
            '</g>'
        )

    grid_x = 82.0
    grid_y = 188.0
    cell = 9.0
    gap = 3.0
    week_step = cell + gap
    day_step = cell + gap

    if days:
        max_count = max(int(day.get("contributionCount", 0)) for day in days) or 1
        first_date = None
        last_date = None
        week_index_by_key: dict[str, int] = {}
        week_counter = 0
        month_labels: list[tuple[float, str]] = []
        previous_month = None

        for day in days:
            date_value = str(day.get("date", ""))
            if not date_value:
                continue
            if first_date is None:
                first_date = date_value
            last_date = date_value
            year_week = datetime.fromisoformat(date_value).strftime("%G-%V")
            if year_week not in week_index_by_key:
                week_index_by_key[year_week] = week_counter
                month = datetime.fromisoformat(date_value).strftime("%b")
                if month != previous_month and week_counter > 0:
                    month_labels.append((grid_x + week_counter * week_step, month))
                elif week_counter == 0:
                    month_labels.append((grid_x, month))
                previous_month = month
                week_counter += 1

            week_index = week_index_by_key[year_week]
            weekday = int(day.get("weekday", 0))
            count = int(day.get("contributionCount", 0))
            x = grid_x + week_index * week_step
            y = grid_y + weekday * day_step
            svg.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
                f'rx="2" fill="{heat_color(count, max_count)}"/>'
            )

        for x, month in month_labels[:12]:
            svg.append(txt(x, 179, month, size=9, fill="#756982"))

        for weekday, label in ((1, "M"), (3, "W"), (5, "F")):
            svg.append(
                txt(
                    62,
                    grid_y + weekday * day_step + 8,
                    label,
                    size=8,
                    fill="#756982",
                    anchor="middle",
                )
            )

        period = f"{first_date or ''} → {last_date or ''}".strip()
        svg.append(txt(42, 306, period, size=9, fill="#6f647c"))
    else:
        svg.append(
            txt(
                42,
                220,
                "Contribution calendar unavailable for this token scope.",
                size=11,
                fill="#8f829f",
            )
        )

    legend_x = 715
    legend_y = 299
    svg.append(txt(legend_x - 42, legend_y + 7, "less", size=9, fill="#6f647c"))
    for index, color in enumerate(
        ("#1b1728", "#4c396b", "#6f51a0", "#9872d2", "#bd91f0", "#e0c0ff")
    ):
        svg.append(
            f'<rect x="{legend_x + index * 16}" y="{legend_y}" width="10" height="10" '
            f'rx="2" fill="{color}"/>'
        )
    svg.append(txt(legend_x + 104, legend_y + 7, "more", size=9, fill="#6f647c"))

    svg.append(
        '<rect x="42" y="316" width="836" height="2" rx="1" '
        'fill="url(#accent)" opacity=".45" filter="url(#glow)"/>'
    )
    svg.append("</svg>")
    return "".join(svg)


def main() -> None:
    PULSE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        user, repos, languages = fetch_profile()
        contributions = fetch_contribution_data()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not refresh profile stats: {exc}") from exc

    PULSE_OUTPUT.write_text(
        build_pulse_svg(user, repos, languages, contributions),
        encoding="utf-8",
    )
    ACTIVITY_OUTPUT.write_text(
        build_activity_svg(contributions),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
