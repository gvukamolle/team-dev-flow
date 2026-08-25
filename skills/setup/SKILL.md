---
name: setup
description: "Install, validate, diagnose, or explain the Universal Team Dev Flow plugin for Codex, Kilo Code, GitHub, or Local Markdown/Obsidian."
---

# Setup Universal Team Dev Flow

## Codex

1. Add the reviewed GitHub marketplace and install `team-dev-flow@team-flow`.
2. Restart Codex and open a new task.
3. Confirm the installed version and available skills.
4. Select one FlowProfile before task work.

Do not request a tracker credential unless the selected adapter genuinely needs
one. This Universal package contains no organization-specific credential wizard.

## Kilo Code

From a reviewed plugin checkout, preview and install the project-local package:

```bash
python3 scripts/host_package.py preview --host kilo --workspace /path/to/project
python3 scripts/host_package.py install --host kilo --workspace /path/to/project
python3 scripts/host_package.py check --host kilo --workspace /path/to/project
```

Run `/reload` and select `team-dev-flow`. Never change global model credentials or
auto-approval as part of setup.

## Local Markdown / Obsidian

Initialize only the user-selected vault-relative folder. The adapter does not
change `.obsidian`. Show a preview before the first write.

## GitHub

GitHub CLI authentication is external to the plugin. `github_adapter.py` supports
bounded Issue reads and non-authorizing Issue/PR previews only. Do not claim that
a preview executed a remote action.

## Diagnosis

Run `python3 scripts/validate_repository.py`, `python3 scripts/host_package.py
check` for Kilo, and the relevant adapter unit tests. Report exact failures without
printing credentials or raw authenticated stderr.
