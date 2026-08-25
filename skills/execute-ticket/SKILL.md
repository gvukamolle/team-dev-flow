---
name: execute-ticket
description: "Implement an accepted provider-neutral Task Contract in a bounded branch after start-work returns READY."
---

# Execute a Task Contract

## Entry gate

Require:

- a schema-valid Task Contract;
- source revision and contract hash;
- correct repository and target branch;
- known dirty-work ownership;
- no unresolved blocker;
- user authority for implementation edits.

If any condition is missing, return to `start-work`.

## Plan

Create an implementation plan mapped to acceptance criteria. Each step states:

- files/components expected to change;
- behavior delivered;
- test/evidence produced;
- dependencies on earlier steps;
- whether it can run independently.

Do not create plan items for non-goals or unrelated cleanup.

## Builder role

Use one builder owner for implementation files. If multiple workers are justified, give them non-overlapping file/module ownership and state that they must preserve other work. Do not parallelize tightly coupled edits merely to use more agents.

The builder must follow [`builder.md`](../../roles/builder.md), applicable `AGENTS.md`, and the Task Contract.

## Implementation rules

1. Make the smallest coherent change.
2. Preserve public and cross-service compatibility unless the contract explicitly changes it.
3. Add tests alongside behavior.
4. Do not hide failures with ignores, broad exception swallowing, disabled checks, stubs, or fake assertions.
5. Update contracts, docs, migrations, and observability when the behavior requires it.
6. Stop on material scope discovery. Draft a clarification/follow-up through the selected TaskStore adapter instead of broadening the branch.

## Verification

After every new implementation code state, stop Builder activity and invoke the independent read-only Verifier role from [`verifier.md`](../../roles/verifier.md). Give it the Task Contract, source revision, exact full HEAD SHA, applicable `AGENTS.md`, changed diff, and required checks. Do not let Builder impersonate Verifier or author the final verification verdict.

Require the Verifier to run focused tests first, then broader checks, and produce a schema-valid provider-neutral [`verification-report-v2.schema.json`](../../contracts/verification-report-v2.schema.json). Existing Jira v1 contracts may retain [`verification-report.schema.json`](../../contracts/verification-report.schema.json). Require:

- `independent_from_builder = true`;
- the same contract hash and source revision as the active Task Contract;
- `verified_sha` equal to the exact current full HEAD SHA;
- at least one concrete check;
- explicit `unverified` entries;
- `PASS`, `FAIL`, or `INCOMPLETE` computed from actual evidence.

Return `FAIL` or required-check `INCOMPLETE` to Builder for a bounded fix. Any Builder edit creates a new code state and invalidates the old verification report; invoke Verifier again before review.

Always inspect the final diff and `git diff --check`. State checks not run and why.

## Transition

Enter [`review-loop`](../review-loop/SKILL.md) only with a schema-valid independent Verifier report whose SHA equals current HEAD and whose result satisfies the Task Contract. Do not call the task complete from builder self-review alone.
