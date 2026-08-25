# Review severity

## P0 — catastrophic

Immediate credible risk of mass data loss/exposure, privilege compromise, broad production outage, or irreversible corruption. Requires stopping the workflow and human/security/incident ownership.

## P1 — serious

High-impact correctness, security, privacy, availability, or compatibility failure likely to affect important users or systems. Blocking.

## P2 — bounded defect

Reproducible acceptance failure, regression, missing required error handling, or meaningful test gap that should be fixed before merge. Blocking when in scope.

## P3 — non-blocking

Maintainability, clarity, minor performance, or polish improvement without a current correctness/contract failure. Record only when useful; do not manufacture P3 findings.

Severity describes impact and likelihood, not reviewer confidence or effort to fix.

