# Local Markdown / Obsidian TaskStore

The adapter stores one canonical Team Dev Flow workspace below an explicitly selected Obsidian vault directory. It never edits `.obsidian` and never treats an arbitrary note folder as authoritative without the `obsidian-local` FlowProfile.

## Layout

```text
<selected root>/
├── Dashboard.base
├── Projects/<PROJECT>/Project.md
├── Projects/<PROJECT>/Initiatives/<ID>.md
├── Projects/<PROJECT>/Epics/<ID>.md
├── Projects/<PROJECT>/Specs/<ID>.md
├── Projects/<PROJECT>/Tasks/<ID>.md
└── .team-dev-flow/
    ├── store.json
    ├── store.lock
    └── history/<ref-hash>.jsonl
```

Paths are stable. Dates such as `due`, `created`, and `updated` remain properties; notes are not moved into daily folders. Parent and dependency properties include both provider-neutral refs and Obsidian wikilinks to existing artifacts.

## Ownership

The adapter owns the `tdf_*` identity fields plus `title`, `status`, `health`, `stage`, `parent_ref`, `parent`, `dependency_refs`, `dependencies`, `created`, `updated`, and `due`. Unknown properties and all user text outside the managed marker pair are preserved. Duplicate managed properties, malformed markers, missing relation targets, root drift, symlinks, and concurrent writers fail closed.

`preview` renders the exact candidate without creating directories, notes, or history. `upsert` acquires the store lock, writes a same-directory temporary file, fsyncs it, atomically replaces the note, and appends a redacted history event through another atomic replacement. If history fails, the note is restored or removed to avoid partial state.

`Dashboard.base` follows the native Obsidian Bases YAML format and filters on the unique `tdf_store` identity. It exposes Today, In progress, Blocked, Verification, and Review views without editing vault plugin settings.
