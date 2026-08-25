---
name: specify
description: "Create or refine a right-sized Agentic SDD artifact for an Initiative, Epic, feature, bugfix, research question, quick change, or refactor/migration before implementation planning."
---

# Specify work

Turn an idea or existing work item into the smallest specification that removes decision-changing ambiguity. Do not inflate a small change into a product brief.

## Choose the artifact

- `initiative` — a multi-outcome direction spanning several Epics.
- `epic` — one major outcome containing several Specs or independently releasable Tasks.
- `quick` — a bounded, low-risk change with obvious behavior and verification.
- `feature` — new user/system behavior with journeys, edge cases, rollout, and observable acceptance.
- `bugfix` — observed versus expected behavior, reproduction evidence, impact, and regression proof.
- `research` — a decision to make, evidence to collect, options, and an explicit exit criterion.
- `refactor_migration` — behavior-preserving target state, invariants, compatibility, migration, and rollback.

Use the matching template under [`templates/specs`](../../templates/specs/) and the machine contract [`spec.schema.json`](../../contracts/spec.schema.json).

The lifecycle is `Capture → Clarify/Research → Specify → Plan → Tasks → Implement → Verify → Review → Converge`. Capture may remain a plain request; the first authoritative artifact starts at Specify unless the active TaskStore provides a draft identity.

## Evidence and questions

1. Read the current source record through the available provider adapter.
2. Inspect repository/runtime evidence relevant to the decision.
3. Separate verified facts, assumptions, risks, and open questions.
4. Ask only questions whose answers change behavior, scope, risk, or external state.
5. Link the artifact upward to an Epic/Initiative when known; never invent a parent.

## Readiness gate

A Spec can move to `ready` only when scope is non-empty, acceptance criteria are verifiable, and blocking open questions are empty. Before `active`, every acceptance criterion and design decision must map to a Task. A Research Spec may contain only research/verification Tasks; production work requires a new decision and Spec. Use `scripts/spec_flow.py` for mechanical transition checks.

Then route to [`plan-work`](../plan-work/SKILL.md). Research Specs execute evidence collection before implementation decomposition.
