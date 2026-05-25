"""CLI entry point for the job chatbot.

Two modes:

* Default (no ``ANTHROPIC_API_KEY``): runs the deterministic pipeline.
* ``--chat``: runs the Anthropic tool-use loop (requires the API key).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .orchestrator import run_chat, run_pipeline
from .tools.companies import known_companies


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-chatbot",
        description="Multi-agent job-search chatbot (vteam-hybrid).",
    )
    parser.add_argument("company", nargs="?", help="Company name (e.g. 'PwC').")
    parser.add_argument("--keywords", default="", help="Search keywords (e.g. 'AI').")
    parser.add_argument("--location", default=None, help="Location filter substring.")
    parser.add_argument("--limit", type=int, default=50, help="Max postings to fetch.")
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for CSV + SQLite artifacts.",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Use the Anthropic tool-use loop instead of the deterministic pipeline.",
    )
    parser.add_argument(
        "--list-companies",
        action="store_true",
        help="Print the list of supported companies and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = _build_parser()
    args = parser.parse_args(argv)
    console = Console()

    if args.list_companies:
        for name in known_companies():
            console.print(f"- {name}")
        return 0

    if args.chat:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            console.print("[red]ANTHROPIC_API_KEY is not set.[/red]")
            return 2
        if not args.company:
            console.print("[red]Provide a company (or a natural-language request).[/red]")
            return 2
        user_msg = (
            f"Get all jobs from {args.company} related to "
            f"{args.keywords or 'any role'}"
            + (f" in {args.location}" if args.location else "")
            + "."
        )
        reply = run_chat(user_msg)
        console.print(reply)
        return 0

    if not args.company:
        parser.print_help()
        return 2

    result = run_pipeline(
        args.company,
        keywords=args.keywords,
        location=args.location,
        limit=args.limit,
        output_dir=Path(args.output_dir),
    )
    if not result.company:
        console.print(f"[red]{result.validation['errors'][0]}[/red]")
        return 1

    table = Table(title=f"{result.company} — {len(result.postings)} postings")
    table.add_column("Job ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Location", style="green")
    for posting in result.postings[:20]:
        table.add_row(posting["job_id"], posting["title"], posting["location"])
    console.print(table)
    console.print(
        f"CSV: [bold]{result.csv_path}[/bold]  DB: [bold]{result.db_path}[/bold]"
    )
    console.print(
        f"Validation: ok=[bold]{result.validation['ok']}[/bold] "
        f"rows={result.validation['rows']}"
    )
    return 0 if result.validation["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
