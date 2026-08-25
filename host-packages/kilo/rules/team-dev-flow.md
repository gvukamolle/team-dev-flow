# Team Dev Flow workspace rule

When a request names Team Dev Flow, a work-item reference, a specification, task planning, implementation review, or Git handoff, load the `team-dev-flow` skill.

- Use the repository `AGENTS.md` when present; Kilo Code loads that standard automatically.
- Select exactly one TaskStore through a FlowProfile.
- Do not edit before a Task Contract exists.
- Preserve user-owned work and refuse ambiguous overlapping changes.
- Re-run verification and review after every new commit or push because prior SHA evidence is stale.
- GitHub/Jira mutation output from this package is a preview for human application, never write authority.
