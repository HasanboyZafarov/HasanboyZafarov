#!/usr/bin/env python3
import os
import re
import requests

USERNAME = "HasanboyZafarov"
TOKEN = os.environ["GH_TOKEN"]
README = "README.md"

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

resp = requests.get("https://api.github.com/user", headers=headers)
resp.raise_for_status()
data = resp.json()

public = data["public_repos"]
private = data["total_private_repos"]
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
