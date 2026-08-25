# Branch policy

The active repository policy is authoritative. Discover its default branch,
integration branch, protection rules, and naming convention before creating or
changing branches. Do not assume `main`, `master`, `dev`, or a ticket-key format.

## Normal work

Use one bounded implementation branch for one accepted Task or Spec when the
repository requires branches. A branch may contain task-required code, tests,
documentation, and migrations; it must not contain unrelated cleanup.

Before branching:

- identify existing dirty work and preserve it;
- refresh the configured base branch using the repository's safe update policy;
- derive the branch name from the selected profile or repository convention;
- record the accepted scope and base SHA.

## Release and hotfix

Follow the repository's declared release and hotfix topology. Branch names and
deployment labels are intent, not proof of the deployed commit. Verification
and review evidence remain bound to the exact full SHA.

## Prohibited by default

- destructive reset of user work;
- direct or force push to a protected branch;
- inventing a branch convention when none has been configured;
- mixing unrelated work into the implementation branch;
- merging an old reviewed SHA after a new push.
