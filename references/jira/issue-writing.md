# Generic issue writing standard

Every TaskStore record should make these fields understandable to a human:

1. problem and desired outcome;
2. in-scope and out-of-scope behavior;
3. numbered, independently verifiable acceptance criteria;
4. verified technical constraints;
5. dependencies, parent, and provenance links;
6. validation, observability, migration, and rollback evidence;
7. risk and required approvals.

Create a separate Task for a distinct owner, repository, deployment, rollback,
release boundary, or acceptance decision. Use a checklist only when the same owner
can complete the steps inside one delivery unit.
