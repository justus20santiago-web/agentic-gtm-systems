# Signal monitor contract

A useful monitor is a product with inclusion rules, evidence, state, cadence, and feedback. It is not a recurring search query.

```yaml
name: ai_leadership_hire
version: 1
entity_key: account_domain
inclusion_rule: a named executive or functional leader started an AI-related role
required_evidence:
  - source_url
  - exact_quote
  - event_date
freshness_days: 45
cadence: weekly
dedup_key: account_domain + person + role + event_date
output:
  - event
  - evidence
  - relevance
  - recommended_next_action
feedback:
  labels: [useful, not_useful]
  comment: optional
```

## State machine

`discovered → extracted → verified → deduplicated → delivered → labeled`

Search discovers candidates. Extraction verifies the source. Only verified deltas enter the durable signal cache. Delivery should include enough evidence for a human to label usefulness without opening five tools.

## Optimization rule

Improve the narrow inclusion rule from labeled evidence. Adding more detectors increases noise faster than it increases precision.
