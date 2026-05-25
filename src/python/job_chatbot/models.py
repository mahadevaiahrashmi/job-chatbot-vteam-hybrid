"""Data models for job postings and search queries."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class JobQuery:
    company: str
    keywords: str
    location: str | None = None
    limit: int = 100

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class JobPosting:
    company: str
    job_id: str
    title: str
    location: str
    posted_on: str
    url: str

    def to_dict(self) -> dict:
        return asdict(self)
