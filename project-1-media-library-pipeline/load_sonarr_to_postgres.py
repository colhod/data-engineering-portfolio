"""
Loads the extracted Sonarr history CSV into Postgres.
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

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw_sonarr_history (
    history_id INTEGER,
    series_id INTEGER,
    episode_id INTEGER,
    event_type TEXT,
    date TIMESTAMP,
    source_title TEXT,
    quality TEXT,
    size_bytes TEXT
);
"""


def main():
    conn = psycopg2.connect(
        host=DW_HOST, port=DW_PORT, dbname=DW_DB, user=DW_USER, password=DW_PASSWORD
    )
    cur = conn.cursor()

    print("Creating table if it doesn't exist...")
    cur.execute(CREATE_TABLE_SQL)

    print("Wiping existing rows from raw_sonarr_history...")
    cur.execute("TRUNCATE TABLE raw_sonarr_history;")

    with open("sonarr_history.csv", "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Inserting {len(rows)} rows...")
    for row in rows:
        cur.execute(
            """
            INSERT INTO raw_sonarr_history
            (history_id, series_id, episode_id, event_type, date, source_title, quality, size_bytes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row["history_id"],
                row["series_id"],
                row["episode_id"],
                row["event_type"],
                row["date"],
                row["source_title"],
                row["quality"],
                row["size_bytes"],
            ),
        )

    conn.commit()
    print(f"Done. raw_sonarr_history now has {len(rows)} rows.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
