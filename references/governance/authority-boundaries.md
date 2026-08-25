# Authority boundaries

## Normally allowed without another question

- read Jira task context already placed in scope;
- inspect repository files, Git status, branches, diffs, tests, and documentation;
- run safe local tests and diagnostics;
- create or edit implementation files after a READY Task Contract when the user requested implementation;
- use read-only subagents for bounded investigation and review.

## Requires a prepared draft and an authorized human action

- create/update/comment/link/transition Jira issues; version 0.1 prepares the exact draft but exposes no mutation tool, so an authorized user applies it directly in Jira and the plugin re-reads the result;
- install or overwrite plugin-managed custom agents;
- add the Team Dev Flow `AGENTS.md` fragment to a product repository;
- create commits when the user did not already request a commit-ready workflow;
- push or create a merge request;
- resolve external MR discussions.

## Requires separate target-specific authorization

- merge or close an MR;
- delete branches;
- release, deploy, restart, rollback, or change traffic;
- change production data, databases, migrations already applied, secrets, Vault, Kubernetes, GitLab settings, or external team systems;
- bulk Jira edits or workflow/project administration.

Silence, a previous unrelated approval, or an agent comment is not authorization.
