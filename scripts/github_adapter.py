#!/usr/bin/env python3
"""Read GitHub Issues and render non-authorizing gh mutation previews."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from typing import Callable


REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
FULL_SHA = re.compile(r"^[a-f0-9]{40}$")
MAX_BODY = 100_000


class GitHubAdapterError(RuntimeError):
    pass


def validate_repository(repository: str) -> str:
    if not REPOSITORY.fullmatch(repository or "") or ".." in repository:
        raise GitHubAdapterError("repository must use owner/name with safe GitHub characters")
    return repository


def _run_json(argv: list[str], runner: Callable = subprocess.run) -> dict:
    try:
        result = runner(argv, text=True, encoding="utf-8", capture_output=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired, UnicodeDecodeError) as exc:
        raise GitHubAdapterError(f"GitHub CLI failed: {type(exc).__name__}") from exc
    if result.returncode != 0:
        raise GitHubAdapterError("GitHub CLI request failed; run `gh auth status` locally for details")
    if len(result.stdout.encode()) > 1_000_000:
        raise GitHubAdapterError("GitHub CLI response exceeds 1 MB")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GitHubAdapterError("GitHub CLI returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise GitHubAdapterError("GitHub CLI returned an unexpected payload")
    return value


def normalize_issue(repository: str, value: dict) -> dict:
    number = value.get("number")
    if not isinstance(number, int) or number < 1:
        raise GitHubAdapterError("GitHub issue number is missing")
    body = value.get("body") or ""
    encoded_body = body.encode("utf-8")
    truncated = len(encoded_body) > MAX_BODY
    if truncated:
        body = encoded_body[:MAX_BODY].decode("utf-8", errors="ignore") + "\n[truncated by Team Dev Flow]"
    state = str(value.get("state") or "UNKNOWN").upper()
    status_category = "done" if state == "CLOSED" else "backlog" if state == "OPEN" else "unknown"
    return {
        "schema_version": "team-dev-flow/work-item/v1",
        "ref": f"github:{repository}:{number}",
        "source": {"provider": "github", "instance": repository, "native_id": str(number), "url": value.get("url")},
        "kind": "task",
        "title": str(value.get("title") or ""),
        "body": body,
        "status": {"name": state, "category": status_category},
        "resolution": "completed" if state == "CLOSED" else None,
        "parent_ref": None,
        "labels": sorted(str(label.get("name")) for label in value.get("labels", []) if isinstance(label, dict) and label.get("name")),
        "relations": [],
        "metadata": {
            "assignees": sorted(str(item.get("login")) for item in value.get("assignees", []) if isinstance(item, dict) and item.get("login")),
            "milestone": value.get("milestone", {}).get("title") if isinstance(value.get("milestone"), dict) else None,
            "updated_at": value.get("updatedAt"),
            "body_truncated": truncated,
        },
    }


def read_issue(repository: str, number: int, runner: Callable = subprocess.run) -> dict:
    validate_repository(repository)
    if number < 1:
        raise GitHubAdapterError("issue number must be positive")
    value = _run_json([
        "gh", "issue", "view", str(number), "--repo", repository,
        "--json", "number,title,body,state,labels,assignees,milestone,url,updatedAt",
    ], runner)
    return normalize_issue(repository, value)


def _preview(action: str, repository: str, argv: list[str], stdin: str | None, source_sha: str | None = None) -> dict:
    validate_repository(repository)
    if source_sha is not None and not FULL_SHA.fullmatch(source_sha):
        raise GitHubAdapterError("source SHA must be the full 40-character lowercase commit SHA")
    return {
        "schema_version": "team-dev-flow/external-mutation-preview/v1",
        "provider": "github",
        "action": action,
        "repository": repository,
        "argv": argv,
        "stdin": stdin,
        "source_sha": source_sha,
        "mutation_available": False,
        "confirmation_required": True,
    }


def preview_issue(repository: str, title: str, body: str) -> dict:
    if not title.strip() or len(title) > 256:
        raise GitHubAdapterError("issue title must contain 1-256 characters")
    if len(body.encode()) > MAX_BODY:
        raise GitHubAdapterError("issue body exceeds 100 KB")
    return _preview(
        "create_issue", repository,
        ["gh", "issue", "create", "--repo", repository, "--title", title.strip(), "--body-file", "-"],
        body,
    )


def preview_pull_request(repository: str, base: str, head: str, title: str, body: str, source_sha: str, actual_sha: str) -> dict:
    if not FULL_SHA.fullmatch(actual_sha or "") or source_sha != actual_sha:
        raise GitHubAdapterError("current HEAD does not match the exact source SHA")
    for value, label in ((base, "base"), (head, "head")):
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", value or "") or ".." in value:
            raise GitHubAdapterError(f"invalid {label} branch")
    if not title.strip() or len(title) > 256 or len(body.encode()) > MAX_BODY:
        raise GitHubAdapterError("invalid PR title or body")
    return _preview(
        "create_pull_request", repository,
        ["gh", "pr", "create", "--repo", repository, "--base", base, "--head", head, "--title", title.strip(), "--body-file", "-"],
        body, source_sha,
    )


def current_sha() -> str:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], text=True, encoding="utf-8", capture_output=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired, UnicodeDecodeError) as exc:
        raise GitHubAdapterError(f"Git failed: {type(exc).__name__}") from exc
    sha = result.stdout.strip() if result.returncode == 0 else ""
    if not FULL_SHA.fullmatch(sha):
        raise GitHubAdapterError("unable to resolve the current full Git SHA")
    return sha


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    issue = subparsers.add_parser("issue")
    issue.add_argument("--repo", required=True)
    issue.add_argument("--number", type=int, required=True)
    issue_preview = subparsers.add_parser("preview-issue")
    issue_preview.add_argument("--repo", required=True)
    issue_preview.add_argument("--title", required=True)
    issue_preview.add_argument("--body", required=True)
    pr = subparsers.add_parser("preview-pr")
    pr.add_argument("--repo", required=True)
    pr.add_argument("--base", required=True)
    pr.add_argument("--head", required=True)
    pr.add_argument("--title", required=True)
    pr.add_argument("--body", required=True)
    pr.add_argument("--source-sha", required=True)
    args = parser.parse_args()
    try:
        if args.command == "issue":
            value = read_issue(args.repo, args.number)
        elif args.command == "preview-issue":
            value = preview_issue(args.repo, args.title, args.body)
        else:
            value = preview_pull_request(args.repo, args.base, args.head, args.title, args.body, args.source_sha, current_sha())
        print(json.dumps(value, ensure_ascii=False, indent=2))
    except GitHubAdapterError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
