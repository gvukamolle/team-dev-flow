# Adopt Team Dev Flow

## Select one profile

- `generic`: discovery/specification/planning without a remote tracker;
- `obsidian-local`: writable Local Markdown/Obsidian TaskStore;
- `kilo-github`: Kilo Code with GitHub Issue read and Issue/PR preview.

Do not silently synchronize status between canonical TaskStores.

## Pilot

Use non-production feature, bugfix, and research tasks. Keep existing CI, branch
protection, approvals, release, and deploy controls authoritative. Measure routing
errors, scope drift, false review findings, missing evidence, and setup friction.

Run the shared lifecycle:

```text
Capture → Clarify/Research → Specify → Plan → Tasks
→ Implement → Verify → Review → Converge → Handoff
```

Promote one exact canary SHA/digest only after the pilot passes, and retain the
previous stable pointer for rollback.
