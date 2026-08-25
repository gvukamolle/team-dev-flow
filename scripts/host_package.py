#!/usr/bin/env python3
"""Install/check transactional Team Dev Flow host overlays."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path

try:
    from scripts.local_task_store import StoreError, atomic_write, utc_now
    from scripts.release_inventory import collect_inventory
except ModuleNotFoundError:
    from local_task_store import StoreError, atomic_write, utc_now
    from release_inventory import collect_inventory


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_VERSION = "team-dev-flow/host-install/v1"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _workspace(path: Path) -> Path:
    path = path.expanduser()
    if not path.is_dir() or path.is_symlink():
        raise StoreError("workspace must be an existing non-symlink directory")
    return path.resolve(strict=True)


def _target(workspace: Path, relative: Path, *, create_parent: bool) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise StoreError("host package path traversal is forbidden")
    target = workspace / relative
    current = target.parent
    while not current.exists():
        current = current.parent
    while current != workspace:
        if current.is_symlink():
            raise StoreError(f"symlinked host package path is forbidden: {current}")
        current = current.parent
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise StoreError(f"host package target is not a regular file: {relative}")
    if create_parent:
        target.parent.mkdir(parents=True, exist_ok=True)
    if workspace not in target.resolve(strict=False).parents:
        raise StoreError("host package target escapes the workspace")
    return target


def kilo_payload(plugin_root: Path = ROOT) -> dict[str, bytes]:
    payload: dict[str, bytes] = {}
    for source in collect_inventory(plugin_root):
        relative = source.relative_to(plugin_root)
        payload[(Path(".team-dev-flow/plugin") / relative).as_posix()] = source.read_bytes()
    mappings = {
        "host-packages/kilo/skills/team-dev-flow/SKILL.md": ".kilo/skills/team-dev-flow/SKILL.md",
        "host-packages/kilo/agents/team-dev-flow.md": ".kilo/agents/team-dev-flow.md",
        "host-packages/kilo/rules/team-dev-flow.md": ".kilo/rules/team-dev-flow.md",
    }
    for source_name, target_name in mappings.items():
        payload[target_name] = (plugin_root / source_name).read_bytes()
    return payload


def _manifest_path(workspace: Path, host: str) -> Path:
    return workspace / ".team-dev-flow/hosts" / f"{host}.json"


def _load_manifest(workspace: Path, host: str) -> dict | None:
    path = _manifest_path(workspace, host)
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise StoreError("host install manifest is unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != MANIFEST_VERSION or value.get("host") != host:
        raise StoreError("unsupported host install manifest")
    return value


def check_host(workspace: Path, host: str = "kilo") -> list[str]:
    workspace = _workspace(workspace)
    manifest = _load_manifest(workspace, host)
    if not manifest:
        return ["host package is not installed"]
    errors: list[str] = []
    for item in manifest.get("files", []):
        relative = Path(item.get("path", ""))
        try:
            target = _target(workspace, relative, create_parent=False)
        except StoreError as exc:
            errors.append(str(exc))
            continue
        if not target.is_file():
            errors.append(f"missing installed file: {relative.as_posix()}")
        elif _sha(target.read_bytes()) != item.get("sha256"):
            errors.append(f"installed file drift: {relative.as_posix()}")
    return errors


def install_kilo(
    workspace: Path,
    plugin_root: Path = ROOT,
    *,
    preview: bool = False,
    fail_after: int | None = None,
) -> dict:
    workspace = _workspace(workspace)
    plugin_root = plugin_root.resolve(strict=True)
    payload = kilo_payload(plugin_root)
    previous_manifest = _load_manifest(workspace, "kilo")
    owned = {item["path"]: item["sha256"] for item in (previous_manifest or {}).get("files", [])}
    if previous_manifest:
        drift = check_host(workspace, "kilo")
        if drift:
            raise StoreError("refusing update because installed host files drifted: " + "; ".join(drift))
    for relative_name in payload:
        target = _target(workspace, Path(relative_name), create_parent=False)
        if target.exists() and relative_name not in owned:
            raise StoreError(f"refusing to overwrite unowned workspace file: {relative_name}")
    inventory = [{"path": name, "sha256": _sha(data), "size": len(data)} for name, data in sorted(payload.items())]
    plugin_manifest = json.loads((plugin_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    installed_at = (previous_manifest or {}).get("installed_at") or utc_now()
    manifest = {
        "schema_version": MANIFEST_VERSION,
        "host": "kilo",
        "plugin_version": plugin_manifest["version"],
        "installed_at": installed_at,
        "files": inventory,
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    current_manifest_bytes = _manifest_path(workspace, "kilo").read_bytes() if previous_manifest else None
    changed = [item for item in inventory if not (workspace / item["path"]).is_file() or _sha((workspace / item["path"]).read_bytes()) != item["sha256"]]
    manifest_changed = current_manifest_bytes != manifest_bytes
    if preview:
        return {"host": "kilo", "plugin_version": plugin_manifest["version"], "changed": [item["path"] for item in changed], "manifest_changed": manifest_changed}
    backups: dict[Path, bytes | None] = {}
    replaced = 0
    try:
        for item in changed:
            relative = Path(item["path"])
            target = _target(workspace, relative, create_parent=True)
            backups[target] = target.read_bytes() if target.exists() else None
            atomic_write(target, payload[item["path"]])
            replaced += 1
            if fail_after is not None and replaced >= fail_after:
                raise RuntimeError("injected host install failure")
        if manifest_changed:
            path = _target(workspace, Path(".team-dev-flow/hosts/kilo.json"), create_parent=True)
            backups[path] = current_manifest_bytes
            atomic_write(path, manifest_bytes)
        errors = check_host(workspace, "kilo")
        if errors:
            raise StoreError("host package post-install verification failed: " + "; ".join(errors))
    except Exception:
        for path, previous in reversed(list(backups.items())):
            if previous is None:
                with contextlib.suppress(FileNotFoundError):
                    path.unlink()
            else:
                atomic_write(path, previous)
        raise
    return {"host": "kilo", "plugin_version": plugin_manifest["version"], "changed": len(changed), "verified": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("preview", "install", "check"):
        item = subparsers.add_parser(command)
        item.add_argument("--host", choices=["kilo"], required=True)
        item.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "check":
            errors = check_host(args.workspace, args.host)
            result = {"host": args.host, "valid": not errors, "errors": errors}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if not errors else 1
        result = install_kilo(args.workspace, preview=args.command == "preview")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, StoreError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
