#!/usr/bin/env python3
"""Generate GitHub contribution stats SVG"""

import os
import requests
from datetime import datetime

USERNAME = "HasanboyZafarov"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN", "")
STATS_DIR = "stats"

if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN not set. API calls will be rate-limited.")
    print("Set GITHUB_TOKEN environment variable for authenticated requests.")

os.makedirs(STATS_DIR, exist_ok=True)

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
} if GITHUB_TOKEN else {
    "Accept": "application/vnd.github.v3+json"
}

# GraphQL query to get contribution stats
query = """
query {
  user(login: "%s") {
    name
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
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
  }
}
""" % USERNAME

if not GITHUB_TOKEN:
    print("Cannot fetch stats without GitHub token.")
    print("In GitHub Actions, token is automatic.")
    print("For local testing, set GITHUB_TOKEN environment variable.")
    exit(1)

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query},
    headers=headers
)

data = response.json()
if "errors" in data:
    print(f"GraphQL Error: {data['errors']}")
    exit(1)

if "data" not in data or data["data"] is None:
    print(f"API Error: {data}")
    exit(1)

user_data = data["data"]["user"]["contributionsCollection"]
calendar = user_data["contributionCalendar"]

total_contrib = calendar["totalContributions"]
commits = user_data["totalCommitContributions"]
prs = user_data["totalPullRequestContributions"]
issues = user_data["totalIssueContributions"]
reviews = user_data["totalPullRequestReviewContributions"]

# Find most active day
max_day = None
max_count = 0
for week in calendar["weeks"]:
    for day in week["contributionDays"]:
        if day["contributionCount"] > max_count:
            max_count = day["contributionCount"]
            max_day = day["date"]

most_active_date = max_day if max_day else "N/A"

# Generate SVG
svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="320" viewBox="0 0 500 320">
  <defs>
    <style>
      .stat-box {{ fill: #1f2937; stroke: #a78bfa; stroke-width: 2; }}
      .stat-label {{ font-family: 'Courier New', monospace; font-size: 10px; fill: #a78bfa; }}
      .stat-value {{ font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; fill: #fff; }}
      .title {{ font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; fill: #a78bfa; }}
      .subtitle {{ font-family: 'Courier New', monospace; font-size: 10px; fill: #999; }}
    </style>
  </defs>

  <rect class="stat-box" x="10" y="10" width="480" height="300" rx="8"/>

  <text class="title" x="20" y="35">GitHub Contributions for {USERNAME}</text>

  <text class="stat-label" x="30" y="70">Total Contributions (1y)</text>
  <text class="stat-value" x="30" y="95">{total_contrib}</text>

  <text class="stat-label" x="220" y="70">Commits</text>
  <text class="stat-value" x="220" y="95">{commits}</text>

  <text class="stat-label" x="30" y="135">Pull Requests</text>
  <text class="stat-value" x="30" y="160">{prs}</text>

  <text class="stat-label" x="160" y="135">Issues</text>
  <text class="stat-value" x="160" y="160">{issues}</text>

  <text class="stat-label" x="280" y="135">Code Reviews</text>
  <text class="stat-value" x="280" y="160">{reviews}</text>

  <text class="stat-label" x="30" y="205">Most Active Day</text>
  <text class="stat-value" x="30" y="230">{most_active_date}</text>

  <text class="stat-label" x="280" y="205">Max Streak</text>
  <text class="stat-value" x="280" y="230">{max_count} contrib</text>

  <text class="subtitle" x="20" y="300">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</text>
</svg>"""

with open(f"{STATS_DIR}/github-stats.svg", "w") as f:
    f.write(svg_content)

print(f"[OK] Generated contribution stats: {STATS_DIR}/github-stats.svg")
print(f"   Total Contributions (1y): {total_contrib}")
print(f"   Commits: {commits}")
print(f"   Pull Requests: {prs}")
print(f"   Issues: {issues}")
print(f"   Code Reviews: {reviews}")
print(f"   Most Active Day: {most_active_date} ({max_count} contributions)")
