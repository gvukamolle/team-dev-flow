# Kilo Code profile

Team Dev Flow uses Kilo's current project-local Markdown surfaces: agents in
`.kilo/agents/`, rules in `.kilo/rules/`, skills in `.kilo/skills/`, and the
repository `AGENTS.md`. The host overlay is deliberately thin; canonical flow
logic stays in the installed plugin copy.

Install or verify it from a reviewed Team Dev Flow checkout:

```bash
python3 scripts/host_package.py preview --host kilo --workspace /path/to/project
python3 scripts/host_package.py install --host kilo --workspace /path/to/project
python3 scripts/host_package.py check --host kilo --workspace /path/to/project
```

Restart the Kilo session or run `/reload`, select `team-dev-flow`, then start
from a local task reference or a GitHub issue. The installer is project-local,
transactional, refuses symlinks and unowned collisions, and records SHA-256 for
every managed file. It never changes Kilo credentials or global auto-approval.

References verified 2026-08-25:

- [Kilo customization](https://kilo.ai/docs/customize)
- [Custom agents](https://kilo.ai/docs/customize/custom-modes)
- [Project rules](https://kilo.ai/docs/customize/custom-rules)
- [Skills and reload behavior](https://kilo.ai/docs/customize/skills)

