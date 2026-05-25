"""CSV + SQLite persistence helpers for job postings."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Iterable

CSV_HEADERS = ["company", "job_id", "title", "location", "posted_on", "url"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    company   TEXT NOT NULL,
    job_id    TEXT NOT NULL,
    title     TEXT NOT NULL,
    location  TEXT,
    posted_on TEXT,
    url       TEXT,
    PRIMARY KEY (company, job_id)
);
"""


def write_csv(rows: Iterable[dict], path: Path) -> int:
    """Write ``rows`` to ``path`` as CSV. Returns the number of rows written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in CSV_HEADERS})
            count += 1
    return count


def write_sqlite(rows: Iterable[dict], path: Path) -> int:
    """Upsert ``rows`` into ``path`` (SQLite). Returns the number of rows touched."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.executescript(_SCHEMA)
        cur = conn.cursor()
        count = 0
        for row in rows:
            cur.execute(
                """
                INSERT INTO jobs (company, job_id, title, location, posted_on, url)
                VALUES (:company, :job_id, :title, :location, :posted_on, :url)
                ON CONFLICT(company, job_id) DO UPDATE SET
                    title=excluded.title,
                    location=excluded.location,
                    posted_on=excluded.posted_on,
                    url=excluded.url
                """,
                {key: row.get(key, "") for key in CSV_HEADERS},
            )
            count += 1
        conn.commit()
        return count
    finally:
        conn.close()
