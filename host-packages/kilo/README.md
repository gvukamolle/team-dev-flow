# Kilo Code host package

The current Kilo Code extension/CLI uses Markdown agents under `.kilo/agents/`, project rules under `.kilo/rules/`, project skills under `.kilo/skills/`, and automatically loads `AGENTS.md`. Team Dev Flow installs one thin Kilo wrapper plus a complete isolated copy of the canonical plugin under `.team-dev-flow/plugin/`; it does not maintain a second workflow implementation.

```bash
python3 scripts/host_package.py preview --host kilo --workspace /path/to/project
python3 scripts/host_package.py install --host kilo --workspace /path/to/project
python3 scripts/host_package.py check --host kilo --workspace /path/to/project
```

Start a new Kilo session or run `/reload`, select the `team-dev-flow` agent, and ask `Start local task FLOW/TASK-1` or `Start GitHub issue owner/repo#17`.

Installation is project-local, transactional, and hash-inventoried. It refuses symlinks, unowned collisions, and modified previously installed files. A failed update rolls back every replaced file. It never modifies global Kilo configuration, model/provider credentials, or auto-approval settings.
