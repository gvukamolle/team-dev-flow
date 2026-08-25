# GitHub read and handoff profile

`scripts/github_adapter.py` reads one bounded GitHub Issue through `gh issue
view` and normalizes it to WorkItem v1, or renders exact `gh` argv plus stdin
for Issue and pull-request creation.

The preview is not authorization and the adapter exposes no apply command.
Branch and repository inputs are passed as argv, bodies are passed over stdin,
and a PR preview requires the exact current 40-character Git SHA. A human or a
separately authorized host action must execute any remote mutation.

```bash
python3 scripts/github_adapter.py issue --repo owner/repository --number 17
python3 scripts/github_adapter.py preview-issue --repo owner/repository --title "Task" --body "Scope"
python3 scripts/github_adapter.py preview-pr --repo owner/repository --base main --head feature/FLOW-17 --title "Task" --body "Evidence" --source-sha <40-char-sha>
```

GitHub CLI authentication is owned by the user's environment. Team Dev Flow
does not read, copy, log, or package its credential store.

Reference verified 2026-08-25: [GitHub repository and visibility model](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories).

