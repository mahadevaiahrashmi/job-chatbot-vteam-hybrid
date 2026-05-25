# Testing Guide — job-chatbot (vteam-hybrid)

Developer-facing guide to the test suite for the **vteam-hybrid**
implementation. Covers what is tested today, how the in-process /
subprocess split shapes the tests, and how to add new tests, agents,
and workers without breaking the IPC contract.

---

## 1. Testing philosophy

Three rules drive every test in this repo:

1. **No live network, no live LLM.** The Workday HTTP layer is
   monkey-patched out and the Anthropic SDK's tool-use loop is bypassed
   in favor of `run_pipeline()`. A clean clone must pass `pytest` on a
   plane.
2. **Real subprocesses, synthetic data.** The whole point of the
   "hybrid" architecture is that some tools run out-of-process. Mocking
   the subprocess boundary would defeat the test. So we **do** run the
   real `db_worker.py` and `tester_worker.py` under `subprocess.run` —
   but only ever against synthetic, in-memory data.
3. **Tests must be fast and deterministic.** The full suite runs in
   well under five seconds and never flakes on CI runners that lack
   network egress.

---

## 2. What's covered today

All tests live in `tests/test_smoke.py`. There are **13 test functions**;
one is parametrized over two values, so pytest collects **14 cases**
total.

| # | Function | What it asserts |
|---|----------|-----------------|
| 1 | `test_extract_job_id_strips_suffix` | `_extract_job_id("_712616WD-2") == "712616WD"` — the `-N` suffix is stripped. |
| 2 | `test_extract_job_id_full_path` | A real Workday externalPath yields the canonical WD-suffixed id. |
| 3 | `test_extract_job_id_fallback` | When the path has no WD id, falls back to the last segment (and empty input -> empty string). |
| 4 | `test_resolve_pwc_aliases` | `"PwC"` resolves to tenant `pwc` / site `Global_Experienced_Careers`, and `"pricewaterhousecoopers"` resolves to the same canonical name. |
| 5 | `test_known_companies_count` | `known_companies()` returns exactly 8 entries. |
| 6 | `test_confirm_company_unknown` | Unknown name returns `company=None` and a `notes` string containing `"Supported companies"`. |
| 7 | `test_storage_round_trip` | Writes 2 sample rows to CSV + SQLite via `write_csv` / `write_sqlite`, then re-reads with `validate_csv` — expects `ok=True`, `rows=2`, no errors. |
| 8 | `test_validate_csv_catches_dupes` | A CSV with a duplicated `(company, job_id)` pair fails validation with a `"duplicate"` error. |
| 9 | `test_run_pipeline_with_stub_scraper` | Drives `run_pipeline("pwc", ..., scraper=_fake_scraper)` and asserts the result has company `"PricewaterhouseCoopers"`, one posting, validation `ok=True`, and the CSV + DB files exist on disk. |
| 10 | `test_run_pipeline_unknown_company` | `run_pipeline("Acme", ...)` returns `company=None` and `validation["ok"] is False`. |
| 11 | `test_worker_help` (parametrized over `db_worker.py`, `tester_worker.py`) | Each worker's `--help` exits 0 and stdout contains `"usage"`. Two pytest cases. |
| 12 | `test_subprocess_db_then_tester` | **The IPC contract test.** Real `subprocess.run` invokes `db_worker.py` with JSON on stdin, parses its stdout JSON (`rows == 2`), then real-`subprocess.run`s `tester_worker.py --csv …` against the file the DB worker just wrote and asserts `ok=True`, `rows=2`. |
| 13 | `test_version_exposed` | `job_chatbot.__version__ == "0.1.0"`. |

### Why test #12 matters

`test_subprocess_db_then_tester` is the **only test that exercises the
actual subprocess hop** the orchestrator depends on. It's intentional:

- Mocking subprocesses would hide breakage in the worker CLI contract
  (argparse changes, stdin/stdout format drift, exit-code regressions).
- A real round-trip is cheap — total cost is two cold Python interpreter
  starts, well under a second.
- It catches the class of bugs that the hybrid architecture is most
  prone to: a worker that "works when imported" but breaks when
  invoked as a script.

If you change anything about the worker CLI surface, run this test
first.

---

## 3. Test categories

The 13 functions sort into three categories:

| Category | Tests | Why grouped |
|----------|-------|-------------|
| **Unit** | 1, 2, 3 (regex), 4, 5, 6 (registry), 7, 8 (storage) | Pure functions; in-memory only. |
| **Integration** | 9, 10 (pipeline through CompanyConfirm + Scraper stub + real subprocess workers), 12 (worker subprocess round-trip) | Wire multiple components together. Tests 9, 10, 12 invoke real subprocesses. |
| **Contract** | 11 (worker `--help`), and the JSON-shape assertions in 12 | Lock down the public surface the orchestrator depends on: argparse args + stdout JSON shape + exit code. |

---

## 4. How to run tests

```bash
# Standard, quiet
uv run pytest -q

# Verbose with stdout from any subprocess workers that fail
uv run pytest -vv -s

# A single test
uv run pytest tests/test_smoke.py::test_subprocess_db_then_tester -vv

# Only the worker-contract tests
uv run pytest -q -k worker

# With coverage (after `uv pip install coverage`)
uv run coverage run -m pytest -q && uv run coverage report -m
```

`pyproject.toml` sets `pythonpath = ["src/python"]` so imports like
`from job_chatbot.tools.companies import …` work without an editable
install. The editable install is still recommended for IDE
auto-completion and for picking up the `job-chatbot` console script.

---

## 5. Mocking strategy

The codebase has two external dependencies — both are handled
deliberately, not generically.

### Workday HTTP (`tools/workday.py`)

The tests never call `search_jobs()` directly with a live network.
Instead, `test_run_pipeline_with_stub_scraper` passes a `scraper`
argument:

```python
def _fake_scraper(company, *, keywords="", location=None, limit=100):
    return [JobPosting(...).to_dict()]

result = run_pipeline("pwc", keywords="AI", scraper=_fake_scraper, ...)
```

`run_pipeline()` accepts a `scraper=` injection point precisely so
tests can swap the Workday call out without monkey-patching `httpx`.

### Anthropic SDK tool-use loop (`orchestrator.run_chat`)

The Anthropic loop in `run_chat()` is **not exercised by any test**.
Tests call `run_pipeline()` — the deterministic offline cousin — which
runs the same four steps in the same order without touching the SDK.

This is by design: the LLM loop is non-deterministic and would either
need expensive mocking or live API calls. Both are worse than testing
the deterministic path that shares almost all its logic with the
chat path.

### Subprocess workers

**Not mocked.** Tests use `subprocess.run([sys.executable, worker, …])`
against the real worker scripts, on synthetic data written to a
`tmp_path` fixture. This is the point.

---

## 6. Adding a new test

Worked example: a test that the scraper applies the `location` filter
correctly.

```python
# tests/test_smoke.py
def test_scraper_location_filter(tmp_path: Path):
    def _scraper(company, *, keywords="", location=None, limit=100):
        return [
            JobPosting(company.canonical_name, "A1WD", "Eng",
                       "Bengaluru, India", "", "u").to_dict(),
            JobPosting(company.canonical_name, "A2WD", "Eng",
                       "London, UK", "", "u").to_dict(),
        ]
    result = run_pipeline("pwc", location="India",
                          output_dir=tmp_path, scraper=_scraper)
    assert all("India" in p["location"] for p in result.postings)
```

Conventions:

- **Use `tmp_path`** (the pytest fixture) for any file the test
  writes. Never hard-code `/tmp/...`.
- **Inject fakes via parameters**, don't monkey-patch — every
  production path that touches the network already exposes a seam.
- **Assert on observable behavior** (output dict shape, exit code,
  CSV contents), not internal call counts.

---

## 7. Adding a new in-process agent

Use the existing CompanyConfirm + Scraper as a template:

1. Add `src/python/job_chatbot/agents/<name>.py` with one public
   function. Make it a pure-ish function — take a Company / dict in,
   return a dict out — so it serializes cleanly.
2. Add an entry to the `TOOLS` list in `orchestrator.py` with an
   `input_schema` and a description matching the Anthropic tool-use
   format.
3. Add a thin `_tool_<name>(...)` wrapper and register it in
   `_TOOL_DISPATCH`.
4. Add unit tests for whatever underlying tool/util the agent calls
   (e.g. if it talks to a new `tools/<thing>.py`, test that).
5. If the agent participates in the main pipeline, extend
   `run_pipeline()` and add an integration test that uses an injected
   stub — same shape as `test_run_pipeline_with_stub_scraper`.

---

## 8. Adding a new subprocess worker

Subprocess workers are how this implementation isolates expensive,
sandboxable, or remote-bound work from the orchestrator. Follow the
existing `db_worker.py` and `tester_worker.py` for reference.

### Step 1 — create the file

```python
# src/python/job_chatbot/workers/<name>_worker.py
"""<Name> worker — invoked as a subprocess by the orchestrator.

Usage::
    python <name>_worker.py --foo value < input.json

Stdin: <describe>. Stdout: JSON ``{...}``. Exit: 0 ok, 1+ on failure.
"""
if __name__ == "__main__":
    raise SystemExit(main())
```

The docstring **is** the contract — keep it accurate.

### Step 2 — define the CLI contract

- `argparse` for all flags (so `--help` works for free).
- One JSON document on stdin (not JSON Lines, not a stream).
- One JSON document on stdout. Logs go to stderr.
- Exit `0` on success, non-zero on failure.

### Step 3 — add an integration test

```python
def test_<name>_worker_round_trip(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(_PKG_DIR / "workers" / "<name>_worker.py"),
         "--foo", str(tmp_path / "x")],
        input=json.dumps({...}), text=True, capture_output=True, check=True,
    )
    assert json.loads(proc.stdout)["ok"] is True
```

Also extend the parametrize list in `test_worker_help`:

```python
@pytest.mark.parametrize("worker", ["db_worker.py", "tester_worker.py", "<name>_worker.py"])
```

### Step 4 — wire it into the orchestrator

Add a `_tool_<name>(...)` function that calls `subprocess.run`
exactly like `_tool_persist_jobs`. Register it in `_TOOL_DISPATCH`
and add an entry to the `TOOLS` list with an `input_schema`.

The existing two workers — `workers/db_worker.py` (persist) and
`workers/tester_worker.py` (validate) — are the canonical references.

---

## 9. Worker CLI contract checklist

Every new worker **must** tick every box. Tests 11 and 12 enforce
several of these; the rest are conventions the orchestrator relies on.

- [ ] `--help` prints usage and exits 0 (covered by `test_worker_help`).
- [ ] All inputs come from argparse flags or stdin — never from
      `os.environ` (no env-var side effects).
- [ ] **Stdin is one JSON document**, not a JSON Lines stream. Read
      with `sys.stdin.read()` then `json.loads`.
- [ ] **Stdout is JSON-only.** Print exactly one JSON document at the
      end. No banners, no progress dots, nothing else on stdout.
- [ ] Logs and diagnostics go to **stderr** (use `print(..., file=sys.stderr)`).
- [ ] Exit `0` on success, non-zero on any failure (the orchestrator
      uses the exit code for `check=True` semantics on the DB worker
      and `check=False` + JSON parsing for the tester worker).
- [ ] The worker is runnable directly: `python <path>/<name>_worker.py
      --help` must work without first installing the package. The
      `sys.path` shim at the top of `db_worker.py` is the pattern.
- [ ] The top-of-file docstring documents every flag, stdin shape, and
      stdout shape.

---

## 10. Test data / fixtures

The smoke tests use one in-file fixture, `_SAMPLE_ROWS`, defined at
the top of `test_smoke.py`:

```python
_SAMPLE_ROWS = [
    {"company": "PricewaterhouseCoopers", "job_id": "712616WD",
     "title": "Senior AI Engineer", "location": "Bengaluru, India",
     "posted_on": "Posted 3 Days Ago",
     "url": "https://pwc.wd3.myworkdayjobs.com/job/Bengaluru/_712616WD"},
    {"company": "PricewaterhouseCoopers", "job_id": "712617WD", ...},
]
```

Two rows with matching keys to `tools.storage.CSV_HEADERS`. Reuse it
when you add tests that need realistic posting shapes.

For paths, **always use pytest's `tmp_path`** — it's per-test, cleaned
up automatically, and works on any OS.

There is no `conftest.py` today. If you add cross-cutting fixtures,
put them there.

---

## 11. What's deliberately NOT tested

The following are out of scope on purpose. If you find yourself
wanting to test them, push back hard — usually the right move is to
extend the deterministic path instead.

- **Live Anthropic API calls.** `run_chat()` is not exercised. Adding
  a test that hits `api.anthropic.com` would make the suite require
  a key and be non-deterministic.
- **Live Workday HTTP.** `tools.workday.search_jobs` is never run for
  real in tests. The integration test uses `_fake_scraper` via the
  `scraper=` injection point on `run_pipeline`.
- **The `--chat` REPL.** The chat-mode branch in `main.py` is gated on
  `ANTHROPIC_API_KEY` and shells out to `run_chat()`. No test enters
  that branch.
- **Rich-rendered terminal output.** We assert on data
  (`result.postings`, exit codes), not on what the table looks like.

---

## 12. Coverage

We don't enforce a coverage threshold today. Suggested measurement:

```bash
uv pip install coverage
uv run coverage run -m pytest -q
uv run coverage report -m --include="src/python/job_chatbot/*"
```

Expected gaps in any coverage run:

- `orchestrator.run_chat` — deliberately untested (see §11).
- `tools.workday.search_jobs` — uncovered HTTP code path.
- The `if __name__ == "__main__":` blocks in `main.py` and the
  workers (when measured outside the subprocess that invokes them).

These gaps are acceptable. Coverage of new code should land above
80% — primarily through `run_pipeline` integration tests and direct
unit tests on tools.

---

## 13. Continuous integration

Suggested GitHub Actions workflow. Drop into
`.github/workflows/test.yml`:

```yaml
name: tests
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install package
        run: uv pip install --system -e ".[dev]"
      - name: Run pytest
        run: uv run pytest -q
```

Notes:

- No secrets needed — the suite does not hit the Anthropic API or the
  network.
- Subprocess tests work on the GitHub-hosted Linux runner without
  extra setup because `sys.executable` resolves to the runner's
  Python.

---

## 14. Test smells (hybrid-specific)

These are mistakes that are easy to make when authoring tests for an
architecture that mixes in-process and subprocess work.

| Smell | Why it bites | Fix |
|-------|--------------|-----|
| Test leaves a `db_worker.py` / `tester_worker.py` process running | A hung subprocess between tests pollutes the next test's environment and can hold open file handles on `tmp_path`. | Use `subprocess.run(..., timeout=...)` (not `Popen` without a wait); always assert on the return code; never `Popen(...).poll()` without `wait()`. |
| Hard-coded `/tmp/something` paths | Breaks on Windows / parallel test runs / containers where `/tmp` is read-only. Worse: tests interfere with each other. | Use the `tmp_path` fixture. Always. |
| Calling `python3` or `python` directly | The PATH `python` may be a different interpreter than the one running pytest — your test will silently exercise the wrong env. | Use `sys.executable` (see `test_subprocess_db_then_tester`). |
| Asserting on `proc.stdout` as a substring | Worker output is JSON. Sub-string matching couples the test to formatting (whitespace, key order). | Parse with `json.loads(proc.stdout)` and assert on the dict. |
| Setting `ANTHROPIC_API_KEY` in tests | Encourages tests that accidentally hit the live API. | Never set it. Tests must pass with the variable unset. |
| Mocking `subprocess.run` | Hides the entire purpose of the IPC layer; lets the worker CLI contract drift undetected. | Run the workers for real against `tmp_path`. |
| Mixing stderr noise into stdout assertions | If a worker prints a deprecation warning to stdout it will break the orchestrator's `json.loads`. | When adding to a worker, route logs to stderr; assert on stderr separately if you must. |

---

## 15. Linting + type-checking

There is no enforced linter in `pyproject.toml` today. Recommended
tooling when you add it:

```bash
# Formatter + linter (one tool)
uv pip install ruff
uv run ruff check src/python tests
uv run ruff format src/python tests

# Type-checker
uv pip install mypy
uv run mypy --strict src/python/job_chatbot
```

The codebase is annotated with `from __future__ import annotations`
throughout and uses modern type hints (`str | None`, `list[dict]`),
so `mypy --strict` should be reachable with a small `mypy.ini` that
ignores `anthropic` and `httpx` stubs.

For pre-commit:

```yaml
# .pre-commit-config.yaml (suggested)
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
      - id: ruff-format
```

When you add these, also wire them into the CI workflow in §13 as
extra steps before `uv run pytest -q`.
