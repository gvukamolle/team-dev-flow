# Review stop conditions

## PASS

- current Jira contract is unchanged;
- full reviewed SHA equals current HEAD/MR head;
- schema-valid independent Verifier report is `PASS` for that same SHA, contract hash, and Jira revision;
- no unresolved in-scope P0–P2 finding;
- acceptance criteria have evidence;
- required checks pass or an allowed exception is explicit;
- all findings have terminal dispositions;
- review pass count is at most five.

## REQUEST_CHANGES

Use when one or more evidence-backed in-scope P0–P2 findings remain or required verification failed.

## ESCALATE

Use when:

- product/architecture choice cannot be resolved from the contract;
- the same in-scope P0–P2 disagreement repeats twice without new evidence;
- five passes are reached;
- required external approval or system access is missing;
- fixing the issue would materially expand Jira scope.

Do not continue changing code after escalation until the owner decides.

“Same disagreement” is not a caller-supplied boolean. The ledger hashes the normalized
claim and separately hashes its sorted evidence set after normalizing whitespace in
each evidence item. The first blocking occurrence is
`REQUEST_CHANGES`; a second matching identity and evidence revision is `ESCALATE`.
If evidence changed, the new revision does not trigger this early stop. Independently,
an unresolved fifth pass always escalates. P3, adjacent, and out-of-scope suggestions
never trigger repeated-disagreement escalation.
