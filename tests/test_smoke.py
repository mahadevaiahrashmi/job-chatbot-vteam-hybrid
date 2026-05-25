"""Smoke tests for the job chatbot. No live Anthropic or Workday calls."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from job_chatbot import __version__
from job_chatbot.agents.company_confirm import confirm_company
from job_chatbot.models import JobPosting
from job_chatbot.orchestrator import run_pipeline
from job_chatbot.tools.companies import known_companies, resolve_company
from job_chatbot.tools.storage import write_csv, write_sqlite
from job_chatbot.tools.workday import _extract_job_id
from job_chatbot.workers.tester_worker import validate_csv

_REPO_ROOT = Path(__file__).resolve().parent.parent
_PKG_DIR = _REPO_ROOT / "src" / "python" / "job_chatbot"


# ---------------------------------------------------------------------------
# Job-id regex (the contract this template must preserve)
# ---------------------------------------------------------------------------


def test_extract_job_id_strips_suffix():
    assert _extract_job_id("_712616WD-2") == "712616WD"


def test_extract_job_id_full_path():
    path = "/Global_Experienced_Careers/job/Bengaluru/IN-Senior-_712616WD"
    assert _extract_job_id(path) == "712616WD"


def test_extract_job_id_fallback():
    # No WD-suffixed id: fall back to last segment.
    assert _extract_job_id("/some/path/abc") == "abc"
    assert _extract_job_id("") == ""


# ---------------------------------------------------------------------------
# Company registry
# ---------------------------------------------------------------------------


def test_resolve_pwc_aliases():
    company = resolve_company("PwC")
    assert company is not None
    assert company.tenant == "pwc"
    assert company.site == "Global_Experienced_Careers"
    assert resolve_company("pricewaterhousecoopers").canonical_name == company.canonical_name


def test_known_companies_count():
    assert len(known_companies()) == 8


def test_confirm_company_unknown():
    confirmation = confirm_company("Acme Anvils")
    assert confirmation.company is None
    assert "Supported companies" in confirmation.notes


# ---------------------------------------------------------------------------
# Storage round-trip
# ---------------------------------------------------------------------------


_SAMPLE_ROWS = [
    {
        "company": "PricewaterhouseCoopers",
        "job_id": "712616WD",
        "title": "Senior AI Engineer",
        "location": "Bengaluru, India",
        "posted_on": "Posted 3 Days Ago",
        "url": "https://pwc.wd3.myworkdayjobs.com/job/Bengaluru/_712616WD",
    },
    {
        "company": "PricewaterhouseCoopers",
        "job_id": "712617WD",
        "title": "ML Researcher",
        "location": "London, UK",
        "posted_on": "Posted Yesterday",
        "url": "https://pwc.wd3.myworkdayjobs.com/job/London/_712617WD",
    },
]


def test_storage_round_trip(tmp_path: Path):
    csv_path = tmp_path / "jobs.csv"
    db_path = tmp_path / "jobs.db"

    n_csv = write_csv(_SAMPLE_ROWS, csv_path)
    n_db = write_sqlite(_SAMPLE_ROWS, db_path)
    assert n_csv == 2 and n_db == 2

    result = validate_csv(csv_path)
    assert result["ok"] is True
    assert result["rows"] == 2
    assert result["errors"] == []


def test_validate_csv_catches_dupes(tmp_path: Path):
    csv_path = tmp_path / "dupes.csv"
    dupes = _SAMPLE_ROWS + [_SAMPLE_ROWS[0]]
    write_csv(dupes, csv_path)
    result = validate_csv(csv_path)
    assert result["ok"] is False
    assert any("duplicate" in err for err in result["errors"])


# ---------------------------------------------------------------------------
# Pipeline (with the network scraper stubbed out)
# ---------------------------------------------------------------------------


def _fake_scraper(company, *, keywords="", location=None, limit=100):
    return [
        JobPosting(
            company=company.canonical_name,
            job_id="712616WD",
            title=f"AI Engineer ({keywords or 'any'})",
            location=location or "Remote",
            posted_on="Posted 3 Days Ago",
            url=f"{company.base_url}/job/_712616WD",
        ).to_dict()
    ]


def test_run_pipeline_with_stub_scraper(tmp_path: Path):
    result = run_pipeline(
        "pwc",
        keywords="AI",
        output_dir=tmp_path / "output",
        scraper=_fake_scraper,
    )
    assert result.company == "PricewaterhouseCoopers"
    assert len(result.postings) == 1
    assert result.validation["ok"] is True
    assert Path(result.csv_path).exists()
    assert Path(result.db_path).exists()


def test_run_pipeline_unknown_company(tmp_path: Path):
    result = run_pipeline(
        "Acme",
        output_dir=tmp_path / "output",
        scraper=_fake_scraper,
    )
    assert result.company is None
    assert result.validation["ok"] is False


# ---------------------------------------------------------------------------
# Subprocess workers (--help must work; full subprocess round-trip)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "worker",
    ["db_worker.py", "tester_worker.py"],
)
def test_worker_help(worker: str):
    proc = subprocess.run(
        [sys.executable, str(_PKG_DIR / "workers" / worker), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "usage" in proc.stdout.lower()


def test_subprocess_db_then_tester(tmp_path: Path):
    csv_path = tmp_path / "jobs.csv"
    db_path = tmp_path / "jobs.db"

    db_proc = subprocess.run(
        [
            sys.executable,
            str(_PKG_DIR / "workers" / "db_worker.py"),
            "--csv",
            str(csv_path),
            "--db",
            str(db_path),
        ],
        input=json.dumps(_SAMPLE_ROWS),
        text=True,
        capture_output=True,
        check=True,
    )
    summary = json.loads(db_proc.stdout)
    assert summary["rows"] == 2

    tester_proc = subprocess.run(
        [
            sys.executable,
            str(_PKG_DIR / "workers" / "tester_worker.py"),
            "--csv",
            str(csv_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    result = json.loads(tester_proc.stdout)
    assert result["ok"] is True
    assert result["rows"] == 2


def test_version_exposed():
    assert __version__ == "0.1.0"
