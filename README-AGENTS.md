# Job-Search Chatbot — Agent Appendix

This appendix layers a **multi-agent job-search chatbot** on top of the
upstream `vteam-hybrid` template. The original `README.md` is kept
verbatim; this file documents the additions in `src/python/job_chatbot/`.

> The user types something like
> `get all jobs from PwC related to AI`
> and the system runs four agents in sequence to scrape Workday, persist
> the postings, and validate the output.

## The hybrid orchestration pattern

`vteam-hybrid` emphasizes mixing modes of agent execution. This project
splits the four agents along that line:

```
                          job-chatbot orchestrator
                          (Anthropic SDK tool-use loop)
                                     |
        +----------------------------+----------------------------+
        |                            |                            |
   in-process                   in-process                    subprocess
   CompanyConfirm                Scraper                      DB worker
   (agents/company_confirm.py)   (agents/scraper.py)          (workers/db_worker.py)
                                                                   |
                                                              subprocess
                                                              Tester worker
                                                              (workers/tester_worker.py)
```

| Agent          | Mode        | Lives in                                          | Responsibility |
| -------------- | ----------- | ------------------------------------------------- | -------------- |
| CompanyConfirm | in-process  | `src/python/job_chatbot/agents/company_confirm.py` | Normalizes a raw company string to a registered tenant. |
| Scraper        | in-process  | `src/python/job_chatbot/agents/scraper.py`         | Calls Workday `/wday/cxs/{tenant}/{site}/jobs` with pagination. |
| DB             | subprocess  | `src/python/job_chatbot/workers/db_worker.py`      | Reads postings from stdin, writes CSV + SQLite. |
| Tester         | subprocess  | `src/python/job_chatbot/workers/tester_worker.py`  | Validates the CSV and exits non-zero on failure. |

The orchestrator (`orchestrator.py`) exposes all four as Anthropic tools
named `confirm_company`, `scrape_jobs`, `persist_jobs`, `validate_csv`.
Tools 1+2 dispatch to local Python functions; tools 3+4 shell out via
`subprocess.run([sys.executable, ...])`.

A deterministic `run_pipeline(...)` helper mirrors the LLM loop without
any network calls — that path is used by `--chat`-less CLI runs and by
the smoke tests.

## Quickstart

```bash
cd /Users/rashmi/Documents/job/job-chatbot-vteam-hybrid
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Deterministic mode (calls Workday, but no LLM):
job-chatbot PwC --keywords AI --limit 25

# LLM mode (requires .env with ANTHROPIC_API_KEY):
cp .env.example .env
# ...edit .env...
job-chatbot --chat "PwC" --keywords AI
```

CSV + SQLite artifacts land in `output/`.

## Example session

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

## Supported companies (8)

- Adobe
- Cisco
- JPMorgan Chase
- NVIDIA
- Netflix
- PricewaterhouseCoopers
- Salesforce
- Workday

Aliases: `pwc`, `jpmc`, `chase`, `jp morgan`, `sfdc`, etc. See
`src/python/job_chatbot/tools/companies.py`.

## Layout (additions only)

```
src/python/job_chatbot/
  __init__.py
  main.py                # CLI entry point (job-chatbot ...)
  orchestrator.py        # Anthropic tool-use loop + deterministic pipeline
  models.py
  agents/
    __init__.py
    company_confirm.py   # in-process
    scraper.py           # in-process
  workers/
    __init__.py
    db_worker.py         # subprocess worker (CSV + SQLite)
    tester_worker.py     # subprocess worker (CSV validation)
  tools/
    __init__.py
    workday.py           # POST /wday/cxs/{tenant}/{site}/jobs
    companies.py         # 8-company registry + aliases
    storage.py           # write_csv / write_sqlite helpers
tests/test_smoke.py      # No live network or LLM calls
pyproject.toml           # Python package metadata
.env.example
output/                  # gitignored
```

The original `vteam-hybrid` files (CLAUDE.md, .claude/, docs/, samples/,
scripts/, README.md, etc.) are unchanged.

## Tests

```bash
uv run pytest -q
```

Tests are fully offline — the scraper is stubbed and no Anthropic API
calls are made.

## Workday details

* Endpoint: `POST {base_url}/wday/cxs/{tenant}/{site}/jobs`
* Body: `{"appliedFacets":{}, "limit":20, "offset":0, "searchText":"..."}`
* Pagination: stop on empty page or when `offset >= total`.
* Job-id regex: `_([A-Z0-9-]+WD)(?:-\d+)?$` -> `_712616WD-2` becomes
  `712616WD`. This keeps duplicate listings from inflating counts.
