#!/usr/bin/env python3
"""Generate and manage a GitHub-ready Team Dev Flow marketplace repository."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from scripts.local_task_store import StoreError, atomic_write
except ModuleNotFoundError:
    from local_task_store import StoreError, atomic_write


SHA = re.compile(r"^[a-f0-9]{40}$")
DIGEST = re.compile(r"^[a-f0-9]{64}$")
NAME = re.compile(r"^[A-Za-z0-9_.-]+$")
ROOT = Path(__file__).resolve().parents[1]


def release(version: str, git_ref: str, digest: str) -> dict:
    if not version or not SHA.fullmatch(git_ref) or not DIGEST.fullmatch(digest):
        raise StoreError("release requires version, full lowercase Git SHA, and SHA-256")
    return {"version": version, "git_ref": git_ref, "artifact_sha256": digest}


def catalog(owner: str, plugin_repo: str, marketplace_name: str, current: dict) -> dict:
    if not all(NAME.fullmatch(item or "") for item in (owner, plugin_repo, marketplace_name)):
        raise StoreError("unsafe GitHub owner, repository, or marketplace name")
    return {
        "name": marketplace_name,
        "interface": {"displayName": "Team Dev Flow"},
        "plugins": [{
            "name": "team-dev-flow",
            "source": {"source": "url", "url": f"https://github.com/{owner}/{plugin_repo}.git", "ref": current["git_ref"]},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Developer Tools",
        }],
    }


def _json(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def generate(root: Path, owner: str, plugin_repo: str, marketplace_name: str, version: str, git_ref: str, digest: str, visibility: str, license_id: str) -> None:
    if root.exists() and (root.is_symlink() or not root.is_dir() or any(root.iterdir())):
        raise StoreError("marketplace output must be a missing or empty regular directory")
    if visibility not in {"private", "public"}:
        raise StoreError("visibility must be private or public")
    if visibility == "public" and license_id.upper() == "UNLICENSED":
        raise StoreError("public marketplace requires an explicit distribution license")
    current = release(version, git_ref, digest)
    files = {
        ".agents/plugins/marketplace.json": catalog(owner, plugin_repo, marketplace_name, current),
        "channels/canary.json": {"schema_version": "team-dev-flow/marketplace-channel/v1", "channel": "canary", "plugin": "team-dev-flow", "current": current, "previous": None},
        "channels/stable.json": {"schema_version": "team-dev-flow/marketplace-channel/v1", "channel": "stable", "plugin": "team-dev-flow", "current": None, "previous": None},
        "marketplace-policy.json": {"schema_version": "team-dev-flow/marketplace-policy/v1", "visibility": visibility, "license": license_id, "owner": owner, "plugin_repository": plugin_repo, "publication_status": "local-scaffold"},
    }
    root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    try:
        for name, value in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, _json(value))
            written.append(target)
        atomic_write(root / "README.md", (
            "# Team Dev Flow marketplace\n\n"
            "Immutable canary/stable catalog for Team Dev Flow. Validate with "
            "`python3 scripts/github_marketplace.py verify --root .`. Promote only "
            "a reviewed full Git SHA and matching release SHA-256.\n"
        ).encode())
        written.append(root / "README.md")
        atomic_write(root / "LICENSE", (ROOT / "LICENSE").read_bytes())
        written.append(root / "LICENSE")
    except Exception:
        for path in reversed(written):
            path.unlink(missing_ok=True)
        raise


def load(root: Path, relative: str) -> dict:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise StoreError(f"unsafe or missing marketplace file: {relative}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise StoreError(f"marketplace file must contain an object: {relative}")
    return value


def verify(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        market = load(root, ".agents/plugins/marketplace.json")
        canary = load(root, "channels/canary.json")
        stable = load(root, "channels/stable.json")
        policy = load(root, "marketplace-policy.json")
        if canary.get("channel") != "canary" or stable.get("channel") != "stable":
            errors.append("channel identity mismatch")
        current = stable.get("current") or canary.get("current")
        source = ((market.get("plugins") or [{}])[0].get("source") or {})
        if not current or source.get("ref") != current.get("git_ref"):
            errors.append("catalog ref does not match selected channel")
        if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git", source.get("url", "")):
            errors.append("catalog source is not a canonical GitHub HTTPS URL")
        for channel in (canary, stable):
            for item in (channel.get("current"), channel.get("previous")):
                if item:
                    release(item.get("version", ""), item.get("git_ref", ""), item.get("artifact_sha256", ""))
        if policy.get("visibility") == "public" and str(policy.get("license", "")).upper() == "UNLICENSED":
            errors.append("public marketplace is unlicensed")
    except (OSError, ValueError, json.JSONDecodeError, StoreError, IndexError) as exc:
        errors.append(str(exc))
    return errors


def set_canary(root: Path, value: dict) -> None:
    channel = load(root, "channels/canary.json")
    channel["previous"] = channel.get("current")
    channel["current"] = value
    atomic_write(root / "channels/canary.json", _json(channel))
    market = load(root, ".agents/plugins/marketplace.json")
    market["plugins"][0]["source"]["ref"] = value["git_ref"]
    atomic_write(root / ".agents/plugins/marketplace.json", _json(market))


def promote(root: Path) -> None:
    canary = load(root, "channels/canary.json")
    stable = load(root, "channels/stable.json")
    if not canary.get("current"):
        raise StoreError("canary has no current release")
    stable["previous"] = stable.get("current")
    stable["current"] = canary["current"]
    atomic_write(root / "channels/stable.json", _json(stable))
    market = load(root, ".agents/plugins/marketplace.json")
    market["plugins"][0]["source"]["ref"] = stable["current"]["git_ref"]
    atomic_write(root / ".agents/plugins/marketplace.json", _json(market))


def rollback(root: Path) -> None:
    stable = load(root, "channels/stable.json")
    if not stable.get("previous"):
        raise StoreError("stable has no previous release to restore")
    stable["current"], stable["previous"] = stable["previous"], stable["current"]
    atomic_write(root / "channels/stable.json", _json(stable))
    market = load(root, ".agents/plugins/marketplace.json")
    market["plugins"][0]["source"]["ref"] = stable["current"]["git_ref"]
    atomic_write(root / ".agents/plugins/marketplace.json", _json(market))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("generate")
    create.add_argument("--root", type=Path, required=True)
    create.add_argument("--owner", required=True)
    create.add_argument("--plugin-repo", default="team-dev-flow")
    create.add_argument("--marketplace-name", default="team-flow")
    create.add_argument("--version", required=True)
    create.add_argument("--git-ref", required=True)
    create.add_argument("--artifact-sha256", required=True)
    create.add_argument("--visibility", choices=["private", "public"], required=True)
    create.add_argument("--license", required=True)
    verify_cmd = sub.add_parser("verify")
    verify_cmd.add_argument("--root", type=Path, required=True)
    for name in ("promote", "rollback"):
        item = sub.add_parser(name)
        item.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "generate":
            generate(args.root, args.owner, args.plugin_repo, args.marketplace_name, args.version, args.git_ref, args.artifact_sha256, args.visibility, args.license)
            result = {"generated": str(args.root), "valid": not verify(args.root)}
        elif args.command == "verify":
            errors = verify(args.root)
            result = {"valid": not errors, "errors": errors}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if not errors else 1
        else:
            (promote if args.command == "promote" else rollback)(args.root)
            errors = verify(args.root)
            result = {"action": args.command, "valid": not errors, "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, StoreError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
