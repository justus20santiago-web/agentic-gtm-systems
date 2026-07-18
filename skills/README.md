# Skills

These are portable versions of skills developed while operating a larger private agent system. Machine-specific paths, company policy, live service identifiers, and private tool contracts have been removed.

| Skill | Use it for | Central idea |
|---|---|---|
| [grind](grind/SKILL.md) | Resolve a finite backlog across turns | Ledger-backed state, one item per turn, independent convergence checks |
| [ralph-test-loop](ralph-test-loop/SKILL.md) | Drive a test suite to green | Fix causes, preserve the completion promise, bound iterations |
| [messaging-lint](messaging-lint/SKILL.md) | QA outbound copy | Deterministic floor plus mandatory human-grade read |
| [mcp-audit](mcp-audit/SKILL.md) | Compare a web app with an MCP/API wrapper | Read-only record, endpoint inventory, coverage diff, independent reproduction |
| [tool-expert](tool-expert/SKILL.md) | Build a local expert for one tool | Official docs plus a read-only machine map plus an independently verified test |

Copy a skill directory into the skills location used by your agent harness, then adapt its paths and tool names. Do not add credentials to a skill file.
