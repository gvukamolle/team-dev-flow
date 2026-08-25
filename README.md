# Team Dev Flow

Team Dev Flow is a universal Agentic Spec-Driven Development plugin for Codex,
Kilo Code, and AGENTS.md-compatible coding agents.

It provides one lifecycle across agent hosts, TaskStores, and Git providers:

```text
Initiative → Epic → Quick/Feature/Bugfix/Research/Refactor Spec → Task
Capture → Clarify/Research → Specify → Plan → Implement → Verify → Review → Converge → Handoff
```

## Included profiles

- `generic`: discovery, specification, planning, and local Git without a remote tracker;
- `obsidian-local`: writable Local Markdown/Obsidian TaskStore plus local Git;
- `kilo-github`: Kilo Code, bounded GitHub Issue reads, and non-authorizing Issue/PR previews.

The Universal package contains no organization-specific Jira profile, internal
URL, task identifier, credential setup, or corporate release rule.

## Install in Codex

```bash
codex plugin marketplace add https://github.com/gvukamolle/team-dev-flow-marketplace.git --ref FULL_MARKETPLACE_SHA --json
codex plugin add team-dev-flow@team-flow --json
```

Restart Codex and open a new task after installation.

## Install in Kilo Code

From a reviewed checkout:

```bash
python3 scripts/host_package.py preview --host kilo --workspace /path/to/project
python3 scripts/host_package.py install --host kilo --workspace /path/to/project
python3 scripts/host_package.py check --host kilo --workspace /path/to/project
```

Run `/reload`, select the `team-dev-flow` agent, and start from a local Task or
GitHub Issue.

## Local Markdown / Obsidian

```bash
python3 scripts/local_task_store.py init --vault "/path/to/vault" --folder "Projects/Team Dev Flow"
python3 scripts/local_task_store.py upsert --root "/path/to/vault/Projects/Team Dev Flow" --project FLOW --kind project --id FLOW --title "Team Dev Flow"
```

The adapter creates stable Project/Initiative/Epic/Spec/Task notes and a native
`Dashboard.base`. It does not edit `.obsidian`, follows no symlinks, preserves
user text/properties, and couples atomic note changes with redacted history.

## GitHub boundary

`scripts/github_adapter.py` reads one bounded Issue and renders exact argv/stdin
previews for Issue or PR creation. It exposes no apply command. A PR preview is
bound to the full current commit SHA. Preview is never authorization.

## Development

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
PATH="$PWD/.venv/bin:$PATH" npm test
.venv/bin/python scripts/validate_repository.py
.venv/bin/python scripts/package_release.py
.venv/bin/python scripts/verify_package.py
```

Licensed under Apache-2.0.
