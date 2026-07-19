# n8n workflow blueprints

These JSON files are inactive, credential-free teaching exports. They preserve the design patterns without publishing production IDs, paths, data, or service-specific configuration.

| Workflow | Pattern |
|---|---|
| [Evidence-gated decision](workflows/evidence-gated-decision.json) | Separate evidence and policy from the approved/hold branches |
| [Async enrichment callback](workflows/async-enrichment-callback.json) | Authenticated callback, durable write, retry, explicit 200/502 responses |
| [Reply-stop guard](workflows/reply-stop-guard.json) | Read-only reply scan with fail-closed queue holds |

## Before import

1. Review the JSON and confirm `active` is `false`.
2. Import into a non-production project.
3. Replace every `REPLACE_...` credential or resource ID.
4. For self-hosted-only nodes such as Execute Command, replace the example command with a bounded local adapter.
5. Validate against the target n8n version.
6. Pull the saved workflow back and inspect its `connections` object.
7. Confirm the intended credential is bound on every credentialed node.
8. Test with pinned representative data and identify any downstream node that can still cause a side effect.
9. Configure a published workflow-level error handler for unattended workflows.
10. Activate only after policy and consequence review.

## Compatibility note

The exports use node shapes observed on a contemporary self-hosted n8n instance. n8n node parameters and type versions change. Treat the target instance's node schemas and validation output as canonical.

## What is intentionally absent

- live workflow IDs and execution history
- real credential references
- customer or contact data
- vendor-specific campaign and sequence IDs
- active send, enrollment, CRM-write, payment, or publication nodes
- pin data and static execution state
