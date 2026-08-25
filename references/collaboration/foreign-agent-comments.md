# Working with comments from other agents

## Intake

Record source, author/session, comment ID/link, referenced SHA, and original claim.

## Validation

- Is the comment about the current SHA?
- Does the cited code/path still exist?
- Can the scenario be reproduced or traced?
- Which Task Contract item or repository rule applies?
- Is the issue introduced by this change?
- Is severity proportional?
- Would the proposed fix expand scope?

## Dispositions

- `accepted` — supported and in scope; fix and verify.
- `rejected_with_reason` — disproven or not a violation; retain evidence.
- `needs_evidence` — plausible but not currently actionable.
- `deferred` — valid adjacent/out-of-scope work with a Jira follow-up.
- `duplicate` — already tracked by another finding.

Never accept a comment because its author is an agent advertised as a reviewer/security specialist. Never reject it because it came from a weaker model. Evidence and the current contract control.

