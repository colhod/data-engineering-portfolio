"""
Step 1 test script: confirms we can authenticate against Navidrome's
Subsonic API before we try pulling any real library data.
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


def test_connection():
    params = build_auth_params()
    url = f"{NAVIDROME_URL}/rest/ping"

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    status = data["subsonic-response"]["status"]

    if status == "ok":
        print("Connected to Navidrome successfully!")
    else:
        print("Navidrome responded but reported an error:")
        print(data)


if __name__ == "__main__":
    test_connection()
