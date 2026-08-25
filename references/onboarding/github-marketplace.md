# GitHub marketplace publication

Generate the separate repository only from a reviewed release SHA and archive
digest. Private + `UNLICENSED` is valid for a personal catalog; public publication
requires an explicit distribution license.

```bash
python3 scripts/github_marketplace.py generate \
  --root /path/to/team-dev-flow-marketplace \
  --owner OWNER --plugin-repo team-dev-flow --marketplace-name team-flow \
  --version VERSION --git-ref FULL_40_CHAR_SHA \
  --artifact-sha256 RELEASE_SHA256 --visibility private --license UNLICENSED
python3 scripts/github_marketplace.py verify --root /path/to/team-dev-flow-marketplace
```

Promotion copies the tested canary pointer to stable; rollback swaps stable with
its previous immutable pointer. Commit and review each state change. Creating a
GitHub repository, choosing visibility/license, granting collaborators, pushing,
and changing visibility are separate remote actions.

```bash
python3 scripts/github_marketplace.py promote --root /path/to/team-dev-flow-marketplace
python3 scripts/github_marketplace.py rollback --root /path/to/team-dev-flow-marketplace
```

Codex install after publication:

```bash
codex plugin marketplace add https://github.com/OWNER/team-dev-flow-marketplace.git --ref FULL_MARKETPLACE_SHA --json
codex plugin add team-dev-flow@team-flow --json
```

Kilo users do not consume the Codex catalog directly. They clone a reviewed plugin
release and run the project-local `host_package.py install` command documented in
`references/hosts/kilo-code.md`.
