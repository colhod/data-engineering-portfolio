"""
Test script: confirms we can authenticate against Jellyfin's API
before we try pulling any real library data.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

JELLYFIN_URL = os.getenv("JELLYFIN_URL")
JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY")


def test_connection():
    headers = {"X-Emby-Token": JELLYFIN_API_KEY}
    url = f"{JELLYFIN_URL}/System/Info"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    print("Connected to Jellyfin successfully!")
    print(f"  Server name: {data.get('ServerName')}")
    print(f"  Version: {data.get('Version')}")


if __name__ == "__main__":
    test_connection()
