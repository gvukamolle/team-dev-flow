# Universal requirements

## Core

- One FlowProfile selects one AgentHost, one canonical TaskStore, and one GitProvider.
- Missing capabilities fail closed; read, preview, and write are distinct modes.
- Work uses provider-neutral WorkItem, WorkContext, Task Contract v2, typed Spec,
  verification, review, and handoff contracts.
- Research does not authorize hidden production implementation.
- Every accepted criterion and design decision maps to a Task or explicit evidence.
- Verification and review bind to the exact current full Git SHA.

## Local TaskStore

- The user explicitly selects a vault-relative root.
- Traversal, symlinks, reserved vault paths, root drift, missing relations,
  concurrent writers, and incomplete history fail closed.
- Writes are previewable, atomic, rollback-capable, idempotent, and preserve
  unknown properties and user text.
- `Dashboard.base` is a projection, not another source of truth.

## GitHub

- Issue reads are bounded and normalized.
- Issue/PR previews separate argv from stdin and expose no apply command.
- A PR preview requires the exact current full SHA.
- GitHub authentication remains owned by the user's environment.

## Hosts and distribution

- Host packages are project-local, hash-inventoried, transactional, and refuse
  symlinks, unowned collisions, and managed-file drift.
- Releases use an explicit inventory, secret scan, deterministic archive, full
  Git SHA, and SHA-256.
- Canary and stable remain independent; rollback restores the prior immutable pointer.
