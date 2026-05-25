"""Top-level Anthropic-SDK orchestrator (hybrid in-process + subprocess).

The orchestrator runs an Anthropic ``messages`` loop with four tools:

* ``confirm_company``  (in-process)  — wraps the CompanyConfirm agent.
* ``scrape_jobs``      (in-process)  — wraps the Scraper agent.
* ``persist_jobs``     (subprocess)  — shells out to ``workers/db_worker.py``.
* ``validate_csv``     (subprocess)  — shells out to ``workers/tester_worker.py``.

This deliberately mixes in-process tools with subprocess workers — that's
the "hybrid" pattern: cheap tools stay in-process; tools that benefit from
process isolation (e.g. distinct deps, sandboxing, or eventual remote
execution) ship out via ``subprocess``.

Tests never invoke the Anthropic API. ``run_pipeline`` provides a
deterministic, side-effect-only path used by the smoke tests.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .agents.company_confirm import confirm_company
from .agents.scraper import scrape_jobs
from .tools.companies import known_companies, resolve_company

# Paths to the subprocess workers — resolved relative to this file so the
# orchestrator can shell out without depending on cwd.
_PKG_DIR = Path(__file__).resolve().parent
_DB_WORKER = _PKG_DIR / "workers" / "db_worker.py"
_TESTER_WORKER = _PKG_DIR / "workers" / "tester_worker.py"


TOOLS: list[dict[str, Any]] = [
    {
        "name": "confirm_company",
        "description": (
            "Normalize a user-supplied company name against the supported "
            "company registry. Always call this first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Raw company name."},
            },
            "required": ["name"],
        },
    },
    {
        "name": "scrape_jobs",
        "description": (
            "Scrape Workday postings for a confirmed company. Returns a list "
            "of JSON-serializable job posting dicts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "company": {"type": "string", "description": "Canonical company name."},
                "keywords": {"type": "string", "default": ""},
                "location": {"type": "string"},
                "limit": {"type": "integer", "default": 100},
            },
            "required": ["company"],
        },
    },
    {
        "name": "persist_jobs",
        "description": (
            "Persist scraped postings to a CSV and SQLite DB. Runs as a "
            "subprocess (db_worker.py)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "postings": {"type": "array", "items": {"type": "object"}},
                "csv_path": {"type": "string"},
                "db_path": {"type": "string"},
            },
            "required": ["postings", "csv_path", "db_path"],
        },
    },
    {
        "name": "validate_csv",
        "description": (
            "Validate a CSV produced by persist_jobs. Runs as a subprocess "
            "(tester_worker.py)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "csv_path": {"type": "string"},
                "allow_empty": {"type": "boolean", "default": False},
            },
            "required": ["csv_path"],
        },
    },
]


@dataclass
class PipelineResult:
    company: str | None
    postings: list[dict]
    csv_path: str
    db_path: str
    validation: dict

    def summary(self) -> str:
        if not self.company:
            return "No company resolved."
        return (
            f"{self.company}: {len(self.postings)} postings -> "
            f"{self.csv_path} (validation ok={self.validation.get('ok')})"
        )


# ---------------------------------------------------------------------------
# Tool implementations (the Anthropic loop dispatches to these by name).
# ---------------------------------------------------------------------------


def _tool_confirm_company(name: str) -> dict:
    return confirm_company(name).to_dict()


def _tool_scrape_jobs(
    company: str,
    keywords: str = "",
    location: str | None = None,
    limit: int = 100,
) -> list[dict]:
    resolved = resolve_company(company)
    if not resolved:
        raise ValueError(
            f"Unknown company {company!r}. Supported: {', '.join(known_companies())}"
        )
    return scrape_jobs(resolved, keywords=keywords, location=location, limit=limit)


def _tool_persist_jobs(postings: list[dict], csv_path: str, db_path: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(_DB_WORKER), "--csv", csv_path, "--db", db_path],
        input=json.dumps(postings),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(proc.stdout.strip() or "{}")


def _tool_validate_csv(csv_path: str, allow_empty: bool = False) -> dict:
    cmd = [sys.executable, str(_TESTER_WORKER), "--csv", csv_path]
    if allow_empty:
        cmd.append("--allow-empty")
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    out = proc.stdout.strip() or "{}"
    return json.loads(out)


_TOOL_DISPATCH = {
    "confirm_company": lambda args: _tool_confirm_company(**args),
    "scrape_jobs": lambda args: _tool_scrape_jobs(**args),
    "persist_jobs": lambda args: _tool_persist_jobs(**args),
    "validate_csv": lambda args: _tool_validate_csv(**args),
}


def dispatch_tool(name: str, args: dict) -> Any:
    """Public entry point for the tool dispatch — used by the LLM loop and tests."""
    if name not in _TOOL_DISPATCH:
        raise KeyError(f"Unknown tool: {name}")
    return _TOOL_DISPATCH[name](args)


# ---------------------------------------------------------------------------
# Deterministic pipeline (no LLM calls). Used as the default in main.py and
# by the smoke tests.
# ---------------------------------------------------------------------------


def run_pipeline(
    raw_company: str,
    keywords: str = "",
    location: str | None = None,
    limit: int = 100,
    output_dir: Path | None = None,
    *,
    scraper=None,
) -> PipelineResult:
    """Run the full agent pipeline without invoking the LLM.

    Steps mirror the LLM tool-use loop, in order:

    1. CompanyConfirm (in-process)
    2. Scraper (in-process)
    3. DB worker (subprocess)
    4. Tester worker (subprocess)

    ``scraper`` can be injected for testing (defaults to the real
    Workday-calling scraper).
    """
    confirmation = confirm_company(raw_company)
    if not confirmation.company:
        return PipelineResult(
            company=None,
            postings=[],
            csv_path="",
            db_path="",
            validation={"ok": False, "rows": 0, "errors": [confirmation.notes]},
        )

    output_dir = output_dir or Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = confirmation.company.tenant
    csv_path = output_dir / f"{slug}_jobs.csv"
    db_path = output_dir / f"{slug}_jobs.db"

    if scraper is None:
        postings = scrape_jobs(
            confirmation.company,
            keywords=keywords,
            location=location,
            limit=limit,
        )
    else:
        postings = scraper(
            confirmation.company,
            keywords=keywords,
            location=location,
            limit=limit,
        )

    _tool_persist_jobs(postings, str(csv_path), str(db_path))
    validation = _tool_validate_csv(str(csv_path), allow_empty=True)

    return PipelineResult(
        company=confirmation.canonical_name,
        postings=postings,
        csv_path=str(csv_path),
        db_path=str(db_path),
        validation=validation,
    )


# ---------------------------------------------------------------------------
# Anthropic chat loop (only invoked from main.py when ANTHROPIC_API_KEY is set).
# ---------------------------------------------------------------------------


SYSTEM_PROMPT = (
    "You are the orchestrator for a multi-agent job-search chatbot. "
    "The user asks for jobs at a specific company; you must call the tools "
    "in this order: confirm_company, scrape_jobs, persist_jobs, validate_csv. "
    "Stop and summarize once validate_csv has run. Never invent job data."
)


def run_chat(user_message: str, *, model: str = "claude-3-5-sonnet-latest") -> str:
    """Run a single-turn tool-use loop against the Anthropic API.

    This is intentionally separated from ``run_pipeline`` so tests can
    exercise the agent wiring without touching the network or an API key.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")

    # Imported lazily so importing this module doesn't require the SDK.
    from anthropic import Anthropic  # type: ignore

    client = Anthropic(api_key=api_key)
    messages: list[dict] = [{"role": "user", "content": user_message}]

    for _ in range(8):  # hard cap on tool-use rounds
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        if response.stop_reason != "tool_use":
            return "".join(
                block.text for block in response.content if getattr(block, "type", "") == "text"
            )

        messages.append({"role": "assistant", "content": response.content})
        tool_results: list[dict] = []
        for block in response.content:
            if getattr(block, "type", "") != "tool_use":
                continue
            try:
                result = dispatch_tool(block.name, block.input or {})
                payload = json.dumps(result)
                is_error = False
            except Exception as exc:  # pragma: no cover - defensive
                payload = json.dumps({"error": str(exc)})
                is_error = True
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": payload,
                    "is_error": is_error,
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return "Reached tool-use round limit without final answer."
