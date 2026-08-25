---
name: discover-and-scope
description: "Research uncertain work before creating or clarifying an Initiative, Epic, Spec, or Task in the selected TaskStore."
---

# Discover and scope work

## Boundary

This workflow is read-only unless the user separately authorizes an isolated spike. Its output is a researched task proposal, not production implementation.

## Research lanes

1. Current user/business flow and expected outcome.
2. Owning repository, modules, runtime entry points, data stores, APIs, queues, and integrations.
3. Existing tests, deployment boundaries, migration constraints, compatibility risks, and observability.
4. Neighboring services and tasks owned by infrastructure, database, frontend, security, or other teams.
5. Existing Initiative, Epic, Specs, Tasks, blockers, and potentially duplicative work in the selected TaskStore.

Independent repository lanes may use parallel read-only explorer agents. Give each a bounded question and require file/line or command evidence.

## Output

Produce a Research Brief containing:

- problem and desired outcome;
- verified current behavior;
- affected components and repositories;
- proposed solution boundary and alternatives;
- risks, unknowns, and decisions;
- proposed artifact kind/type, Epic/Initiative placement, owner/team;
- in-scope and out-of-scope lists;
- acceptance criteria;
- validation plan;
- proposed subtasks and issue links;
- provider-neutral draft plus adapter-specific fields/comments ready for preview.

Follow [`issue-writing.md`](../../references/jira/issue-writing.md), [`hierarchy.md`](../../references/jira/hierarchy.md), and [`link-semantics.md`](../../references/jira/link-semantics.md).

## Creation gate

Show the complete draft and decomposition. Create/update/link remote records only after explicit approval. Do not create tasks for another team without authority; produce a handoff-ready draft instead.

Route the researched result through [`specify`](../specify/SKILL.md), then [`plan-work`](../plan-work/SKILL.md), rather than implementing directly from research notes.
