"""
Step 2: explore the shape of Navidrome's library data before writing
the full extraction. This pulls artists, then digs into just the
first couple of artists to see albums and songs, without looping
over everything yet.
"""

import hashlib
import os
import secrets

import requests
from dotenv import load_dotenv

load_dotenv()

NAVIDROME_URL = os.getenv("NAVIDROME_URL")
NAVIDROME_USER = os.getenv("NAVIDROME_USER")
NAVIDROME_PASSWORD = os.getenv("NAVIDROME_PASSWORD")


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


def explore():
    artists = get_all_artists()
    print(f"Found {len(artists)} artists total.\n")

    for artist in artists[:2]:
        artist_id = artist["id"]
        artist_name = artist["name"]
        print(f"--- Artist: {artist_name} (id={artist_id}) ---")

        artist_detail = call_subsonic("getArtist", {"id": artist_id})
        albums = artist_detail["artist"].get("album", [])
        print(f"  Has {len(albums)} album(s)")

        for album in albums[:1]:
            album_id = album["id"]
            album_name = album["name"]
            print(f"  --- Album: {album_name} (id={album_id}) ---")

            album_detail = call_subsonic("getAlbum", {"id": album_id})
            songs = album_detail["album"].get("song", [])
            print(f"    Has {len(songs)} song(s)")

            for song in songs[:2]:
                print(f"    Song: {song.get('title')}")
                print(f"      genre: {song.get('genre')}")
                print(f"      year: {song.get('year')}")
                print(f"      duration (sec): {song.get('duration')}")
                print(f"      suffix (format): {song.get('suffix')}")
                print(f"      bitRate: {song.get('bitRate')}")
        print()


if __name__ == "__main__":
    explore()
