---
name: finish-ticket
description: "Prepare the final current-SHA Git handoff, PR/MR evidence, and approved TaskStore update after implementation and independent review pass."
---

# Finish a Jira ticket

## Completion gate

Require:

- current TaskStore contract has no material drift;
- current HEAD equals reviewed PASS SHA;
- all acceptance criteria have evidence;
- required checks passed or approved limitations are explicit;
- all findings have terminal dispositions;
- no accidental or unrelated diff remains;
- rollout, rollback, migration, monitoring, and documentation are addressed or marked `N/A` with a reason.

If any gate fails, return to the owning skill instead of producing a misleading completion report.

## Handoff

Produce a provider-neutral artifact conforming to [`handoff-v2.schema.json`](../../contracts/handoff-v2.schema.json) and the human template [`final-report.md`](../../templates/handoff/final-report.md). Existing Jira v1 work may retain [`handoff.schema.json`](../../contracts/handoff.schema.json).

It includes:

- scope reference, source revision, and contract hash;
- repository/worktree, source/target branch, and full SHA;
- goal and implemented behavior;
- changed components;
- exact verification commands/results;
- review passes and current-SHA result;
- deferred follow-up issues/proposals;
- risks, limitations, and unverified items;
- rollout/rollback/monitoring;
- external actions still requiring user authorization.

## External actions

Preview PR/MR text, TaskStore update, push, or PR/MR creation. Perform only the actions the user authorized. A plugin PASS is not provider approval and does not replace repository-required reviews.

After a push, invalidate local review PASS and require review evidence for the pushed SHA before claiming merge readiness.
