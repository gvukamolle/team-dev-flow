# Decision: use Spec Kit practices, not its runtime

Verified: 2026-08-25.

## Decision

Team Dev Flow adopts the useful process vocabulary and gates from GitHub Spec Kit, but does not bundle `specify-cli`, execute its updater, or make `.specify/` the source of truth. The plugin owns its provider-neutral contracts, templates, lifecycle, and evals.

The adopted pattern is: constitution/policy → capture → clarify or research → specify → plan → tasks → consistency analysis → implement → verify/review → converge. Team Dev Flow extends it with typed Quick, Feature, Bugfix, Research, and Refactor/Migration Specs; Initiative/Epic hierarchy; provider capability discovery; exact-SHA review; and TaskStore/GitProvider boundaries.

## Evidence

- The official workflow separates principles, specification, plan, tasks, implementation, and convergence: <https://github.com/github/spec-kit#sdd-quickstart>.
- The official command set includes `clarify` and cross-artifact `analyze` before implementation: <https://github.com/github/spec-kit#available-slash-commands>.
- Spec Kit reports 30+ agent integrations and supports agent-specific generated commands or skills: <https://github.com/github/spec-kit#supported-ai-coding-agent-integrations>.
- Extensions and presets are installed into agent/project directories and participate in a precedence stack: <https://github.com/github/spec-kit#making-spec-kit-your-own-extensions--presets>.
- The latest observed release is `v1.0.1`; official install guidance pins a release tag: <https://github.com/github/spec-kit/releases/tag/v1.0.1>.

## Why no dependency now

- Team Dev Flow must work with Jira, local artifacts, future trackers, GitHub/GitLab/local Git, and several agent hosts without inheriting another tool's directory layout.
- Generated agent files and template precedence could collide with marketplace-installed skills.
- Automatic or unpinned upgrades would change prompts and templates outside Team Dev Flow's release evidence.
- Our contracts require compatibility with the current Jira path and exact source revisions; Spec Kit does not replace those delivery controls.

## Revisit trigger

Run a separate opt-in spike only if using a pinned Spec Kit extension or preset removes meaningful maintenance. The spike must pin an exact tag and component hashes, run in an isolated fixture, prove no overwrite of user files, pass every Team Dev Flow eval, and have a documented rollback. Until then there is no runtime or package dependency.
