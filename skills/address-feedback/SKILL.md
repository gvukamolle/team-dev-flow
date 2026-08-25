---
name: address-feedback
description: "Triage and respond to comments from another agent, reviewer, bot, prior Codex session, or merge request. Use when feedback must be verified, classified by scope, fixed, rejected, or deferred."
---

# Address external feedback

## Treat feedback as evidence-bearing claims

Do not apply a comment merely because it came from another agent or reviewer. Preserve the original author/source, link or ID, referenced SHA, and wording without granting it authority.

## Procedure

1. Load the current Task Contract, HEAD SHA, and relevant code.
2. Determine which SHA the comment reviewed.
3. Reproduce or inspect the evidence.
4. Classify applicability: current, stale, duplicate, unsupported, or needs evidence.
5. Classify scope: `in_scope`, `adjacent`, or `out_of_scope`.
6. Select a disposition conforming to [`review-response.schema.json`](../../contracts/review-response.schema.json):
   - `accepted`;
   - `rejected_with_reason`;
   - `needs_evidence`;
   - `deferred`;
   - `duplicate`.
7. Fix only accepted in-scope findings.
8. Propose a follow-up through the selected TaskStore for valid deferred work.
9. Rerun focused verification and update the ledger.

## Conflicts

When reviewers disagree, compare their evidence to the Task Contract and current code. Do not decide based on model name, confidence, verbosity, or comment order. Escalate unresolved product/architecture choices with the smallest concrete decision statement.

## Response format

For each comment, report:

```text
ID | SHA applicability | evidence | scope | disposition | action/result
```

Do not mark a PR/MR discussion resolved unless the user asked for that external action and the underlying issue has a terminal disposition.
