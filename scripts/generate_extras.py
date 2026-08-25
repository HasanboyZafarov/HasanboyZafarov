#!/usr/bin/env python3
"""Generate top-languages and contribution-heatmap SVGs.

Self-hosted replacements for the third-party README card services
(github-readme-stats / github-profile-trophy), which are frequently
rate-limited or offline.
"""

import os
import requests
from datetime import datetime

USERNAME = "HasanboyZafarov"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN", "")
STATS_DIR = "stats"

if not GITHUB_TOKEN:
    print("Cannot fetch stats without GitHub token.")
    exit(1)

os.makedirs(STATS_DIR, exist_ok=True)

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

query = """
query {
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
  }
}
""" % USERNAME

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query},
    headers=headers
)
data = response.json()

if "errors" in data:
    print(f"GraphQL Error: {data['errors']}")
    exit(1)

if not data.get("data") or not data["data"].get("user"):
    print(f"API Error: {data}")
    exit(1)

user = data["data"]["user"]
calendar = user["contributionsCollection"]["contributionCalendar"]
weeks = calendar["weeks"]
total_contrib = calendar["totalContributions"]
max_count = max(
    (day["contributionCount"] for week in weeks for day in week["contributionDays"]),
    default=0
)

# ---------------------------------------------------------------------------
# Most used languages
# ---------------------------------------------------------------------------

FALLBACK_COLORS = ["#a78bfa", "#38bdf8", "#34d399", "#fbbf24", "#f472b6", "#f87171"]

totals = {}
colors = {}
for repo in user["repositories"]["nodes"]:
    for edge in repo["languages"]["edges"]:
        name = edge["node"]["name"]
        totals[name] = totals.get(name, 0) + edge["size"]
        colors[name] = edge["node"]["color"] or ""

top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
grand_total = sum(size for _, size in top) or 1

for i, (name, _) in enumerate(top):
    if not colors.get(name):
        colors[name] = FALLBACK_COLORS[i % len(FALLBACK_COLORS)]

BAR_X, BAR_Y, BAR_W, BAR_H = 20, 60, 460, 12
segments = []
legend = []
offset = 0.0
for i, (name, size) in enumerate(top):
    width = BAR_W * size / grand_total
    segments.append(
        f'  <rect x="{BAR_X + offset:.1f}" y="{BAR_Y}" width="{width:.1f}" '
        f'height="{BAR_H}" fill="{colors[name]}"/>'
    )
    col, row = i % 2, i // 2
    lx = BAR_X + col * 235
    ly = 105 + row * 26
    legend.append(
        f'  <circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{colors[name]}"/>\n'
        f'  <text class="lang-name" x="{lx + 18}" y="{ly}">{name}</text>\n'
        f'  <text class="lang-pct" x="{lx + 205}" y="{ly}" text-anchor="end">'
        f'{size / grand_total * 100:.1f}%</text>'
    )
    offset += width

newline = "\n"
lang_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="200" viewBox="0 0 500 200">
  <defs>
    <style>
      .card {{ fill: #1f2937; stroke: #a78bfa; stroke-width: 2; }}
      .title {{ font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; fill: #a78bfa; }}
      .lang-name {{ font-family: 'Courier New', monospace; font-size: 13px; fill: #ffffff; }}
      .lang-pct {{ font-family: 'Courier New', monospace; font-size: 13px; fill: #9ca3af; }}
      .track {{ fill: #111827; }}
    </style>
    <clipPath id="barClip">
      <rect x="{BAR_X}" y="{BAR_Y}" width="{BAR_W}" height="{BAR_H}" rx="6"/>
    </clipPath>
  </defs>

  <rect class="card" x="10" y="10" width="480" height="180" rx="8"/>
  <text class="title" x="20" y="38">Most Used Languages</text>

  <rect class="track" x="{BAR_X}" y="{BAR_Y}" width="{BAR_W}" height="{BAR_H}" rx="6"/>
  <g clip-path="url(#barClip)">
{newline.join(segments)}
  </g>

{newline.join(legend)}
</svg>"""

with open(f"{STATS_DIR}/top-languages.svg", "w", encoding="utf-8") as f:
    f.write(lang_svg)

print(f"[OK] Generated language breakdown: {STATS_DIR}/top-languages.svg")
for name, size in top:
    print(f"   {name}: {size / grand_total * 100:.1f}%")

# ---------------------------------------------------------------------------
# Contribution heatmap
# ---------------------------------------------------------------------------

CELL, GAP = 9, 2
STEP = CELL + GAP
LEVELS = ["#161b22", "#3b2f6b", "#5b46a8", "#8b5cf6", "#c4b5fd"]


def level_for(count):
    if count == 0:
        return LEVELS[0]
    if max_count <= 1:
        return LEVELS[4]
    ratio = count / max_count
    if ratio <= 0.25:
        return LEVELS[1]
    if ratio <= 0.5:
        return LEVELS[2]
    if ratio <= 0.75:
        return LEVELS[3]
    return LEVELS[4]


GRID_X, GRID_Y = 20, 55
cells = []
month_labels = []
seen_months = set()

for wi, week in enumerate(weeks):
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        x = GRID_X + wi * STEP
        y = GRID_Y + ((date.weekday() + 1) % 7) * STEP
        cells.append(
            f'  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{level_for(day["contributionCount"])}"/>'
        )
    first = datetime.strptime(week["contributionDays"][0]["date"], "%Y-%m-%d")
    key = (first.year, first.month)
    if first.day <= 7 and key not in seen_months:
        seen_months.add(key)
        month_labels.append(
            f'  <text class="axis" x="{GRID_X + wi * STEP}" y="{GRID_Y - 8}">'
            f'{first.strftime("%b")}</text>'
        )

svg_w = GRID_X * 2 + len(weeks) * STEP
legend_y = GRID_Y + 7 * STEP + 18
legend_x = svg_w - GRID_X - 5 * STEP - 62
legend_cells = newline.join(
    f'  <rect x="{legend_x + 32 + i * STEP}" y="{legend_y - CELL + 1}" '
    f'width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
    for i, c in enumerate(LEVELS)
)
svg_h = legend_y + 18

heatmap_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
  <defs>
    <style>
      .card {{ fill: #1f2937; stroke: #a78bfa; stroke-width: 2; }}
      .title {{ font-family: 'Courier New', monospace; font-size: 15px; font-weight: bold; fill: #a78bfa; }}
      .axis {{ font-family: 'Courier New', monospace; font-size: 9px; fill: #9ca3af; }}
    </style>
  </defs>

  <rect class="card" x="5" y="5" width="{svg_w - 10}" height="{svg_h - 10}" rx="8"/>
  <text class="title" x="{GRID_X}" y="34">{total_contrib} contributions in the last year</text>

{newline.join(month_labels)}
{newline.join(cells)}

  <text class="axis" x="{legend_x}" y="{legend_y}">Less</text>
{legend_cells}
  <text class="axis" x="{legend_x + 36 + 5 * STEP}" y="{legend_y}">More</text>
</svg>"""

with open(f"{STATS_DIR}/contribution-graph.svg", "w", encoding="utf-8") as f:
    f.write(heatmap_svg)

print(f"[OK] Generated contribution graph: {STATS_DIR}/contribution-graph.svg")
