"""Scraper agent — runs in-process.

Thin wrapper around :func:`job_chatbot.tools.workday.search_jobs` that
returns plain dictionaries suitable for JSON serialization (so the
orchestrator can pipe them straight into the subprocess workers).
"""

from __future__ import annotations

from ..models import JobPosting
from ..tools.companies import Company
from ..tools.workday import search_jobs


def scrape_jobs(
    company: Company,
    keywords: str = "",
    location: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Run a Workday search and return JSON-friendly dicts."""
    postings: list[JobPosting] = search_jobs(
        company, keywords=keywords, location=location, limit=limit
    )
    return [p.to_dict() for p in postings]
