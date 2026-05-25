# Job-Search Chatbot — User Manual

A friendly walkthrough for people who just want to find jobs at one of the
supported companies. No prior knowledge of agents, Workday APIs, or
subprocesses required.

## What this tool does

This chatbot collects current job postings from a company's public Workday
careers site, filters them by keyword (and optionally by location), and
saves the matching postings to a CSV file on your computer along with a
small SQLite database. You can then open the CSV in Excel or Google Sheets
and decide which roles to apply to. There is no scraping of pages
themselves — the tool calls Workday's own public JSON search endpoint, the
same one that the company's careers website uses.

Note that this repository is layered on top of a methodology template
called `vteam-hybrid`. That means the repo also contains a number of files
that are unrelated to the chatbot — Claude Code agent personas under
`.claude/agents/`, slash commands under `.claude/commands/`, methodology
notes under `docs/methodology/` and `docs/process/`, and sample sprints
under `samples/`. Those come from the template and are kept verbatim. The
actual chatbot code lives under `src/python/job_chatbot/`. You can safely
ignore the template files if you only want to use the chatbot.

## What you need before starting

- **Python 3.11 or newer.** Check with `python3 --version`.
- **`uv`** — the Python package manager this project uses. Install from
  https://github.com/astral-sh/uv if you don't already have it.
- **An Anthropic API key** (only needed for `--chat` mode). The default
  pipeline mode runs without one. Get a key at
  https://console.anthropic.com.

## Installing for the first time

```bash
# 1. Clone the repo (skip if you already have it).
git clone <repo-url> job-chatbot-vteam-hybrid
cd job-chatbot-vteam-hybrid

# 2. Create a virtual environment and install the project.
uv venv
uv pip install -e ".[dev]"

# 3. (Optional) Set up your API key for chat mode.
cp .env.example .env
# Open .env in any editor and replace 'sk-ant-...' with your real key.
```

The install step also wires up a `job-chatbot` command on your PATH (inside
the venv), so you can use either invocation style shown below.

## Running the bot

The CLI has two modes.

**Pipeline mode (default — no LLM, just runs the four agents in order):**

```bash
uv run python -m job_chatbot.main PwC --keywords AI
uv run python -m job_chatbot.main "JPMorgan Chase" --keywords "machine learning" --location Bangalore --limit 25
```

**Chat mode (uses Claude to drive the tool calls — requires
`ANTHROPIC_API_KEY`):**

```bash
uv run python -m job_chatbot.main --chat PwC --keywords AI
uv run python -m job_chatbot.main --chat Salesforce --keywords "data engineer" --location London
```

Both modes share the same flags:

| Flag | Meaning | Default |
| ---- | ------- | ------- |
| `company` (positional) | A supported company name or alias. | — |
| `--keywords` | Free-text keywords (passed to Workday's search). | empty |
| `--location` | Substring filter applied to each posting's location. | none |
| `--limit` | Maximum postings to fetch. | 50 |
| `--output-dir` | Where to write the CSV + SQLite. | `output` |
| `--chat` | Use the Anthropic tool-use loop. | off |
| `--list-companies` | Print the supported companies and exit. | — |

## Example queries

```bash
# All AI roles at PwC.
uv run python -m job_chatbot.main PwC --keywords AI

# Data-engineering roles at Salesforce, capped at 20.
uv run python -m job_chatbot.main Salesforce --keywords "data engineer" --limit 20

# Machine-learning roles at JPMorgan in Bangalore.
uv run python -m job_chatbot.main "JPMorgan Chase" --keywords "machine learning" --location Bangalore

# Any open role at Netflix (no keyword filter).
uv run python -m job_chatbot.main Netflix

# NVIDIA GPU-software roles, written to a custom folder.
uv run python -m job_chatbot.main NVIDIA --keywords "GPU software" --output-dir ~/jobs

# Cisco security engineer roles in San Jose.
uv run python -m job_chatbot.main Cisco --keywords "security engineer" --location "San Jose"

# Chat mode — let Claude pick which tools to call.
uv run python -m job_chatbot.main --chat Adobe --keywords "design systems"

# Just list the companies the tool knows about.
uv run python -m job_chatbot.main --list-companies
```

## Where the results live

Every successful run produces two artifacts under `--output-dir`
(`output/` by default):

- `output/<tenant>_jobs.csv` — one row per posting, suitable for opening in
  Excel, Numbers, or Google Sheets.
- `output/<tenant>_jobs.db` — a SQLite database with a single `jobs`
  table (handy if you want to query across multiple runs).

For example, running `... PwC --keywords AI` produces
`output/pwc_jobs.csv` and `output/pwc_jobs.db`. Re-running with different
keywords overwrites the CSV but **upserts** into the SQLite DB, so the
database accumulates everything you've ever scraped.

## Reading the CSV

The CSV always has six columns:

| Column | What it means |
| ------ | ------------- |
| `company` | Canonical company name (e.g. `PricewaterhouseCoopers`). |
| `job_id` | Workday's internal posting ID (e.g. `712616WD`). Duplicates across regional sites are de-duped. |
| `title` | Job title as posted. |
| `location` | Workday's `locationsText` field (often a city + country). |
| `posted_on` | Free-text "Posted N days ago" string from Workday. |
| `url` | Direct link to the posting on the company's careers site. |

## Supported companies

Eight companies are supported out of the box:

1. **PwC** (PricewaterhouseCoopers) — aliases: `pwc`, `pricewaterhousecoopers`, `pwc india`
2. **JPMorgan Chase** — aliases: `jpmorgan`, `jpmc`, `chase`, `jp morgan`
3. **Salesforce** — alias: `sfdc`
4. **Cisco**
5. **Adobe**
6. **NVIDIA**
7. **Netflix**
8. **Workday**

To see the canonical names: `uv run python -m job_chatbot.main --list-companies`.

## Common questions / troubleshooting

**Q: I get `ANTHROPIC_API_KEY is not set`.**
You're running with `--chat`. Either drop the flag (the default pipeline
mode doesn't need a key) or put your key into `.env`.

**Q: I get `Unknown company 'Foo'`.**
Only the eight companies above are wired up. To add a new one, edit
`src/python/job_chatbot/tools/companies.py`. Each entry needs a Workday
`base_url`, `tenant`, and `site`.

**Q: The run returns zero postings even though the careers page has jobs.**
Most likely the company changed its Workday site name (the part after the
tenant in the URL). Open the company's careers site, find a URL like
`https://acme.wd5.myworkdayjobs.com/Careers/...`, and update the `site`
field in `tools/companies.py`.

**Q: What's all the stuff under `.claude/`, `docs/`, `samples/`, and
`scripts/`? Do I need to read it?**
No — those folders belong to the upstream `vteam-hybrid` template, not the
chatbot. They define Claude Code agent personas (`.claude/agents/`), slash
commands (`.claude/commands/`), methodology guides (`docs/methodology/`,
`docs/process/`), and example sprints (`samples/`). The chatbot's own
documentation is `README-AGENTS.md`, `docs/USER-MANUAL.md` (this file),
and `docs/SYSTEM-DESIGN.md`. The chatbot's code is all under
`src/python/job_chatbot/`.

**Q: Workday returned an HTTP 4xx/5xx and the run crashed.**
Re-run after a minute. If it persists, lower `--limit` (the tool paginates
in pages of 20 — fewer pages means fewer requests). The endpoint is
public but rate-limited at the discretion of each tenant.

**Q: I want to use the SQLite database from another tool.**
The schema is plain SQLite — open it with `sqlite3 output/<tenant>_jobs.db`,
DBeaver, or any other SQLite client. There is one table, `jobs`, with the
same columns as the CSV plus a primary key on `(company, job_id)`.

## Privacy & cost

- **Data is local.** The CSV and SQLite database live on your machine
  under `output/`. Nothing is uploaded anywhere.
- **Workday calls.** Each run makes a handful of unauthenticated POST
  requests to the company's public Workday endpoint. No tracking cookie,
  no login.
- **Anthropic API cost (only in `--chat` mode).** Each chat run uses
  roughly 2–6 tool-use rounds against Claude 3.5 Sonnet. Expect a few US
  cents per query at current pricing. The default (non-chat) pipeline
  mode never calls the Anthropic API and costs nothing beyond your
  electricity.
