#!/usr/bin/env python3
import os
import re
import requests

USERNAME = "HasanboyZafarov"
TOKEN = os.environ["GH_TOKEN"]
README = "README.md"

headers = {
    "Authorization": f"bearer {TOKEN}",
    "Content-Type": "application/json",
}

query = """
query {
  viewer {
    privateRepos: repositories(privacy: PRIVATE) { totalCount }
    publicRepos: repositories(privacy: PUBLIC) { totalCount }
  }
}
"""

resp = requests.post(
    "https://api.github.com/graphql",
    json={"query": query},
    headers=headers,
)
resp.raise_for_status()
data = resp.json()

if "errors" in data:
    print("GraphQL errors:", data["errors"])
    raise SystemExit(1)

viewer = data["data"]["viewer"]
private = viewer["privateRepos"]["totalCount"]
public = viewer["publicRepos"]["totalCount"]
total = public + private

line = f"📦 All Repos: {total}  |  🔒 Private: {private}  |  🌐 Public: {public}"
print(line)

with open(README, "r", encoding="utf-8") as f:
    content = f.read()

updated = re.sub(
    r"<!-- STATS:START -->.*?<!-- STATS:END -->",
    f"<!-- STATS:START -->\n{line}\n<!-- STATS:END -->",
    content,
    flags=re.DOTALL,
)

with open(README, "w", encoding="utf-8") as f:
    f.write(updated)

print("README updated.")
