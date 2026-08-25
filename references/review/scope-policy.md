# Review scope policy

## In scope

A finding is `in_scope` when it demonstrates:

- an acceptance criterion is not met;
- the diff introduces a regression or unsafe behavior;
- a required repository rule is violated;
- task-required tests, docs, migration, rollback, or observability are missing;
- an accidental unrelated change is present in the branch.

## Adjacent

A finding is `adjacent` when it concerns nearby code or a worthwhile hardening opportunity but the current change neither requires nor creates it.

## Out of scope

A finding is `out_of_scope` when it concerns a separate product capability, pre-existing independent defect, optional redesign, broad refactor, or another team's work.

## Blocking rule

Only in-scope P0–P2 findings normally block. An adjacent/out-of-scope issue blocks only if the current diff directly creates an immediate critical risk; the finding must show that causal link.

Valid non-current work is not ignored. It is captured as a follow-up proposal without expanding the current branch.

