# Jira task readiness

## READY

Use when all are true:

- the problem/outcome is understandable;
- acceptance criteria are testable;
- in-scope and non-goals are explicit or safely inferable;
- owner/repository are known;
- blocking dependencies are satisfied or intentionally outside execution;
- risk and required validation are known;
- no Jira/code contradiction materially changes the solution.

## NEEDS_CLARIFICATION

Use when a human/product decision is missing, for example:

- two plausible behaviors produce different user outcomes;
- acceptance criteria contradict each other;
- compatibility or migration policy is not decided;
- the issue asks for implementation while the actual product expectation is unclear.

Ask the smallest decision-changing question and draft the Jira wording that would resolve it.

## NEEDS_RESEARCH

Use when the business goal is understandable but technical impact is not, for example:

- affected repositories/services are unknown;
- the change may require another team's work;
- current behavior or runtime contract is unverified;
- task size/decomposition cannot be estimated responsibly.

Research is read-only and must end in a Jira-ready proposal.

## BLOCKED

Use when useful progress cannot continue because of:

- missing Jira/repository/access;
- unresolved blocking issue link;
- required external decision or artifact unavailable;
- TLS/authentication failure;
- user-owned overlapping changes that cannot be preserved safely.

Name the blocker, evidence, owner if known, and safe remaining work.

