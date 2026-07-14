"""
Step 3: full extraction. Loops through every artist -> every album,
collects every song's metadata, and writes it all to a CSV file as
a durable checkpoint before we load anything into Postgres.
"""

import csv
import hashlib
import os
import secrets

import requests
from dotenv import load_dotenv

load_dotenv()

NAVIDROME_URL = os.getenv("NAVIDROME_URL")
NAVIDROME_USER = os.getenv("NAVIDROME_USER")
NAVIDROME_PASSWORD = os.getenv("NAVIDROME_PASSWORD")

OUTPUT_FILE = "navidrome_tracks.csv"

FIELDS = [
    "id", "title", "artist", "album", "genre", "year",
    "duration", "suffix", "bitRate", "track", "albumId", "artistId",
]


def build_auth_params():
    salt = secrets.token_hex(6)
    token = hashlib.md5((NAVIDROME_PASSWORD + salt).encode("utf-8")).hexdigest()
    return {
        "u": NAVIDROME_USER,
        "t": token,
        "s": salt,
        "v": "1.16.1",
        "c": "portfolio-etl",
        "f": "json",
    }


def call_subsonic(endpoint, extra_params=None):
    params = build_auth_params()
    if extra_params:
        params.update(extra_params)

    url = f"{NAVIDROME_URL}/rest/{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["subsonic-response"]


def get_all_artists():
    data = call_subsonic("getArtists")
    indexes = data["artists"]["index"]

    all_artists = []
    for group in indexes:
        all_artists.extend(group["artist"])

    return all_artists


def extract_all_tracks():
    artists = get_all_artists()
    total_artists = len(artists)
    print(f"Found {total_artists} artists. Starting extraction...\n")

    all_tracks = []
    errors = []

    for i, artist in enumerate(artists, start=1):
        artist_id = artist["id"]
        artist_name = artist["name"]

        try:
            artist_detail = call_subsonic("getArtist", {"id": artist_id})
            albums = artist_detail["artist"].get("album", [])
        except Exception as e:
            print(f"  ERROR getting albums for artist '{artist_name}': {e}")
            errors.append(("artist", artist_name, str(e)))
            continue

        for album in albums:
            album_id = album["id"]
            album_name = album.get("name", "")

            try:
                album_detail = call_subsonic("getAlbum", {"id": album_id})
                songs = album_detail["album"].get("song", [])
            except Exception as e:
                print(f"  ERROR getting songs for album '{album_name}': {e}")
                errors.append(("album", album_name, str(e)))
                continue

            for song in songs:
                row = {field: song.get(field, "") for field in FIELDS}
                all_tracks.append(row)

        if i % 10 == 0 or i == total_artists:
            print(f"  Processed {i}/{total_artists} artists "
                  f"({len(all_tracks)} tracks collected so far)")

    print(f"\nDone. Collected {len(all_tracks)} tracks total.")
    if errors:
        print(f"{len(errors)} error(s) occurred during extraction:")
        for err_type, name, msg in errors:
            print(f"  [{err_type}] {name}: {msg}")

    return all_tracks


def write_csv(tracks):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(tracks)
    print(f"\nWrote {len(tracks)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    tracks = extract_all_tracks()
    write_csv(tracks)
