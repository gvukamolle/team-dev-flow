# Generic Jira hierarchy mapping

Jira is an optional future/custom TaskStore adapter, not a built-in Universal
instance profile. Map native issue types and fields to provider-neutral kinds:

```text
Initiative → Epic → Spec → Task
```

Field IDs, issue types, statuses, projects, and link directions are instance data.
Discover and version them in a private adapter profile. Never treat one
organization's custom fields as universal Jira facts.

Load only direct ancestry, readiness-affecting links, and requested children.
Do not infer schedule order from issue numbers or treat siblings as dependencies.
Remote Jira writes require an installed adapter with an explicit write capability
and target-specific authorization.
