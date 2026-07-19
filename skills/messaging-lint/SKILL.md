---
name: messaging-lint
description: Apply a two-tier quality gate to a messaging batch: a deterministic script floor followed by a mandatory row-by-row human-grade read. Use before handing outbound copy to any review, scheduling, or send system and after every edit pass.
---

# Messaging lint: floor plus ceiling

A regex can catch repeated structures, filler, hedges, punctuation, and suspicious edits. It cannot certify that a message is accurate, coherent, relevant, or worth sending.

## Tier 1: deterministic floor

```bash
python3 scripts/messaging_lint.py batch.csv --verbose \
  --baseline pre_edit.csv --collision-terms terms.txt
```

The script checks:

- shared opener and closer integrity
- filler and hedge language
- em dashes and grammar-corruption smells
- repeated personalized phrases across rows
- suspicious word-count outliers
- campaign-specific positioning collisions
- survival of distinctive source language after an edit pass

Fix violations and repeat until the script exits zero. Always use `--baseline` after an edit pass.

## Tier 2: mandatory inline read

Read every row and mark `PASS` or `FAIL` with a reason. Check:

1. Does every sentence parse naturally when read aloud?
2. Is each factual claim precise enough for the reader's expertise?
3. Does the opener show current relevance instead of reciting a biography?
4. Does every bridge have a clear antecedent?
5. Is attribution complete?
6. Does the message avoid explaining the reader's own product back to them?
7. Is the tension expressed in the reader's operating language?
8. Is there no unsupported number, outcome, customer claim, or invented quote?
9. Is there at most one proof point?
10. Does the requested action fit the relationship and channel?

Fix every `FAIL`, then run Tier 1 again because prose edits can reintroduce mechanical violations.

## Output contract

Report separately:

- Tier 1 violations found and fixed
- Tier 2 verdict for every row and the reason for each fix
- Any claim-level source verification that was not performed

Never collapse both tiers into one generic “clean” verdict.
