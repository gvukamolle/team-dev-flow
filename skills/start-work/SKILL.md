---
name: start-work
description: "Start or resume implementation from an existing Jira, GitHub, GitLab, local Markdown/Obsidian, Notion, or custom TaskStore record; normalize its hierarchy and create a bounded Task Contract before edits."
---

# Start work from a TaskStore record

## Inputs

Required: one implementation scope reference. Examples: Jira key, GitHub/GitLab issue URL, or a local task/spec path. If several references are supplied, ask which is the implementation Task unless the user explicitly requests portfolio/dependency analysis.

## Step 1 — Provider context

Select the available TaskStore adapter and load a bounded record, parent chain, direct children/links, relevant discussion, and source revision. For Jira, call `jira_get_task_context` and prefer its provider-neutral `normalized` packet while preserving the legacy Jira fields as evidence.

Do not infer ordering from identifiers. Do not claim a missing parent relation exists. If the requested provider is unavailable, accept a complete exported artifact only with explicit offline-source selection and record reconciliation as a boundary.

## Step 2 — Repository preflight

Read-only checks:

- find repository root and applicable `AGENTS.md` files;
- inspect current branch, HEAD, target branch, and `git status`;
- identify user-owned changes;
- locate relevant code, tests, docs, and CI commands;
- assess whether this repository plausibly implements the Jira task.

Use a scope-analyst/explorer subagent for noisy codebase discovery when it can work independently. It is read-only and returns evidence, not implementation.

## Step 3 — Readiness

Apply the provider-neutral readiness rules plus [`readiness.md`](../../references/jira/readiness.md) for Jira and return exactly one state:

- `READY`
- `NEEDS_CLARIFICATION`
- `NEEDS_RESEARCH`
- `BLOCKED`

List the evidence and smallest next action. Do not start editing unless the state is `READY`.

## Step 4 — Task Contract

Build a provider-neutral v2 contract conforming to [`task-contract-v2.schema.json`](../../contracts/task-contract-v2.schema.json). Existing Jira-only sessions may continue validating v1 contracts. Include scope reference, source revision, explicit in/out scope, validations, risks, dependencies, approval boundaries, and contract hash.

Show a compact readback. If clarification changes public scope, prepare an exact adapter-specific update draft. Apply remote writes only with authority, then re-read the source and rebuild the Task Contract before editing. When the selected source is local Markdown, write only inside the user-selected root and preserve its revision/hash.

## Step 5 — Transition

- `READY` + user requested implementation → follow [`execute-ticket`](../execute-ticket/SKILL.md).
- `NEEDS_RESEARCH` → follow [`discover-and-scope`](../discover-and-scope/SKILL.md) in read-only mode.
- `NEEDS_CLARIFICATION` → ask only the decision-changing question and propose the Jira edit.
- `BLOCKED` → report the blocker and safe work still possible; do not invent a workaround.
