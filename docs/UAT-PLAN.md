# UAT Plan — job-chatbot (vteam-hybrid)

User Acceptance Testing plan for the **vteam-hybrid** implementation of the
job-search chatbot. Aimed at product / non-engineer reviewers who need to
confirm the system behaves correctly before sign-off.

---

## 1. What UAT covers

This UAT validates the **chatbot code under `src/python/job_chatbot/`**
end-to-end:

- the in-process **CompanyConfirm** agent (normalizes raw company input),
- the in-process **Scraper** agent (calls the Workday public API),
- the subprocess **DB worker** (`workers/db_worker.py`, writes CSV + SQLite),
- the subprocess **Tester worker** (`workers/tester_worker.py`, validates CSV),
- the **Anthropic-SDK orchestrator** that ties them together,
- the **CLI entry point** (`python -m job_chatbot.main`).

### Out of scope

This repo also contains the upstream `noodlefrenzy/vteam-hybrid` template
material:

- agent personas in `.claude/`
- methodology, process, and template docs in `docs/methodology/`,
  `docs/process/`, `docs/scaffolds/`, `docs/research/`

**UAT does not cover that template content.** It is reference material, not
shipped software.

---

## 2. Prerequisites

| Item | Required version / notes |
|------|--------------------------|
| Operating system | macOS or Linux. Windows via WSL2. |
| Python | 3.11 or newer (the package declares `requires-python = ">=3.11"`). |
| `uv` | Latest. Install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Network | Outbound HTTPS to `*.myworkdayjobs.com` (real scrape) and `api.anthropic.com` (only for `--chat`). |
| Anthropic API key | Only needed for the `--chat` flag. The default deterministic pipeline does NOT require it. |
| Disk | < 50 MB for venv + outputs. |
| Time budget | One end-to-end run takes 10–25 seconds (see Section 6). |

---

## 3. Setup checklist

Step through these in order. Each box should be tickable before you start
running scenarios.

- [ ] **Clone the repo**

  ```bash
  git clone https://github.com/mahadevaiahrashmi/job-chatbot-vteam-hybrid.git
  cd job-chatbot-vteam-hybrid
  ```

- [ ] **Create the virtual environment**

  ```bash
  uv venv
  ```

- [ ] **Install the package with dev extras**

  ```bash
  uv pip install -e ".[dev]"
  ```

- [ ] **Copy and fill the `.env` file** (only required if you plan to
      exercise `--chat`)

  ```bash
  cp .env.example .env
  # then edit .env and paste in your ANTHROPIC_API_KEY
  ```

- [ ] **Run the smoke tests** — all 14 should pass

  ```bash
  uv run pytest -q
  ```

- [ ] **Smoke-run the CLI** against a real company

  ```bash
  uv run python -m job_chatbot.main PwC --keywords AI
  ```

  Optional: try the chat-mode orchestrator (requires the API key)

  ```bash
  uv run python -m job_chatbot.main PwC --keywords AI --chat
  ```

If all six boxes tick, you are ready to execute the acceptance scenarios.

---

## 4. Acceptance test scenarios

Run each scenario fresh (delete `output/` between runs if you want a clean
starting state). Record the result in the right-hand column.

| ID | Scenario | Steps | Expected result | Pass / Fail |
|----|----------|-------|-----------------|-------------|
| UAT-001 | List supported companies | `uv run python -m job_chatbot.main --list-companies` | Prints exactly 8 canonical company names (Adobe, Cisco, JPMorgan Chase, NVIDIA, Netflix, PricewaterhouseCoopers, Salesforce, Workday). Exit 0. | |
| UAT-002 | Resolve known company | `uv run python -m job_chatbot.main PwC --keywords AI` | A Rich table prints up to 20 PwC postings; "CSV:" and "DB:" lines name files under `output/`. Exit 0. | |
| UAT-003 | Resolve via alias | `uv run python -m job_chatbot.main "JP Morgan"` | Resolves to "JPMorgan Chase"; table prints. Exit 0. | |
| UAT-004 | Unknown company is rejected cleanly | `uv run python -m job_chatbot.main "Acme Anvils"` | Prints a red error mentioning supported companies. Exit 1. No files written. | |
| UAT-005 | Keyword filter is applied | `uv run python -m job_chatbot.main NVIDIA --keywords "machine learning"` | All printed titles plausibly relate to the keyword; CSV exists. | |
| UAT-006 | Location filter is applied | `uv run python -m job_chatbot.main Salesforce --location India` | Every "Location" cell printed in the table contains "India" (case-insensitive). | |
| UAT-007 | Output artifacts are written | After UAT-002: `ls output/pwc_jobs.csv output/pwc_jobs.db` | Both files exist and are non-empty. CSV opens in a spreadsheet and has the header `company,job_id,title,location,posted_on,url`. | |
| UAT-008 | Validation surfaces in CLI | After UAT-002 | Last line of output reads `Validation: ok=True rows=N` with N > 0. | |
| UAT-009 | Chat mode round-trip (API key required) | `uv run python -m job_chatbot.main PwC --keywords AI --chat` | A natural-language summary is printed. No Python traceback. Exit 0. | |
| UAT-010 | Chat mode without API key fails politely | Unset `ANTHROPIC_API_KEY`, run as above with `--chat` | Red message: `ANTHROPIC_API_KEY is not set.` Exit 2. | |
| UAT-011 | **Hybrid IPC works** — orchestrator spawns subprocess workers and cleans them up | Run UAT-002, then `ps aux \| grep db_worker \| grep -v grep` and the same for `tester_worker`. | Both `ps` greps return **no rows**. There are no hung Python subprocesses left over from the run. | |
| UAT-012 | **Worker crash isolation** — a worker failure does not corrupt in-process state | Temporarily make `workers/db_worker.py` unrunnable (e.g. `chmod -x` or rename), run UAT-002. Restore afterwards. | Run exits non-zero. The error surfaces to the CLI (Rich-formatted, not a hard crash with raw traceback hiding the failure). CompanyConfirm and Scraper output still appears in logs / the agents themselves did not hang. | |
| UAT-013 | **Worker CLI contracts** — both workers expose `--help` | `uv run python src/python/job_chatbot/workers/db_worker.py --help` and the same for `tester_worker.py` | Each prints a `usage:` line + the documented `--csv` / `--db` / `--allow-empty` flags. Exit 0. No traceback. | |

---

## 5. Negative tests

These exercise edge cases. They should all fail gracefully — never crash
with an unhandled exception.

| ID | Input | Expected behavior |
|----|-------|-------------------|
| NEG-01 | No company argument and no `--list-companies` | Argparse help is printed; exit 2. |
| NEG-02 | Empty company string: `uv run python -m job_chatbot.main ""` | Treated as unknown; red error; exit 1. |
| NEG-03 | Mixed-case alias: `"pRiCeWaTeRhOuSeCoOpErS"` | Resolves to PwC successfully (case-insensitive lookup). |
| NEG-04 | Network down during scrape | An `httpx` error message is printed; exit non-zero. The CSV is **not** written (or is empty and validation flags it). |
| NEG-05 | `--limit 0` | Run completes; validation reports `rows=0`. With current logic this is treated as a validation failure unless `--allow-empty` is plumbed through. Document the actual behavior you observe. |
| NEG-06 | Malformed JSON piped into `db_worker.py` directly | Worker exits non-zero with a JSON-decoding message on stderr. |
| NEG-07 | Run `tester_worker.py --csv /does/not/exist.csv` | Stdout JSON has `"ok": false`, `errors` mentions "CSV does not exist". Exit non-zero. |

---

## 6. Performance expectations

The pipeline is dominated by the Workday HTTP round-trip. Local processing
is negligible.

| Phase | Typical cost |
|-------|--------------|
| CompanyConfirm (in-process) | < 5 ms |
| Workday HTTP fetch (paginated, 20/page) | 1–3 s per page; usually 1–3 pages |
| DB worker subprocess spawn (warm cache) | ~50–100 ms |
| Tester worker subprocess spawn (warm cache) | ~50–100 ms |
| CSV + SQLite write | < 50 ms for typical result sizes |
| **Total end-to-end run** | **10–25 seconds** for `--limit 50` |

Two specific guarantees to verify:

- **Subprocess overhead is small.** The two subprocess hops together add
  only ~100–200 ms — they should not be the bottleneck.
- **No process leakage.** See UAT-011: after the run completes, `ps`
  shows zero `db_worker.py` or `tester_worker.py` processes.

If a run takes more than 60 seconds, capture the output and flag it as
a possible regression.

---

## 7. Sign-off template

Copy this block into the UAT ticket / sign-off email and fill it in.

```
UAT cycle:        ____________________________
Tester:           ____________________________
Date:             ____________________________
Repo SHA tested:  ____________________________
Python version:   ____________________________
OS:               ____________________________

Pytest result (uv run pytest -q):     ____ passed / ____ failed
Scenarios passed (UAT-001 .. UAT-013): __ / 13
Negative tests passed (NEG-01 .. NEG-07): __ / 7

Blocking issues filed (link IDs): __________________________

Sign-off:
[ ] Approved for release
[ ] Approved with caveats (list below)
[ ] Rejected

Caveats / notes:
________________________________________________________________
________________________________________________________________

Signed:           ____________________________
```

---

## 8. Reporting bugs

When a scenario fails, file an issue with the following:

1. **Scenario ID** (e.g. `UAT-011`) and one-line description.
2. **Exact command** you ran.
3. **Expected vs actual** output. Paste the full terminal output in a
   fenced code block.
4. **Environment**: OS, Python version (`python --version`), `uv`
   version (`uv --version`), repo commit SHA (`git rev-parse HEAD`).
5. **Side artifacts**: contents of `output/` if relevant — but redact
   anything sensitive first.
6. **For UAT-011 (subprocess leakage)**: paste the output of
   `ps aux | grep -E 'db_worker|tester_worker' | grep -v grep`.
7. **For UAT-012 (worker crash)**: include the full traceback or
   Rich-rendered error message and confirm whether the process exited
   or hung.
8. Tag the issue `uat` and assign it to the chatbot maintainer.

Bugs found in template content (`.claude/`, `docs/methodology/`, etc.)
are **out of scope for this UAT** — file them upstream against
`noodlefrenzy/vteam-hybrid` instead.
