# Security and publication boundary

## Never commit

- API keys, OAuth tokens, cookies, passwords, webhook secrets, or authorization headers
- Credential IDs from a real n8n instance
- Customer, prospect, employee, or account records
- Internal hostnames, private endpoints, browser-profile identifiers, or local absolute paths
- Active workflow exports, execution data, pin data, or production campaign IDs
- Vendor payloads copied from authenticated applications

## n8n safety

Every workflow in `n8n/workflows/` must:

- set `active` to `false`
- omit execution and pin data
- use placeholders for every credential or external resource ID
- avoid send, enroll, publish, payment, CRM-write, or activation nodes
- expose an explicit hold/error branch where failure could otherwise disappear

Importing a workflow is not permission to activate it. Validate it against the target n8n version, inspect the saved connections, bind the intended credentials, use pinned test data, and review every downstream side effect before publication.

## Reporting a problem

Open a private security advisory on GitHub if a committed artifact appears to contain a secret or private operational detail. Rotate the affected credential before treating repository history cleanup as remediation.
