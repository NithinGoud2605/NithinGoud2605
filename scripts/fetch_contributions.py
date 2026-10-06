#!/usr/bin/env python3
"""Fetch the last year of contributions from the GitHub GraphQL API into data/contributions.json.

Needs GITHUB_TOKEN (the Actions token works; locally use `gh auth token`).
Standard library only, so the daily workflow needs no pip install.
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USERNAME = os.getenv("GH_USERNAME") or "NithinGoud2605"

QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
    followers { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def graphql(token):
    body = json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    # Current streak: today may still be empty, so start counting from yesterday in that case.
    current = 0
    tail = days[:-1] if days and days[-1]["count"] == 0 else days
    for d in reversed(tail):
        if d["count"] == 0:
            break
        current += 1
    return current, longest


def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    user = graphql(token)
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [
        {"date": d["date"], "count": d["contributionCount"], "level": LEVELS[d["contributionLevel"]]}
        for w in cal["weeks"]
        for d in w["contributionDays"]
        if d["date"] <= date.today().isoformat()
    ]
    current, longest = streaks(days)
    data = {
        "username": USERNAME,
        "total": cal["totalContributions"],
        "current_streak": current,
        "longest_streak": longest,
        "public_repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "weeks": [[{"date": d["date"], "count": d["contributionCount"], "level": LEVELS[d["contributionLevel"]]}
                   for d in w["contributionDays"]] for w in cal["weeks"]],
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    out = ROOT / "data" / "contributions.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1))
    print(f"{USERNAME}: {data['total']} contributions, streak {current} (longest {longest})")


if __name__ == "__main__":
    main()
