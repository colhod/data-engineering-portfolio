"""
Extracts Sonarr's full history (grabs, imports, deletions) via pagination,
and writes it to a CSV file as a durable checkpoint before loading into Postgres.
"""

import csv
import os

import requests
from dotenv import load_dotenv

load_dotenv()

SONARR_URL = os.getenv("SONARR_URL")
SONARR_API_KEY = os.getenv("SONARR_API_KEY")

HEADERS = {"X-Api-Key": SONARR_API_KEY}
PAGE_SIZE = 100


def fetch_all_history():
    all_records = []
    page = 1

    while True:
        response = requests.get(
            f"{SONARR_URL}/api/v3/history",
            headers=HEADERS,
            params={"page": page, "pageSize": PAGE_SIZE, "sortKey": "date", "sortDirection": "descending"},
        )
        response.raise_for_status()
        data = response.json()

        all_records.extend(data["records"])
        print(f"  Fetched page {page} ({len(all_records)}/{data['totalRecords']} records so far)")

        if len(all_records) >= data["totalRecords"]:
            break
        page += 1

    return all_records


def flatten_record(record):
    return {
        "history_id": record["id"],
        "series_id": record.get("seriesId"),
        "episode_id": record.get("episodeId"),
        "event_type": record["eventType"],
        "date": record["date"],
        "source_title": record.get("sourceTitle"),
        "quality": record.get("quality", {}).get("quality", {}).get("name"),
        "size_bytes": record.get("data", {}).get("size"),
    }


def main():
    print("Fetching Sonarr history...")
    records = fetch_all_history()

    print(f"Done. Collected {len(records)} history events total.")

    rows = [flatten_record(r) for r in records]

    with open("sonarr_history.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to sonarr_history.csv")


if __name__ == "__main__":
    main()
