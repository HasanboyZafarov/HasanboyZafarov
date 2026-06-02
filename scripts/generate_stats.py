#!/usr/bin/env python3
"""Generate GitHub stats SVG images"""

import os
import requests
from datetime import datetime

USERNAME = "HasanboyZafarov"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
STATS_DIR = "stats"

os.makedirs(STATS_DIR, exist_ok=True)

headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Fetch user data
user_response = requests.get(f"https://api.github.com/users/{USERNAME}", headers=headers)
user_data = user_response.json()

# Fetch repos
repos_response = requests.get(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=stars",
    headers=headers
)
repos = repos_response.json()

# Calculate stats
total_stars = sum(repo.get("stargazers_count", 0) for repo in repos if not repo.get("fork"))
public_repos = user_data.get("public_repos", 0)
followers = user_data.get("followers", 0)

# Generate SVG
svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">
  <defs>
    <style>
      .stat-box {{ fill: #1f2937; stroke: #a78bfa; stroke-width: 2; }}
      .stat-label {{ font-family: 'Courier New', monospace; font-size: 12px; fill: #a78bfa; }}
      .stat-value {{ font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; fill: #fff; }}
      .title {{ font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; fill: #a78bfa; }}
    </style>
  </defs>

  <rect class="stat-box" x="10" y="10" width="380" height="180" rx="8"/>

  <text class="title" x="20" y="35">GitHub Stats for {USERNAME}</text>

  <text class="stat-label" x="30" y="70">Public Repos</text>
  <text class="stat-value" x="30" y="95">{public_repos}</text>

  <text class="stat-label" x="140" y="70">Total Stars</text>
  <text class="stat-value" x="140" y="95">{total_stars}</text>

  <text class="stat-label" x="260" y="70">Followers</text>
  <text class="stat-value" x="260" y="95">{followers}</text>

  <text class="stat-label" x="20" y="160" font-size="10">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</text>
</svg>"""

with open(f"{STATS_DIR}/github-stats.svg", "w") as f:
    f.write(svg_content)

print(f"[OK] Generated stats: {STATS_DIR}/github-stats.svg")
print(f"   Public Repos: {public_repos}")
print(f"   Total Stars: {total_stars}")
print(f"   Followers: {followers}")
