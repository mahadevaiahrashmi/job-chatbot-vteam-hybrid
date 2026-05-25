"""DB worker — invoked as a subprocess by the orchestrator.

Usage::

    python db_worker.py --csv output/jobs.csv --db output/jobs.db < postings.json

* Reads a JSON array of postings from stdin (one dict per posting,
  matching :data:`job_chatbot.tools.storage.CSV_HEADERS`).
* Writes the CSV to ``--csv`` and upserts rows into the SQLite DB at ``--db``.
* Emits a JSON summary on stdout: ``{"csv": ..., "db": ..., "rows": N}``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python src/python/job_chatbot/workers/db_worker.py` (no install)
# by extending sys.path to the package root.
_THIS_FILE = Path(__file__).resolve()
_PKG_ROOT = _THIS_FILE.parent.parent.parent  # .../src/python
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from job_chatbot.tools.storage import write_csv, write_sqlite  # noqa: E402


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Persist job postings to CSV + SQLite.")
    parser.add_argument("--csv", required=True, help="Path to write the CSV output.")
    parser.add_argument("--db", required=True, help="Path to the SQLite database.")
    parser.add_argument(
        "--input",
        default="-",
        help="Path to a JSON file with the postings array (default: stdin).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.input == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.input).read_text(encoding="utf-8")

    if not raw.strip():
        rows: list[dict] = []
    else:
        rows = json.loads(raw)
        if not isinstance(rows, list):
            print("Input must be a JSON array of postings.", file=sys.stderr)
            return 2

    csv_path = Path(args.csv)
    db_path = Path(args.db)
    csv_count = write_csv(rows, csv_path)
    db_count = write_sqlite(rows, db_path)

    summary = {
        "csv": str(csv_path),
        "db": str(db_path),
        "rows": csv_count,
        "db_rows": db_count,
    }
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
