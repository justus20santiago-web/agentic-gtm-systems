---
name: mcp-audit
description: Audit an authenticated web application's read-only UI capabilities against an existing API wrapper or MCP tool surface. Record a bounded walkthrough, inventory XHR and fetch calls, diff observed endpoints against current coverage, and independently reproduce candidates before treating them as contracts.
---

# MCP audit: record, diff, verify

## Deliverables

1. Read-only video or screenshots of the scoped surfaces
2. Deduplicated endpoint inventory: method, host, templated path, triggering surface
3. Coverage file for the existing wrapper and MCP tools
4. Ranked capability gaps
5. Independently reproduced, redacted endpoint cards

## Safety boundary

- Use a dedicated audit browser profile, never a production automation profile.
- Do not record login or credential entry.
- Navigation is read-only unless the user authorizes one exact reversible write test.
- Deny clicks matching send, enroll, delete, save, publish, archive, payment, or similar consequences.
- Treat an internal UI endpoint as a candidate, not a supported contract.
- Store sanitized examples only. Never preserve cookies or authorization headers.

## Loop

1. **Scope one target.** Record the hypothesis, auth layer, UI path, and forbidden clicks.
2. **Record.** Capture the route, visible state, and XHR/fetch traffic for that target only.
3. **Review cold.** Identify candidate routes, payload shapes, stable locators, and stop gates.
4. **Extract.** Create a redacted endpoint card.
5. **Verify independently.** Reproduce without relying on the original browser recording.
6. **Diff coverage.** Compare with the current wrapper routes and MCP tool schemas.
7. **Fortify.** Add a read-heavy typed tool only after verification and policy review.

## Verification gate

An endpoint is `VERIFIED` only when all are documented:

- observed request
- auth class, without secret values
- required request shape
- success and error response shapes
- independent reproduction
- intended invocation path
- safety tier: `read | write | never-call`

Anything else is `PARTIAL` or `NEEDS_PASS`.
