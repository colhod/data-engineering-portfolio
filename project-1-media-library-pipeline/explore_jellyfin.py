"""
Explore the shape of Jellyfin's library data before writing the
full extraction. Pulls a small batch of items to check the fields
look right.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

JELLYFIN_URL = os.getenv("JELLYFIN_URL")
JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY")

HEADERS = {"X-Emby-Token": JELLYFIN_API_KEY}


def get_users():
    """
    Jellyfin's /Items endpoint is scoped per-user, so we need a user ID
    first. This grabs the first available user (your admin account).
    """
    response = requests.get(f"{JELLYFIN_URL}/Users", headers=HEADERS)
    response.raise_for_status()
    return response.json()


def explore():
    users = get_users()
    print(f"Found {len(users)} user(s).")
    user_id = users[0]["Id"]
    print(f"Using user: {users[0]['Name']} (id={user_id})\n")

    params = {
        "Recursive": "true",
        "IncludeItemTypes": "Movie,Episode",
        "Fields": "Genres,ProductionYear,RunTimeTicks,MediaSources",
        "Limit": 5,
    }

    response = requests.get(
        f"{JELLYFIN_URL}/Users/{user_id}/Items",
        headers=HEADERS,
        params=params,
    )
    response.raise_for_status()
    data = response.json()

    items = data.get("Items", [])
    total = data.get("TotalRecordCount", 0)
    print(f"Total items available: {total}")
    print(f"Showing first {len(items)}:\n")

    for item in items:
        print(f"Title: {item.get('Name')}")
        print(f"  Type: {item.get('Type')}")
        print(f"  Year: {item.get('ProductionYear')}")
        print(f"  Genres: {item.get('Genres')}")
        runtime_ticks = item.get("RunTimeTicks")
        if runtime_ticks:
            runtime_minutes = runtime_ticks / 10_000_000 / 60
            print(f"  Runtime (min): {round(runtime_minutes, 1)}")
        media_sources = item.get("MediaSources", [])
        if media_sources:
            print(f"  File size (bytes): {media_sources[0].get('Size')}")
            print(f"  Container/format: {media_sources[0].get('Container')}")
        print()


if __name__ == "__main__":
    explore()
