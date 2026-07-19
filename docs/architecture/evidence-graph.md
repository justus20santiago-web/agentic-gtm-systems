# Evidence graph

An evidence graph is a derived reasoning layer, not a new source of truth. It connects already-governed observations so an agent can explain why two entities or decisions are related.

```mermaid
flowchart LR
    A["Governed source records"] --> B["Deterministic extractors"]
    B --> C["Versioned nodes and edges"]
    C --> D["Bounded neighborhood packet"]
    D --> E["Agent explanation or comparison"]
    E --> F["Decision receipt"]
```

## Construction rules

- Deterministic extraction is first-class; model extraction is an injected and reviewable adapter.
- Every edge records its source, confidence, and extraction version.
- Graph refreshes create versioned snapshots rather than mutating evidence in place.
- Query planning starts from bounded templates and only then permits validated graph queries.
- The graph advises a decision unit; deterministic policy remains authoritative.

## Packet boundary

Agents receive a small neighborhood packet with the relevant nodes, edges, source pointers, and missing-evidence flags. They do not receive the entire graph. This improves explainability, reduces context cost, and prevents unrelated private data from leaking across tasks.

Public examples should use synthetic entities. Production graphs, identities, source documents, and derived packets remain private.
