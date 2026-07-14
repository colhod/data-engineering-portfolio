"""
Step 4: load the extracted CSV into Postgres.
This is a "raw" landing table - each run wipes it and reloads fresh
from the CSV, so it always mirrors the latest extraction exactly.
"""

import csv
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DW_HOST = os.getenv("DW_POSTGRES_HOST")
DW_PORT = os.getenv("DW_POSTGRES_PORT")
DW_DB = os.getenv("DW_POSTGRES_DB")
DW_USER = os.getenv("DW_POSTGRES_USER")
DW_PASSWORD = os.getenv("DW_POSTGRES_PASSWORD")

CSV_FILE = "navidrome_tracks.csv"
TABLE_NAME = "raw_navidrome_tracks"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id TEXT,
    title TEXT,
    artist TEXT,
    album TEXT,
    genre TEXT,
    year TEXT,
    duration TEXT,
    suffix TEXT,
    bitrate TEXT,
    track TEXT,
    album_id TEXT,
    artist_id TEXT
);
"""

INSERT_SQL = f"""
INSERT INTO {TABLE_NAME}
    (id, title, artist, album, genre, year, duration, suffix, bitrate, track, album_id, artist_id)
VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""


def read_csv_rows():
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_to_postgres(rows):
    conn = psycopg2.connect(
        host=DW_HOST,
        port=DW_PORT,
        dbname=DW_DB,
        user=DW_USER,
        password=DW_PASSWORD,
    )
    cur = conn.cursor()

    print("Creating table if it doesn't exist...")
    cur.execute(CREATE_TABLE_SQL)

    print(f"Wiping existing rows from {TABLE_NAME}...")
    cur.execute(f"TRUNCATE TABLE {TABLE_NAME};")

    print(f"Inserting {len(rows)} rows...")
    for row in rows:
        cur.execute(INSERT_SQL, (
            row["id"], row["title"], row["artist"], row["album"],
            row["genre"], row["year"], row["duration"], row["suffix"],
            row["bitRate"], row["track"], row["albumId"], row["artistId"],
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Done. {TABLE_NAME} now has {len(rows)} rows.")


if __name__ == "__main__":
    rows = read_csv_rows()
    load_to_postgres(rows)
