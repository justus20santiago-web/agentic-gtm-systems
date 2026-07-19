---
name: tool-expert
description: Build or refresh a tested local expert for one named tool. Combine official documentation with a dated, read-only map of the machine's actual configuration, write explicit safety rails for every consequential action class, and independently verify the expert on a real read-only task.
---

# Tool-expert factory

## Output

1. An expert definition for one tool
2. A dated test record with factual claims, independent checks, and a pass/fail verdict

An untested expert is incomplete.

## Pipeline

1. **Research:** prefer official documentation and live tool schemas.
2. **Map locally:** inspect installation, version, configuration, connections, and existing objects read-only.
3. **Author:** explain the mental model, local map, common workflows, limitations, and safety rails.
4. **Test:** give the expert a real read-only task, then independently verify every factual claim.
5. **Record:** save the prompt, claims-to-reality table, communication score, safety score, and verdict.

## Required safety rails

Classify and gate:

- destructive operations
- outward messages or publications
- paid or rate-limited actions
- permission and identity changes
- production mutations

Discovery remains read-only. A safe write test requires explicit current authorization and must be reversible.

## Refresh rule

Date-stamp machine-specific facts. Refresh the map and re-run the test when versions, credentials, connected accounts, or tool schemas change.
