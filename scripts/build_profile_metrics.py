from __future__ import annotations

import json
import os
import urllib.request
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile-metrics-live.svg"
USERNAME = os.environ.get("PROFILE_USERNAME", "Stellmaria")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TIMEZONE_NAME = os.environ.get("PROFILE_TIMEZONE", "Europe/Minsk")
try:
    TIMEZONE = ZoneInfo(TIMEZONE_NAME)
except ZoneInfoNotFoundError:
    if TIMEZONE_NAME != "Europe/Minsk":
        raise
    # Windows' embeddable Python can lack IANA tzdata. Minsk is UTC+3 year-round.
    TIMEZONE = timezone(timedelta(hours=3), "Europe/Minsk")
API = "https://api.github.com"


def request_json(url: str, *, data: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "stellmaria-profile-metrics",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def contribution_year(year: int, start: datetime, end: datetime) -> tuple[int, dict[date, int]]:
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    payload = request_json(
        f"{API}/graphql",
        data={
            "query": query,
            "variables": {
                "login": USERNAME,
                "from": start.isoformat().replace("+00:00", "Z"),
                "to": end.isoformat().replace("+00:00", "Z"),
            },
        },
    )
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days: dict[date, int] = {}
    for week in calendar.get("weeks", []):
        for item in week.get("contributionDays", []):
            days[date.fromisoformat(item["date"])] = int(item.get("contributionCount", 0))
    return int(calendar.get("totalContributions", 0)), days


def streaks(days: dict[date, int], today: date) -> tuple[int, int]:
    if not days:
        return 0, 0
    first = min(days)
    last = max(days)
    longest = 0
    running = 0
    cursor = first
    while cursor <= last:
        if days.get(cursor, 0) > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
        cursor += timedelta(days=1)

    anchor = today if days.get(today, 0) > 0 else today - timedelta(days=1)
    if days.get(anchor, 0) <= 0:
        return 0, longest
    current = 0
    cursor = anchor
    while days.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def metric(x: int, label: str, value: str, note: str) -> str:
    return (
        f'<g transform="translate({x} 98)">'
        '<rect width="196" height="94" rx="20" fill="#141120" stroke="#3c2e50"/>'
        f'<text x="18" y="29" fill="#aa98bd" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.5" font-weight="700">{label}</text>'
        f'<text x="18" y="65" fill="#f7f0ff" font-family="Inter,Segoe UI,sans-serif" font-size="28" font-weight="700">{value}</text>'
        f'<text x="18" y="82" fill="#776b84" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="8.5">{note}</text>'
        '</g>'
    )


def build() -> str:
    profile = request_json(f"{API}/users/{USERNAME}")
    created = datetime.fromisoformat(str(profile["created_at"]).replace("Z", "+00:00"))
    now = datetime.now(UTC)
    local_now = now.astimezone(TIMEZONE)
    first_year = created.year
    totals: dict[int, int] = {}
    all_days: dict[date, int] = {}

    for year in range(first_year, now.year + 1):
        start = datetime(year, 1, 1, tzinfo=UTC)
        if year == first_year and created > start:
            start = created
        end = datetime(year, 12, 31, 23, 59, 59, tzinfo=UTC)
        if year == now.year:
            end = now
        total, days = contribution_year(year, start, end)
        totals[year] = total
        all_days.update(days)

    total_all = sum(totals.values())
    current, longest = streaks(all_days, local_now.date())
    followers = int(profile.get("followers", 0))
    refreshed = local_now.strftime("%Y-%m-%d · %H:%M Minsk")

    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="300" viewBox="0 0 920 300" role="img" aria-label="GitHub contribution metrics since 2022">',
        '<defs>',
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#080914"/><stop offset=".5" stop-color="#100d1d"/><stop offset="1" stop-color="#1b1027"/></linearGradient>',
        '<linearGradient id="accent" x1="0" x2="1"><stop stop-color="#d8b4fe"/><stop offset=".5" stop-color="#8f7cf7"/><stop offset="1" stop-color="#efa5d1"/></linearGradient>',
        '<filter id="glow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '</defs>',
        '<rect x="1" y="1" width="918" height="298" rx="28" fill="url(#bg)" stroke="#39294d"/>',
        '<circle cx="64" cy="42" r="2" fill="#d8b4fe"><animate attributeName="opacity" values=".2;1;.2" dur="4s" repeatCount="indefinite"/></circle>',
        '<circle cx="853" cy="45" r="1.7" fill="#efa5d1"><animate attributeName="opacity" values="1;.2;1" dur="4s" repeatCount="indefinite"/></circle>',
        '<text x="44" y="49" fill="#f6efff" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="19" font-weight="700">GITHUB AT A GLANCE</text>',
        f'<text x="44" y="73" fill="#998aaa" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10.5">contribution history since {first_year} · refreshed {refreshed}</text>',
        metric(44, "CONTRIBUTIONS SINCE 2022", f"{total_all:,}", "GitHub contribution calendar"),
        metric(254, "CURRENT STREAK", str(current), "consecutive active days"),
        metric(464, "LONGEST STREAK", str(longest), "best active-day run"),
        metric(674, "FOLLOWERS", str(followers), "public profile signal"),
        '<text x="44" y="224" fill="#a895bb" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.5" font-weight="700">YEARLY CONTRIBUTION SIGNAL</text>',
    ]

    years = list(totals)
    max_total = max(totals.values()) if totals else 1
    bar_x = 44
    available = 832
    gap = 12
    bar_w = (available - gap * (len(years) - 1)) / max(1, len(years))
    for idx, year in enumerate(years):
        value = totals[year]
        x = bar_x + idx * (bar_w + gap)
        fill_w = max(3.0, bar_w * (value / max_total if max_total else 0))
        svg.append(f'<rect x="{x:.1f}" y="241" width="{bar_w:.1f}" height="12" rx="6" fill="#20182d"/>')
        svg.append(f'<rect x="{x:.1f}" y="241" width="{fill_w:.1f}" height="12" rx="6" fill="url(#accent)" opacity=".78"><animate attributeName="opacity" values=".48;.92;.48" dur="4s" begin="{idx * .35}s" repeatCount="indefinite"/></rect>')
        svg.append(f'<text x="{x + bar_w / 2:.1f}" y="272" text-anchor="middle" fill="#8f819f" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9">{year} · {value:,}</text>')

    svg.extend([
        '<rect x="76" y="286" width="768" height="2" rx="1" fill="url(#accent)" opacity=".45" filter="url(#glow)"><animate attributeName="x" values="76;126;76" dur="6s" repeatCount="indefinite"/><animate attributeName="width" values="768;668;768" dur="6s" repeatCount="indefinite"/></rect>',
        '</svg>',
    ])
    return "".join(svg)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN is required")
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT}")
