#!/usr/bin/env python3
"""Generate GitHub commit stats SVG"""

import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict

USERNAME = "HasanboyZafarov"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
STATS_DIR = "stats"

os.makedirs(STATS_DIR, exist_ok=True)

headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Fetch all repos
repos_response = requests.get(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=all",
    headers=headers
)
repos = repos_response.json()

# Collect commit stats
total_commits = 0
commits_this_year = 0
commits_this_month = 0
day_counts = defaultdict(int)

now = datetime.now()
year_ago = now - timedelta(days=365)
month_ago = now - timedelta(days=30)

for repo in repos:
    try:
        commits_url = f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits?per_page=1&author={USERNAME}"
        commits_response = requests.get(commits_url, headers=headers)

        if commits_response.status_code == 200 and commits_response.json():
            # Get commit count from link header
            link_header = commits_response.headers.get('link', '')
            if 'last' in link_header:
                # Extract page number from last link
                import re
                match = re.search(r'page=(\d+)>; rel="last"', link_header)
                if match:
                    total_commits += int(match.group(1))

            # Get recent commits for this month/year stats
            recent_commits = requests.get(
                f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits?per_page=100&author={USERNAME}",
                headers=headers
            ).json()

            for commit in recent_commits:
                commit_date = datetime.fromisoformat(commit['commit']['author']['date'].replace('Z', '+00:00')).replace(tzinfo=None)

                if commit_date > month_ago:
                    commits_this_month += 1
                if commit_date > year_ago:
                    commits_this_year += 1

                day_name = commit_date.strftime('%A')
                day_counts[day_name] += 1

    except Exception as e:
        pass

# Find most active day
most_active_day = max(day_counts, key=day_counts.get) if day_counts else "Monday"
most_active_commits = day_counts.get(most_active_day, 0)

# Generate SVG
svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="280" viewBox="0 0 500 280">
  <defs>
    <style>
      .stat-box {{ fill: #1f2937; stroke: #a78bfa; stroke-width: 2; }}
      .stat-label {{ font-family: 'Courier New', monospace; font-size: 11px; fill: #a78bfa; }}
      .stat-value {{ font-family: 'Courier New', monospace; font-size: 28px; font-weight: bold; fill: #fff; }}
      .title {{ font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; fill: #a78bfa; }}
      .subtitle {{ font-family: 'Courier New', monospace; font-size: 10px; fill: #999; }}
    </style>
  </defs>

  <rect class="stat-box" x="10" y="10" width="480" height="260" rx="8"/>

  <text class="title" x="20" y="35">Commit Stats — {USERNAME}</text>

  <text class="stat-label" x="30" y="75">Total Commits</text>
  <text class="stat-value" x="30" y="105">{total_commits}</text>

  <text class="stat-label" x="180" y="75">This Year</text>
  <text class="stat-value" x="180" y="105">{commits_this_year}</text>

  <text class="stat-label" x="330" y="75">This Month</text>
  <text class="stat-value" x="330" y="105">{commits_this_month}</text>

  <text class="stat-label" x="30" y="155">Most Active Day</text>
  <text class="stat-value" x="30" y="185">{most_active_day}</text>

  <text class="stat-label" x="280" y="155">Commits on {most_active_day[:3]}</text>
  <text class="stat-value" x="280" y="185">{most_active_commits}</text>

  <text class="subtitle" x="20" y="260">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</text>
</svg>"""

with open(f"{STATS_DIR}/github-stats.svg", "w") as f:
    f.write(svg_content)

print(f"[OK] Generated commit stats: {STATS_DIR}/github-stats.svg")
print(f"   Total Commits: {total_commits}")
print(f"   Commits This Year: {commits_this_year}")
print(f"   Commits This Month: {commits_this_month}")
print(f"   Most Active Day: {most_active_day} ({most_active_commits} commits)")
