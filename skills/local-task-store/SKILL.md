---
name: local-task-store
description: "Initialize or operate the selected Local Markdown/Obsidian TaskStore, preserving user notes while creating or updating Projects, Initiatives, Epics, Specs, Tasks, history, and Dashboard.base views."
---

# Local Markdown / Obsidian TaskStore

Use this skill only after the user selects an exact Obsidian vault and vault-relative Team Dev Flow folder. Never infer a vault from unrelated notes, write under `.obsidian`, or make local Markdown canonical alongside another TaskStore in the same FlowProfile.

## Initialize

Preview the target path, then run:

```bash
python3 scripts/local_task_store.py init --vault <vault-root> --folder <vault-relative-folder>
```

The adapter rejects traversal, reserved folders, files, and symlinks. It creates a stable store identity, a lock, and `Dashboard.base` views for Today, In progress, Blocked, Verification, and Review.

## Preview and write

Use `preview` with the same arguments as `upsert` before a material change. A relation uses `kind:id`, for example `--parent epic:EPIC-12` or `--depends task:TASK-4`.

```bash
python3 scripts/local_task_store.py preview --root <store-root> --project FLOW --kind task --id TASK-1 --title "Add adapter"
python3 scripts/local_task_store.py upsert --root <store-root> --project FLOW --kind task --id TASK-1 --title "Add adapter"
```

Writes are lock-protected, same-directory atomic replacements with rollback. Stable paths do not move by day; `due`, `created`, and `updated` are properties. The adapter owns only `tdf_*` and workflow properties, preserves unknown properties and user text outside its managed markers, validates parent/dependency targets, and appends redacted history only when content changes.

## Authority and handoff

- The selected `obsidian-local` FlowProfile is the only condition that makes this store authoritative.
- Preview is not authorization for a remote write, Git push, PR/MR, merge, release, or deployment.
- Use provider-neutral refs from the note and bind review/verification to the current Git SHA.
- If the root identity changes, a link target is absent, markers are malformed, or another writer holds the lock, stop fail-closed instead of repairing silently.
