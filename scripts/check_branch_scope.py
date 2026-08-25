#!/usr/bin/env python3
"""Check that an implementation branch carries a provider-neutral scope identifier."""

from __future__ import annotations

import argparse
import re
import subprocess


def branch_slug(scope_ref: str) -> str:
    native_id = scope_ref.rsplit(":", 1)[-1]
    slug = re.sub(r"[^A-Za-z0-9]+", "-", native_id).strip("-")
    if not slug:
        raise ValueError("scope reference has no branch-safe identifier")
    return slug


def branch_matches(scope_ref: str, branch: str) -> bool:
    slug = branch_slug(scope_ref).lower()
    lowered = branch.lower()
    return any(
        lowered == f"{prefix}/{slug}" or lowered.startswith(f"{prefix}/{slug}-")
        for prefix in ("feature", "hotfix", "sync", "discovery")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scope_ref")
    parser.add_argument("--branch")
    args = parser.parse_args()
    branch = args.branch or subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    try:
        valid = branch_matches(args.scope_ref, branch)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 2
    if not valid:
        print(f"ERROR: branch {branch!r} does not belong to {args.scope_ref}")
        return 1
    print(f"Branch: valid for {args.scope_ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
