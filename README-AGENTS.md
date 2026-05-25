# Job-Search Chatbot — Agent Appendix

A multi-agent job-search chatbot layered on top of the `noodlefrenzy/vteam-hybrid`
methodology template. The template's files (`README.md`, `CLAUDE.md`,
`.claude/`, `docs/methodology/`, `samples/`, `scripts/`, etc.) are kept
verbatim. This README documents the chatbot code that lives under
`src/python/job_chatbot/`.

---

## For Non-Technical Users

The chatbot takes a company name and (optionally) some keywords, scrapes
the company's public Workday careers site, and saves matching job
postings to a CSV file plus a small SQLite database on your computer.

This is **separate from the template's methodology**. The Claude Code
agent personas under `.claude/agents/` and the slash commands under
`.claude/commands/` belong to `vteam-hybrid` itself — they have nothing
to do with the chatbot. You can use the chatbot without ever touching
them.

**Where to start:** read **[docs/USER-MANUAL.md](docs/USER-MANUAL.md)**
for a full walkthrough — installation, example queries, where the
results land, and troubleshooting.

**Prerequisites:** Python 3.11+, the [`uv`](https://github.com/astral-sh/uv)
package manager, and (optional, only for `--chat` mode) an Anthropic API
key.

### Example session

```
$ job-chatbot --chat "get all jobs from PwC related to AI"

I'll start by confirming the company name...
[tool] confirm_company({"name": "PwC"})
        -> PricewaterhouseCoopers (tenant=pwc, site=Global_Experienced_Careers)
[tool] scrape_jobs({"company":"PricewaterhouseCoopers","keywords":"AI","limit":50})
        -> 23 postings
[tool] persist_jobs({"postings":[...], "csv_path":"output/pwc_jobs.csv", ...})
        -> {"csv":"output/pwc_jobs.csv","db":"output/pwc_jobs.db","rows":23}
[tool] validate_csv({"csv_path":"output/pwc_jobs.csv"})
        -> {"ok":true, "rows":23, "errors":[]}

Found 23 AI-related postings at PricewaterhouseCoopers. Saved to
output/pwc_jobs.csv and output/pwc_jobs.db. Validation passed.
```

### Supported companies (8)

- Adobe
- Cisco
- JPMorgan Chase
- NVIDIA
- Netflix
- PricewaterhouseCoopers (PwC)
- Salesforce
- Workday

Aliases such as `pwc`, `jpmc`, `chase`, `jp morgan`, `sfdc` are also
accepted. See `src/python/job_chatbot/tools/companies.py`.

---

## For Developers

### Hybrid architecture in one paragraph

An Anthropic SDK orchestrator (`orchestrator.py`) exposes four tools to
Claude. Two of them — `confirm_company` and `scrape_jobs` — run
**in-process** as plain Python function calls (the agents share the
`Company` and `JobPosting` dataclasses, so passing data between them is
free). The other two — `persist_jobs` and `validate_csv` — run as
**subprocesses** via `subprocess.run([sys.executable, workers/<name>.py,
...])`, communicating with the orchestrator over stdin/stdout JSON and
exit codes. The same logic is also available as a deterministic
`run_pipeline(...)` helper that bypasses the LLM and is used by the
default CLI mode and the smoke tests.

| Agent          | Mode        | File | Responsibility |
| -------------- | ----------- | ---- | -------------- |
| CompanyConfirm | in-process  | `agents/company_confirm.py` | Normalize a company string to a registered tenant. |
| Scraper        | in-process  | `agents/scraper.py`         | Call Workday `/wday/cxs/{tenant}/{site}/jobs` with pagination. |
| DB             | subprocess  | `workers/db_worker.py`      | Read postings from stdin; write CSV + SQLite. |
| Tester         | subprocess  | `workers/tester_worker.py`  | Validate the CSV; exit non-zero on failure. |

**Full architecture, sequence diagrams, data flow, failure modes,
testing strategy, and extension points are in
[docs/SYSTEM-DESIGN.md](docs/SYSTEM-DESIGN.md).**

### Tech stack

- Python 3.11+
- [`anthropic`](https://pypi.org/project/anthropic/) SDK (tool-use loop)
- [`httpx`](https://pypi.org/project/httpx/) (Workday client)
- [`rich`](https://pypi.org/project/rich/) (terminal output)
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) (`.env` loading)
- [`pytest`](https://pypi.org/project/pytest/) (smoke tests, offline)
- Standard library: `argparse`, `csv`, `sqlite3`, `subprocess`, `json`, `re`

### Code layout

```
src/python/job_chatbot/
  __init__.py
  main.py                # CLI entry point (job-chatbot ...)
  orchestrator.py        # Anthropic tool-use loop + deterministic pipeline
  models.py              # JobQuery, JobPosting dataclasses
  agents/
    __init__.py
    company_confirm.py   # in-process
    scraper.py           # in-process
  workers/
    __init__.py
    db_worker.py         # subprocess (CSV + SQLite)
    tester_worker.py     # subprocess (CSV validation)
  tools/
    __init__.py
    workday.py           # POST /wday/cxs/{tenant}/{site}/jobs
    companies.py         # 8-company registry + aliases
    storage.py           # write_csv / write_sqlite helpers
tests/test_smoke.py      # 14 offline test cases
pyproject.toml
.env.example
output/                  # gitignored
```

### Quickstart

```bash
cd /Users/rashmi/Documents/job/job-chatbot-vteam-hybrid
uv venv
uv pip install -e ".[dev]"

# Deterministic mode (no LLM, hits Workday):
uv run python -m job_chatbot.main PwC --keywords AI --limit 25

# LLM mode (requires .env with ANTHROPIC_API_KEY):
cp .env.example .env
# ...edit .env...
uv run python -m job_chatbot.main --chat PwC --keywords AI
```

CSV + SQLite artifacts land in `output/`.

### Tests

```bash
uv run pytest -q
```

All tests run offline — neither Workday nor Anthropic is contacted. The
scraper is stubbed via a `scraper=` kwarg on `run_pipeline`, and the
Anthropic loop is not exercised at all.

### Workday details

* Endpoint: `POST {base_url}/wday/cxs/{tenant}/{site}/jobs`
* Body: `{"appliedFacets":{}, "limit":20, "offset":0, "searchText":"..."}`
* Pagination: stop on empty page or when `offset >= total`.
* Job-id regex: `_([A-Z0-9-]+WD)(?:-\d+)?$` -> `_712616WD-2` becomes
  `712616WD`. This keeps duplicate listings from inflating counts.

### Template relationship

The original `vteam-hybrid` files (`CLAUDE.md`, `.claude/`, `docs/`
methodology subfolders, `samples/`, `scripts/`, `README.md`, etc.) are
**unchanged**. This appendix and the two docs under `docs/USER-MANUAL.md`
and `docs/SYSTEM-DESIGN.md` are additive. Do not modify the template's
`README.md` — it documents the template itself.
