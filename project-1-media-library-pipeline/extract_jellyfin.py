"""
Full Jellyfin extraction. Pulls every Movie and Episode in one API
call (Jellyfin supports this directly, no nested loop needed like
Navidrome), and writes it all to a CSV checkpoint.
"""

import csv
import os

import requests
from dotenv import load_dotenv

load_dotenv()

JELLYFIN_URL = os.getenv("JELLYFIN_URL")
JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY")

HEADERS = {"X-Emby-Token": JELLYFIN_API_KEY}
OUTPUT_FILE = "jellyfin_items.csv"

FIELDS = [
    "id", "title", "type", "series_name", "year", "genres",
    "runtime_minutes", "file_size_bytes", "container",
]


def get_users():
    response = requests.get(f"{JELLYFIN_URL}/Users", headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_all_items(user_id):
    params = {
        "Recursive": "true",
        "IncludeItemTypes": "Movie,Episode",
        "Fields": "Genres,ProductionYear,RunTimeTicks,MediaSources,SeriesName",
    }

    response = requests.get(
        f"{JELLYFIN_URL}/Users/{user_id}/Items",
        headers=HEADERS,
        params=params,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("Items", [])


def shape_row(item):
    runtime_ticks = item.get("RunTimeTicks")
    runtime_minutes = round(runtime_ticks / 10_000_000 / 60, 1) if runtime_ticks else ""

    media_sources = item.get("MediaSources", [])
    file_size = media_sources[0].get("Size") if media_sources else ""
    container = media_sources[0].get("Container") if media_sources else ""

    genres = item.get("Genres", [])
    genres_str = ", ".join(genres) if genres else ""

    return {
        "id": item.get("Id"),
        "title": item.get("Name"),
        "type": item.get("Type"),
        "series_name": item.get("SeriesName", ""),
        "year": item.get("ProductionYear"),
        "genres": genres_str,
        "runtime_minutes": runtime_minutes,
        "file_size_bytes": file_size,
        "container": container,
    }


def extract_all():
    users = get_users()
    user_id = users[0]["Id"]
    print(f"Using user: {users[0]['Name']}")

    items = get_all_items(user_id)
    print(f"Found {len(items)} items. Shaping rows...")

    rows = [shape_row(item) for item in items]
    return rows


def write_csv(rows):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    rows = extract_all()
    write_csv(rows)
