# Finding protocol

Every finding states:

- unique finding ID;
- ticket and exact full 40- or 64-character reviewed SHA; abbreviated SHAs are invalid evidence;
- severity and scope class;
- narrow code location;
- observable claim;
- evidence or reproduction path;
- expected behavior from the contract/rule;
- smallest safe corrective action;
- whether the current change introduced the issue.

Bad finding:

> This code could be cleaner and might not scale.

Good finding:

> `REV-004`, P2, in scope, reviewed SHA `abc…`: the new retry loop in `worker.py:91` retries non-idempotent POST after a read timeout, so one request can create two records. AC-03 requires single creation. Restrict retries to the idempotency-key path or persist the request key before retrying.

Builder responses preserve the original finding and select one terminal status. Rejection requires evidence; deferral requires a follow-up Jira key before final completion.

Record passes with `scripts/review_ledger.py add-pass --packet <packet.json>`. Do not
supply a desired result: the ledger computes `PASS`, `REQUEST_CHANGES`, or `ESCALATE`
from current-SHA independent verification, Jira revision, contract drift, and finding
dispositions. Check final currency with `check-current` and all four SHA/contract/Jira
arguments.

The packet includes the Jira ticket and a complete
`team-dev-flow/verification-report/v1` object. The ledger validates that object against
Draft 2020-12 and cross-checks its ticket, full SHA, contract hash, and Jira revision.
A two-field `{verified_sha, result}` summary is not verification evidence.

For `needs_evidence`, provide a stable claim and the evidence items considered. The
raw packet is validated before normalization; `evidence` must be an array of non-empty
strings. The ledger normalizes claim and per-item evidence whitespace, then computes
both the disagreement fingerprint and evidence
revision; caller-supplied fingerprints are overwritten. A second occurrence of the
same in-scope P0–P2 fingerprint with the same evidence revision escalates. New evidence
changes the revision and permits another bounded review pass. P3, adjacent, and
out-of-scope suggestions are non-blocking and cannot trigger this early escalation.
