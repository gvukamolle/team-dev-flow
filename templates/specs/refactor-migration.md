---
tdf_artifact: spec
tdf_spec_type: refactor_migration
tdf_status: draft
tdf_id: "{{ID}}"
parent_refs: ["{{PARENT_REF}}"]
---

# {{TITLE}}

## Current and target state

- Current ownership/architecture:
- Problem or forcing function:
- Target ownership/architecture:
- Behavior that must remain unchanged:

## Migration contract

- DES-01 — target architecture decision:
- Compatibility window:
- Data/schema/API/event migration:
- Ordering and dependencies:
- Dual-read/write or adapter strategy:
- Cutover signal:
- Rollback path:

## Acceptance

- AC-01 — preserved invariant; verification:
- AC-02 — target behavior; verification:
- Performance/security/observability proof:
- Cleanup deferred until after cutover:

## Task candidates

| Phase/task | Owner | Parent AC | Parent DES | Entry gate | Exit evidence |
|---|---|---|---|---|---|
