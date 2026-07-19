# Decision-unit contract

A decision unit is the smallest reusable component that can answer one bounded question and explain what should happen next.

```yaml
name: closed_lost_reentry
version: 2
owner: revenue_operations
purpose: decide whether a previously lost account deserves a fresh review
inputs:
  - account_id
  - website
outputs:
  decision: REENGAGE_NOW | BANK | DROP
  evidence_ids: string[]
  blockers: string[]
  next_action: string
  next_eligible_at: datetime | null
policy:
  allowed_actions: [produce_internal_brief]
  prohibited_actions: [send_message, enroll_contact, write_crm]
cost:
  max_units: 10
evidence:
  freshness_days: 30
  minimum_sources: 2
evaluation:
  primary_metric: human_useful_rate
  safety_metrics: [false_positive_rate, unsupported_claim_rate]
```

## Required properties

- **One decision:** not an open-ended agent job.
- **Typed contract:** callers know exactly what can be returned.
- **Evidence boundary:** the unit states what proof is sufficient.
- **Authority boundary:** outward actions are not implied by a recommendation.
- **Cost boundary:** a retry cannot silently multiply spend.
- **Version identity:** feedback can be attributed.
- **Explicit next action:** downstream orchestration never guesses intent.

## Registry fields

Use a shared registry across skills, workflows, functions, and playbooks:

`name, version, owner, purpose, inputs, outputs, evidence, cost, policy, next_action, evaluation, status`

This prevents duplicate logic hiding behind different automation products.
