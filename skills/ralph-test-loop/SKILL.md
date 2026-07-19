---
name: ralph-test-loop
description: Run a bounded, filesystem-backed loop that drives a test suite to green by fixing the cause of each real failure, re-running focused tests, and then re-running the full suite. Stop only when the ledger shows zero failures, a genuine external block is recorded, or the iteration cap is reached.
---

# Ralph test loop

The runner is deterministic. The agent diagnoses and fixes code. A state file and JSON ledger make the loop resumable.

## Runner contract

The configured command must:

- write a JSON ledger shaped like `{ "fail": 0, "results": [{"id":"test-id","status":"PASS","tail":"..."}] }`
- exit `0` only when `fail == 0`
- support a focused-test mode when practical

## Per-iteration loop

1. Read the state file, rails, completion promise, and latest ledger.
2. Run the full suite.
3. If `fail == 0`, append a closing log entry, emit the exact completion promise, and stop.
4. For each failure, inspect its captured output and the code it exercises.
5. Fix the root cause in code. Never weaken or delete the test to force green.
6. Re-run the focused test.
7. Re-run the full suite because a local fix can cause a regression.
8. Stop after six iterations and report remaining failures, diagnoses, and attempted fixes.

## Genuine blocks

An unavailable external service, expired human authentication, or an enforced quota may be marked `BLOCKED` with a concise reason when it is not a code defect. Do not use `BLOCKED` for a hard bug or an unclear diagnosis.

## Hard rules

- Never emit the completion promise unless the ledger proves it.
- Fix implementation causes, not the test contract.
- Keep diffs small and reviewable.
- Do not add sends, paid actions, destructive mutations, or persistent jobs to make a test pass.
- Preserve prior block decisions unless new evidence changes them.
