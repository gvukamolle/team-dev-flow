---
name: review-loop
description: "Run independent, SHA-bound code review and bounded builder-reviewer iterations against a provider-neutral Task Contract."
---

# Independent review loop

Read [`scope-policy.md`](../../references/review/scope-policy.md), [`severity.md`](../../references/review/severity.md), [`finding-protocol.md`](../../references/review/finding-protocol.md), and [`stop-conditions.md`](../../references/review/stop-conditions.md) before reviewing.

## Review packet

Require:

- Task Contract and contract hash;
- source revision and drift check;
- source and target branch;
- base SHA and exact reviewed HEAD SHA;
- diff and applicable `AGENTS.md` rules;
- schema-valid independent Verifier report for the exact reviewed SHA;
- prior review ledger, if any.

Do not review an unspecified local branch as if it were the MR head.

Reject the packet before Reviewer invocation when the verification report was produced by Builder, has `independent_from_builder != true`, names another SHA/contract/source revision, omits required checks, or is `FAIL`. Treat an `INCOMPLETE` required check according to the explicit exception rules in the Task Contract; never silently convert it to `PASS`.

## Independent first pass

Spawn a reviewer role in read-only mode. Give it the factual review packet and [`reviewer.md`](../../roles/reviewer.md). Withhold persuasive builder narrative on the first pass.

The reviewer prioritizes consequential, reproducible problems. Style-only and future-improvement comments are non-blocking unless repository rules make them part of the contract.

## Finding validation

Validate each finding against [`review-finding.schema.json`](../../contracts/review-finding.schema.json). Reject malformed or evidence-free comments from the blocking set.

For each valid finding, confirm:

- the cited code exists at reviewed SHA;
- the scenario is reachable or contractually relevant;
- severity matches impact;
- scope is `in_scope`, `adjacent`, or `out_of_scope`;
- proposed action is safe and does not unnecessarily expand work.

## Builder response

Return accepted in-scope findings to the builder. Every response conforms to [`review-response.schema.json`](../../contracts/review-response.schema.json).

Adjacent/out-of-scope work is deferred with a TaskStore follow-up reference unless the current diff directly creates a critical risk.

## Re-review

After changes:

1. invoke the independent Verifier again and require a new schema-valid report;
2. capture the new SHA;
3. mark prior PASS invalid;
4. review the delta and re-evaluate affected full behavior;
5. preserve finding history and dispositions.

The executable loop is therefore always `Builder → independent Verifier → independent Reviewer`. Reviewer never receives a code state that has only Builder self-review.

## Stop

Stop with `PASS`, `REQUEST_CHANGES`, or `ESCALATE`. Never report PASS for a different SHA than current HEAD. Stop after five passes or two repeated evidence-free in-scope P0–P2 disagreements and ask the task owner to decide. P3, adjacent, and out-of-scope suggestions never trigger this early stop.
