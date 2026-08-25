# Team constitution

These principles govern every Team Dev Flow workflow.

1. **Public scope before code.** Jira records what the team agreed to deliver.
2. **One implementation task, branch, and feature MR.** Release and hotfix synchronization are explicit exceptions.
3. **Responsibility stays human.** Agents research, build, test, and review; humans own requirements, architecture, approval, release, and consequences.
4. **Evidence over confidence.** Claims name the source, command, environment, and exact SHA.
5. **Current state over stale context.** Live Jira, current code, active config, and current MR head outrank old chats or cached summaries.
6. **Independent review.** Builder self-review does not count as independent review. Reviewer PASS is SHA-bound.
7. **Scope restraint.** Valid future work is captured without silently expanding the current branch.
8. **Preserve user work.** Dirty changes and external edits are never discarded or overwritten casually.
9. **Secrets and personal data stay out.** Credentials and raw sensitive data do not enter prompts, plugin files, docs, fixtures, logs, or MR comments.
10. **Automation cannot grant itself authority.** Jira writes, push, merge, release, deploy, and infrastructure actions follow explicit boundaries.
11. **Mechanical gates are deterministic.** CI, scripts, schemas, and branch protection enforce what prose alone cannot.
12. **Improve from evidence.** Repeated review feedback becomes a scoped rule and eval only after examples prove it is consequential and not noisy.

