# Commit policy

- Stage files deliberately by logical purpose; do not use `git add .` blindly.
- Keep commits cohesive and reviewable.
- Include the Jira key in the subject when team Git conventions require it.
- Do not mix formatting, generated assets, refactors, and behavior unless inseparable.
- Never commit local config, tokens, certificates, production data, raw logs, or agent scratch state.
- Do not amend, rebase shared work, or force-push without explicit authorization.
- A commit message states the behavior/intent, not that an agent performed the change.

Before commit, inspect staged diff and run relevant validation plus `git diff --check`.

