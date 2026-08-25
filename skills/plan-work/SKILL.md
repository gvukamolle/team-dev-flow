---
name: plan-work
description: "Decompose a ready Initiative, Epic, or typed Spec into provider-neutral Tasks with ownership, dependencies, acceptance boundaries, and verification; also roll Tasks upward to expose missing or oversized parent scope."
---

# Plan work from a Spec

## Entry gate

Require a schema-valid Spec in `ready` or `active` state. If acceptance criteria, scope, or decision-changing questions are unresolved, return to [`specify`](../specify/SKILL.md).

## Decompose downward

Create separate Tasks when ownership, repository, release lifecycle, risk, or acceptance boundary differs. Create subtasks only when the same owner and delivery unit benefit from independently tracked steps.

Every proposed Task includes:

- provider-neutral scope reference or a draft reference;
- parent Spec/Epic reference;
- goal and explicit non-goals;
- owned repository/component;
- dependencies and blockers;
- acceptance criteria mapped back to parent criteria;
- design decisions mapped back through `DES-*` references;
- validation, rollout, rollback, and approval boundaries.

## Validate upward

After decomposition, verify that:

- every parent acceptance criterion has an owning Task or explicit non-code evidence;
- every design decision needed for implementation has an owning Task;
- no Task exists only because of incidental implementation detail;
- combined Tasks do not silently broaden the parent outcome;
- an oversized Task is promoted into a child Spec rather than hidden in a checklist;
- missing shared work is raised to the Epic/Initiative instead of duplicated.

## Publish through an adapter

Render the same plan for the selected TaskStore: Jira, GitHub Issues, GitLab Issues, local Markdown/Obsidian, Notion, or a custom adapter. Preview all remote writes and require the provider's authority boundary. Local files are not automatically authoritative unless the active Task Contract selects them as its source.

Run the consistency gate before implementation. If scope grows, create a preview promotion plan (`Task → Spec → Epic → Initiative`) that preserves the native ID/ref and appends a history event; never silently replace the work item. Parent projections keep `status`, `health`, and `stage` separate and calculate completion from required children only.

Once one Task is selected, route to [`start-work`](../start-work/SKILL.md). After implementation, verification, and review, Converge either confirms the exact Spec/Task coverage at the current SHA or appends concrete remaining Tasks.
