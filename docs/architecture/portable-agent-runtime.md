# Portable agent runtime

A reliable local agent stack separates judgment, deterministic execution, and authenticated tools. Model choice is a routing concern; authority belongs to policy and the user.

```mermaid
flowchart TD
    A["User intent"] --> B["Routing contract"]
    B --> C["Reasoning agent"]
    B --> D["Deterministic worker"]
    B --> E["Authenticated tool adapter"]
    C --> F["Decision unit"]
    D --> F
    E --> F
    F --> G{"Consequence gate"}
    G -->|"approved"| H["Bounded action"]
    G -->|"hold"| I["Human review"]
```

## Runtime contract

- The reasoning agent handles ambiguity, synthesis, and explicit tradeoffs.
- Deterministic workers own repeatable parsing, validation, scoring, and file transforms.
- Tool adapters own authentication and expose the smallest typed capability possible.
- Routing selects a capable surface but cannot broaden its permissions.
- Every long-running loop has a machine-checkable exit condition and durable state.

Machine paths, installed models, credentials, browser profiles, and tool-specific routing are deployment details. A portable release publishes the interfaces, fallback rules, and proof requirements instead.
