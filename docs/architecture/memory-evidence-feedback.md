# Memory, evidence, and feedback

An agent needs three different forms of memory. Combining them produces stale facts, unverifiable claims, and hard-to-debug behavior.

| Memory layer | Purpose | Typical contents |
|---|---|---|
| Operational source of truth | Current policy and state | Scope rules, suppression, ownership, allowed actions |
| Evidence store | Reprocessable source material | Quotes, payloads, timestamps, source URLs, confidence |
| Outcome ledger | What happened after a decision | Human label, reply, conversion, error, cost, version IDs |

## Preserve observations at field level

For every material observation, keep:

```yaml
field: work_email
value: person@example.com
source: provider_name
observed_at: 2026-01-01T00:00:00Z
confidence: high
cost_units: 1
status: accepted # accepted | no_result | blocked | error
approved_by: null
written_back: false
```

`blocked`, `error`, and `attempted_no_result` are different outcomes. Collapsing them causes accidental retries and repeated spend.

## Feedback must bind to a version

A useful label identifies the artifact that earned it:

```yaml
decision_unit: account_signal_monitor
decision_version: 3
prompt_hash: sha256:example
evidence_receipt_id: receipt_123
output_id: signal_456
label: not_useful
comment: source proves the event, but it is irrelevant to the account
```

Without version binding, a feedback loop cannot tell whether a policy, prompt, evidence source, or transport change improved the result.

## Write-back rule

Every completed run should leave a durable receipt containing inputs, sources, policy version, decision, next action, cost, and outcome status. Chat transcripts are not an operational database.
