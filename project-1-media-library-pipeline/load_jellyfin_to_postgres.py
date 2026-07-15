"""
Load the extracted Jellyfin CSV into Postgres.
Same pattern as the Navidrome load: a raw landing table that gets
wiped and reloaded fresh from the CSV each run.
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

CSV_FILE = "jellyfin_items.csv"
TABLE_NAME = "raw_jellyfin_items"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id TEXT,
    title TEXT,
    type TEXT,
    series_name TEXT,
    year TEXT,
    genres TEXT,
    runtime_minutes TEXT,
    file_size_bytes TEXT,
    container TEXT
);
"""

INSERT_SQL = f"""
INSERT INTO {TABLE_NAME}
    (id, title, type, series_name, year, genres, runtime_minutes, file_size_bytes, container)
VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s);
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
            row["id"], row["title"], row["type"], row["series_name"],
            row["year"], row["genres"], row["runtime_minutes"],
            row["file_size_bytes"], row["container"],
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Done. {TABLE_NAME} now has {len(rows)} rows.")


if __name__ == "__main__":
    rows = read_csv_rows()
    load_to_postgres(rows)

