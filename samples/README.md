---
agent-notes: { ctx: "index of methodology demonstration samples", deps: [docs/methodology/phases.md, docs/methodology/personas.md], state: active, last: "sato@2026-03-21" }
---

# Samples

These directories are pre-populated project snapshots that demonstrate what the vteam-hybrid methodology produces. They are **not runnable applications** -- they are the artifacts that result from following the methodology: test files, implementation code, ADRs, debate transcripts, sprint plans, retrospectives, and code reviews.

Each sample is self-contained. Read the README in each directory, then browse the files it points to.

## Available Samples

| Sample | Demonstrates | Time to Explore |
|--------|-------------|-----------------|
| [hello-tdd/](hello-tdd/) | Core TDD workflow (Tara writes tests, Sato makes them pass) | ~5 minutes |
| [architecture-debate/](architecture-debate/) | Architecture Gate (Archie proposes, Wei challenges) | ~5 minutes |
| [full-sprint/](full-sprint/) | Complete sprint lifecycle (plan, TDD, review, done gate, boundary) | ~10 minutes |

## How to Read the Samples

1. **Start with the README** in each sample directory. It explains the scenario and walks you through the files in order.
2. **Look at the agent-notes** at the top of each file. They show which agent created the file and when -- this is how the methodology tracks authorship.
3. **Notice the sequence.** In `hello-tdd/`, the test file was written before the implementation. In `architecture-debate/`, the ADR was written before implementation could begin. In `full-sprint/`, the sprint plan precedes all other artifacts.

## What These Samples Are Not

- **Not runnable code.** The Python files in `hello-tdd/` demonstrate the TDD artifacts, not a working CLI tool. There is no `pyproject.toml` or virtual environment.
- **Not templates.** To start a real project, use `/quickstart` on the vteam-hybrid template. These samples show what that process produces.
- **Not exhaustive.** Each sample highlights one aspect of the methodology. A real project would have all of these artifacts and more.
