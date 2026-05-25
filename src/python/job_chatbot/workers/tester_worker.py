"""Tester worker — invoked as a subprocess by the orchestrator.

Usage::

    python tester_worker.py --csv output/jobs.csv

Validates that the CSV produced by the DB worker:

* Exists and is non-empty.
* Has the expected header row.
* Contains a non-blank ``job_id`` and ``url`` on every row.
* Has no duplicate ``(company, job_id)`` pairs.

Emits a JSON summary on stdout. Exits non-zero if any check fails.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# Allow direct execution without installing the package.
_THIS_FILE = Path(__file__).resolve()
_PKG_ROOT = _THIS_FILE.parent.parent.parent  # .../src/python
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from job_chatbot.tools.storage import CSV_HEADERS  # noqa: E402


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a job postings CSV produced by the DB worker."
    )
    parser.add_argument("--csv", required=True, help="Path to the CSV to validate.")
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Treat a CSV with only headers as a successful (empty) result.",
    )
    return parser.parse_args(argv)


def validate_csv(path: Path, allow_empty: bool = False) -> dict:
    """Validate a job postings CSV. Returns a result dict.

    The dict always has ``ok`` (bool), ``rows`` (int), and ``errors`` (list).
    """
    errors: list[str] = []
    if not path.exists():
        return {"ok": False, "rows": 0, "errors": [f"CSV does not exist: {path}"]}

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        if headers != CSV_HEADERS:
            errors.append(
                f"Unexpected headers. Got {headers!r}, expected {CSV_HEADERS!r}."
            )
        seen: set[tuple[str, str]] = set()
        rows = 0
        for idx, row in enumerate(reader, start=2):  # line 2 = first data row
            rows += 1
            if not (row.get("job_id") or "").strip():
                errors.append(f"row {idx}: empty job_id")
            if not (row.get("url") or "").strip():
                errors.append(f"row {idx}: empty url")
            key = ((row.get("company") or "").strip(), (row.get("job_id") or "").strip())
            if key in seen:
                errors.append(f"row {idx}: duplicate (company, job_id) {key}")
            seen.add(key)

    if rows == 0 and not allow_empty:
        errors.append("CSV has no data rows.")

    return {"ok": not errors, "rows": rows, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    result = validate_csv(Path(args.csv), allow_empty=args.allow_empty)
    print(json.dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
