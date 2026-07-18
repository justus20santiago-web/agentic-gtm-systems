---
name: grind
description: Resolve a finite set of already-identified decisions, findings, risks, or open items one at a time using a durable ledger, bounded adversarial review, a cross-item reconvene pass, and a final independent goalkeeper. Use when three or more concrete items are already on the table. Do not use for open-ended greenfield building.
---

# Grind

Turn a finite backlog into a converged, reviewable ledger. State lives on disk, not in the chat session.

## Preconditions

- A named, finite work list already exists.
- The completion criteria are concrete and falsifiable.
- A durable ledger path is available.
- Any outward, destructive, or paid action has a separate explicit authorization boundary.

If any precondition is missing in an unattended run, mark the ledger `needs_human` and stop.

## Ledger contract

```yaml
record_type: grind_ledger
status: in_progress # in_progress | converged | needs_human | halted
goal_charter: "Frozen statement of success"
item_count: 5
turns: 0
reloop_rounds: 0
reviewer_spawns: 0
started_at: 2026-01-01T00:00:00Z
reconvene_verdict: null
goalkeeper_verdict: null
```

Each item has a stable anchor and literal status:

```markdown
## Item 1 — Decide the retry policy
<!-- item:1 -->
status: pending
reloops: 0
Sources:
Confidence:
Dissent:
Resolution:
```

## Startup gates on every turn

1. Acquire a single-writer lock before reading or creating the ledger.
2. Stop immediately when the run status is terminal.
3. In unattended mode, require a pre-committed charter and explicit `headless_approved: true`.
4. Apply persisted brakes before new work:
   - `turns >= 5 * item_count + 20`
   - `reloop_rounds >= 3`
   - `reviewer_spawns >= 4 * item_count + 16`
   - elapsed wall time exceeds two hours
5. On a brake, mark remaining items `NEEDS YOU`, set `halted`, release the lock, and stop.

Never keep a brake counter only in memory.

## One-item algorithm

1. Reclaim a stale `in_progress` item whose claim expired or whose resolution is empty.
2. Select the first `pending` item.
3. Atomically claim it and increment `turns` before review begins.
4. Give an isolated adversarial panel only the frozen charter, the item, and relevant on-disk evidence.
5. Resolve exactly one item. Record evidence, confidence, dissent, and either `done` or `NEEDS YOU`.
6. Re-read the exact item anchor and verify the persisted content.
7. Release the lock and end the turn.

Only the parent process writes the ledger. Reviewers return structured findings.

## Convergence

When no items remain pending:

1. **Reconvene:** an isolated reviewer sees all concise resolutions and checks cross-item consistency, missing dependencies, and contradictions.
2. If it flags rework, increment `reloop_rounds`, return affected items to `pending`, and stop the turn.
3. **Goalkeeper:** a separate held-out reviewer evaluates the complete ledger against the frozen charter.
4. Set `converged` only when the goalkeeper accepts and every item is terminal.

If isolated review is unavailable, do not self-certify. Set `needs_human`.

## Hard rules

- The charter freezes before item work. New scope starts a new grind.
- One item per turn.
- Nothing self-grades.
- Non-empty output is not verification; re-read and compare the exact block.
- Status is a literal field, not a heading or emoji.
- Any outward action requires its own current authorization; resolving an item does not grant it.
- Repeated identical objections halt faster than the round cap.

## Completion line

Emit exactly one machine-readable status at the end of each turn:

`GRIND_STATUS: in_progress | converged | needs_human | halted`
