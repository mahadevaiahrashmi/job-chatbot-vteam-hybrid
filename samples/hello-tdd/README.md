---
agent-notes: { ctx: "walkthrough of TDD sample artifacts", deps: [samples/hello-tdd/tests/test_greet.py, samples/hello-tdd/src/greeter/cli.py], state: active, last: "sato@2026-03-21" }
---

# Sample: hello-tdd

**What this demonstrates:** The core TDD workflow -- Tester Tara writes failing tests first, SDE Sato writes the minimum code to make them pass, then refactors.

**Time to explore:** ~5 minutes

## Scenario

A user ran `/quickstart` and described a simple CLI greeting tool. The methodology produced a backlog with three items. The first item ("basic greet command") went through the TDD pipeline:

1. Tara wrote failing tests (the "red" phase)
2. Sato wrote implementation code to make them pass (the "green" phase)
3. Sato refactored (the "refactor" phase -- in this case the code was simple enough that no refactoring was needed)

## Files to Read (in order)

### 1. `CLAUDE.md`
This is what a CLAUDE.md looks like after `/quickstart` fills it in. Notice the project name, description, and tech stack are populated -- these were blank in the template.

### 2. `docs/plans/quickstart-backlog.md`
The backlog that `/quickstart` created. Three items, sized S/S/M. The first item is checked off -- that is the one we implemented in this sample.

### 3. `tests/test_greet.py`
**This file was written by Tara before any implementation code existed.** That is the key insight of TDD -- the tests define the expected behavior, and they start out failing because there is nothing to test yet.

Notice:
- Three focused tests: default name, custom name, empty name raises an error
- Each test name describes the behavior it verifies, not the function it calls
- The empty-name test uses `pytest.raises` -- Tara always covers unhappy paths
- The agent-notes show `tara` as the author

### 4. `src/greeter/cli.py`
**This file was written by Sato after the tests existed.** Sato read the failing tests, understood what was expected, and wrote the simplest code that makes them pass.

Notice:
- The implementation is minimal -- no unnecessary features, no over-engineering
- The `greet()` function validates input at the boundary (empty name check) and has a clean happy path
- The agent-notes show `sato` as the author
- The code matches the test expectations exactly: `"Hello, World!"` for default, `"Hello, {name}!"` for custom

## Key Takeaway

The tests came first. The implementation exists to satisfy the tests, not the other way around. If you removed the implementation and gave someone only the test file, they could write a compatible implementation without any other documentation.
