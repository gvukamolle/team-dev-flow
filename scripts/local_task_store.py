#!/usr/bin/env python3
"""Safe Local Markdown / Obsidian TaskStore for Team Dev Flow."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import stat
import tempfile
import time
from pathlib import Path
from typing import Callable, Iterator

try:
    from scripts.redact_stream import redact_text
except ModuleNotFoundError:
    from redact_stream import redact_text


SCHEMA_VERSION = "team-dev-flow/local-store/v1"
ARTIFACT_VERSION = "team-dev-flow/local-artifact/v1"
KINDS = {"project", "initiative", "epic", "spec", "task"}
KIND_FOLDERS = {
    "project": "",
    "initiative": "Initiatives",
    "epic": "Epics",
    "spec": "Specs",
    "task": "Tasks",
}
STATUSES = {"backlog", "draft", "clarifying", "ready", "active", "blocked", "verifying", "reviewing", "done", "cancelled", "superseded"}
HEALTH = {"unknown", "on_track", "at_risk", "blocked"}
STAGES = {"discovery", "specifying", "planning", "implementing", "verifying", "reviewing", "done"}
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
TOP_LEVEL_PROPERTY = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?:\s*(?P<value>.*))?$")
MANAGED_START = "<!-- team-dev-flow:managed:start -->"
MANAGED_END = "<!-- team-dev-flow:managed:end -->"
RESERVED_ROOT_PARTS = {".obsidian", ".trash", ".git", ".agents"}


class StoreError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_identifier(value: str, label: str) -> str:
    if not IDENTIFIER.fullmatch(value or ""):
        raise StoreError(f"invalid {label}: use 1-64 letters, digits, dots, underscores, or hyphens")
    return value


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def select_store_root(vault: Path, folder: str) -> Path:
    """Resolve a new/existing store below a real vault directory without traversal."""
    vault = vault.expanduser()
    if not vault.is_dir() or vault.is_symlink():
        raise StoreError("vault must be an existing non-symlink directory")
    vault_real = vault.resolve(strict=True)
    relative = Path(folder)
    if relative.is_absolute() or not relative.parts or any(part in {"", ".", ".."} or part in RESERVED_ROOT_PARTS for part in relative.parts):
        raise StoreError("store folder must be a safe vault-relative path outside reserved directories")
    candidate = vault_real.joinpath(relative)
    existing_parent = candidate
    while not existing_parent.exists():
        existing_parent = existing_parent.parent
    if existing_parent.is_symlink() or not _is_relative_to(existing_parent.resolve(strict=True), vault_real):
        raise StoreError("store folder escapes the selected vault")
    if candidate.exists() and (not candidate.is_dir() or candidate.is_symlink()):
        raise StoreError("store root must be a real directory, not a file or symlink")
    candidate.mkdir(parents=True, exist_ok=True)
    current = candidate
    while current != vault_real:
        if current.is_symlink():
            raise StoreError(f"symlinked store path is forbidden: {current}")
        current = current.parent
    if not _is_relative_to(candidate.resolve(strict=True), vault_real):
        raise StoreError("store root resolves outside the selected vault")
    return candidate


def validate_store_root(root: Path) -> Path:
    root = root.expanduser()
    if not root.is_dir() or root.is_symlink():
        raise StoreError("TaskStore root must be an existing non-symlink directory")
    real = root.resolve(strict=True)
    config = real / ".team-dev-flow" / "store.json"
    if not config.is_file() or config.is_symlink():
        raise StoreError("TaskStore is not initialized or its config is unsafe")
    return real


def _safe_target(root: Path, relative: Path, *, create_parent: bool = True) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise StoreError("artifact path traversal is forbidden")
    target = root / relative
    if create_parent:
        target.parent.mkdir(parents=True, exist_ok=True)
    current = target.parent
    while not current.exists():
        current = current.parent
    while current != root:
        if current.is_symlink():
            raise StoreError(f"symlinked TaskStore path is forbidden: {current}")
        current = current.parent
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise StoreError("artifact target must be a regular file")
    if not _is_relative_to(target.parent.resolve(strict=False), root.resolve(strict=True)):
        raise StoreError("artifact target escapes TaskStore root")
    return target


def atomic_write(path: Path, data: bytes, after_replace: Callable[[Path], None] | None = None) -> bool:
    """Atomically replace a regular file and restore the previous bytes on post-replace failure."""
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise StoreError("atomic target must be a regular file")
    previous = path.read_bytes() if path.exists() else None
    if previous == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(raw_temp)
    replaced = False
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o644)
        os.replace(temp, path)
        replaced = True
        if after_replace:
            after_replace(path)
        if hasattr(os, "O_DIRECTORY"):
            directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        return True
    except Exception:
        if replaced:
            if previous is None:
                with contextlib.suppress(FileNotFoundError):
                    path.unlink()
            else:
                rollback_fd, rollback_name = tempfile.mkstemp(prefix=f".{path.name}.rollback.", suffix=".tmp", dir=path.parent)
                try:
                    with os.fdopen(rollback_fd, "wb") as stream:
                        stream.write(previous)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.chmod(rollback_name, 0o644)
                    os.replace(rollback_name, path)
                finally:
                    with contextlib.suppress(FileNotFoundError):
                        Path(rollback_name).unlink()
        raise
    finally:
        with contextlib.suppress(FileNotFoundError):
            temp.unlink()


class StoreLock:
    def __init__(self, root: Path, timeout: float = 5.0):
        self.path = root / ".team-dev-flow" / "store.lock"
        self.timeout = timeout
        self.stream = None

    def __enter__(self) -> "StoreLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("a+b")
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    self.stream.seek(0)
                    msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except (BlockingIOError, OSError):
                if time.monotonic() >= deadline:
                    self.stream.close()
                    self.stream = None
                    raise StoreError("TaskStore is locked by another process")
                time.sleep(0.05)

    def __exit__(self, exc_type, exc, traceback) -> None:
        if not self.stream:
            return
        if os.name == "nt":
            import msvcrt
            self.stream.seek(0)
            with contextlib.suppress(OSError):
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
        self.stream.close()
        self.stream = None


def _store_id(root: Path) -> str:
    return hashlib.sha256(str(root.resolve(strict=True)).encode()).hexdigest()[:16]


def _read_config(root: Path) -> dict:
    config = root / ".team-dev-flow" / "store.json"
    value = json.loads(config.read_text(encoding="utf-8"))
    if value.get("schema_version") != SCHEMA_VERSION or value.get("provider") != "local_markdown":
        raise StoreError("unsupported Local TaskStore configuration")
    if value.get("store_id") != _store_id(root):
        raise StoreError("TaskStore root identity does not match its canonical path")
    return value


def _dashboard(store_id: str) -> str:
    common_order = "      - file.name\n      - tdf_kind\n      - status\n      - health\n      - stage\n      - due\n      - parent\n"
    return (
        f"filters:\n  and:\n    - 'tdf_store == \"{store_id}\"'\n    - 'file.ext == \"md\"'\n"
        "properties:\n  tdf_kind:\n    displayName: Type\n  status:\n    displayName: Status\n  health:\n    displayName: Health\n  stage:\n    displayName: Stage\n  due:\n    displayName: Due\n  parent:\n    displayName: Parent\n"
        "views:\n"
        "  - type: table\n    name: Today\n    filters:\n      and:\n        - 'due == today()'\n        - 'status != \"done\"'\n    order:\n" + common_order +
        "  - type: table\n    name: In progress\n    filters:\n      or:\n        - 'status == \"active\"'\n        - 'stage == \"implementing\"'\n    order:\n" + common_order +
        "  - type: table\n    name: Blocked\n    filters:\n      or:\n        - 'status == \"blocked\"'\n        - 'health == \"blocked\"'\n    order:\n" + common_order +
        "  - type: table\n    name: Verification\n    filters: 'stage == \"verifying\"'\n    order:\n" + common_order +
        "  - type: table\n    name: Review\n    filters: 'stage == \"reviewing\"'\n    order:\n" + common_order
    )


def init_store(vault: Path, folder: str = "Team Dev Flow") -> Path:
    root = select_store_root(vault, folder)
    metadata = root / ".team-dev-flow"
    metadata.mkdir(parents=True, exist_ok=True)
    config_path = _safe_target(root, Path(".team-dev-flow/store.json"))
    existing = None
    if config_path.exists():
        existing = json.loads(config_path.read_text(encoding="utf-8"))
    store_id = _store_id(root)
    config = {
        "schema_version": SCHEMA_VERSION,
        "store_id": store_id,
        "provider": "local_markdown",
        "root_name": root.name,
        "created": existing.get("created") if isinstance(existing, dict) and existing.get("store_id") == store_id else utc_now(),
    }
    if existing and existing.get("store_id") != store_id:
        raise StoreError("existing TaskStore configuration belongs to another root")
    with StoreLock(root):
        atomic_write(config_path, (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode())
        atomic_write(_safe_target(root, Path("Dashboard.base")), _dashboard(store_id).encode())
    return root


def _artifact_relative(project: str, kind: str, identifier: str) -> Path:
    validate_identifier(project, "project")
    validate_identifier(identifier, "artifact id")
    if kind not in KINDS:
        raise StoreError(f"unsupported artifact kind: {kind}")
    if kind == "project":
        if identifier != project:
            raise StoreError("project artifact id must match the project id")
        return Path("Projects") / project / "Project.md"
    return Path("Projects") / project / KIND_FOLDERS[kind] / f"{identifier}.md"


def _parse_frontmatter(text: str) -> tuple[list[str], str]:
    if not text.startswith("---\n"):
        return [], text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise StoreError("unterminated YAML frontmatter")
    return text[4:end].splitlines(), text[end + 5:]


def _yaml_value(key: str, value: object) -> str:
    if value is None:
        return "null"
    if key in {"created", "updated", "due"} and isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T[^\s]+)?", value):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _update_properties(lines: list[str], properties: dict[str, object]) -> list[str]:
    indexes: dict[str, int] = {}
    for index, line in enumerate(lines):
        match = TOP_LEVEL_PROPERTY.match(line)
        if not match:
            continue
        key = match.group("key")
        if key in indexes:
            raise StoreError(f"duplicate top-level property: {key}")
        indexes[key] = index
    result = list(lines)
    for key, value in properties.items():
        rendered = f"{key}: {_yaml_value(key, value)}"
        if key in indexes:
            result[indexes[key]] = rendered
        else:
            result.append(rendered)
    return result


def _existing_property(lines: list[str], key: str) -> str | None:
    for line in lines:
        match = TOP_LEVEL_PROPERTY.match(line)
        if match and match.group("key") == key:
            raw = (match.group("value") or "").strip()
            if raw.startswith('"'):
                try:
                    return str(json.loads(raw))
                except json.JSONDecodeError:
                    return raw.strip('"')
            return raw
    return None


def _replace_managed_body(body: str, managed: str, description: str | None, is_new: bool) -> str:
    block = f"{MANAGED_START}\n{managed.rstrip()}\n{MANAGED_END}\n"
    start = body.find(MANAGED_START)
    end = body.find(MANAGED_END)
    if (start >= 0) != (end >= 0) or (start >= 0 and end < start):
        raise StoreError("invalid Team Dev Flow managed markers")
    if start >= 0:
        suffix = body[end + len(MANAGED_END):].strip("\n")
        prefix = body[:start].strip("\n")
        pieces = [item for item in (prefix, block.rstrip("\n"), suffix) if item]
        return "\n\n".join(pieces) + "\n"
    preserved = body.strip("\n")
    user_text = description.strip() if is_new and description else preserved
    return block + (f"\n{user_text}\n" if user_text else "")


def _wikilink(relative: Path) -> str:
    return f"[[{relative.with_suffix('').as_posix()}]]"


def _append_history(root: Path, ref: str, event: dict) -> None:
    safe_name = hashlib.sha256(ref.encode()).hexdigest()[:24]
    path = _safe_target(root, Path(".team-dev-flow/history") / f"{safe_name}.jsonl")
    sanitized = {
        key: redact_text(value) if isinstance(value, str) else value
        for key, value in event.items()
    }
    line = (json.dumps(sanitized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(line) > 16384:
        raise StoreError("history event exceeds 16 KiB")
    previous = path.read_bytes() if path.exists() else b""
    if previous and not previous.endswith(b"\n"):
        raise StoreError("history has an incomplete trailing record; refusing to append")
    atomic_write(path, previous + line)


def upsert_artifact(
    root: Path,
    *,
    project: str,
    kind: str,
    identifier: str,
    title: str,
    status: str = "backlog",
    health: str = "unknown",
    stage: str = "discovery",
    parent: tuple[str, str] | None = None,
    dependencies: list[tuple[str, str]] | None = None,
    due: str | None = None,
    description: str | None = None,
    evidence: str | None = None,
    preview: bool = False,
) -> Path | dict[str, object]:
    root = validate_store_root(root)
    config = _read_config(root)
    validate_identifier(project, "project")
    validate_identifier(identifier, "artifact id")
    if kind not in KINDS or status not in STATUSES or health not in HEALTH or stage not in STAGES:
        raise StoreError("invalid kind, status, health, or stage")
    if not title.strip():
        raise StoreError("artifact title is required")
    if due and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due):
        raise StoreError("due must use YYYY-MM-DD")
    dependencies = dependencies or []
    relative = _artifact_relative(project, kind, identifier)
    target = _safe_target(root, relative, create_parent=not preview)
    parent_relative = _artifact_relative(project, parent[0], parent[1]) if parent else None
    dependency_relatives = [_artifact_relative(project, item_kind, item_id) for item_kind, item_id in dependencies]
    for relation in ([parent_relative] if parent_relative else []) + dependency_relatives:
        if relation and not (root / relation).is_file():
            raise StoreError(f"linked artifact does not exist: {relation.as_posix()}")
    ref = f"local_markdown:{config['store_id']}:{project}/{kind}/{identifier}"
    parent_ref = f"local_markdown:{config['store_id']}:{project}/{parent[0]}/{parent[1]}" if parent else None
    dependency_refs = [f"local_markdown:{config['store_id']}:{project}/{item_kind}/{item_id}" for item_kind, item_id in dependencies]
    now = utc_now()
    with StoreLock(root):
        existing_text = target.read_text(encoding="utf-8") if target.exists() else ""
        frontmatter, body = _parse_frontmatter(existing_text)
        created = _existing_property(frontmatter, "created") or now
        previous_updated = _existing_property(frontmatter, "updated") or now
        properties = {
            "tdf_schema": ARTIFACT_VERSION,
            "tdf_store": config["store_id"],
            "tdf_ref": ref,
            "tdf_id": identifier,
            "tdf_kind": kind,
            "tdf_project": project,
            "title": title.strip(),
            "status": status,
            "health": health,
            "stage": stage,
            "parent_ref": parent_ref,
            "parent": _wikilink(parent_relative) if parent_relative else None,
            "dependency_refs": dependency_refs,
            "dependencies": [_wikilink(item) for item in dependency_relatives],
            "created": created,
            "updated": previous_updated,
            "due": due,
        }
        managed = f"# {title.strip()}\n\n`{ref}`\n"
        rendered_body = _replace_managed_body(body, managed, description, not target.exists())
        rendered = "---\n" + "\n".join(_update_properties(frontmatter, properties)) + "\n---\n" + rendered_body
        if existing_text and rendered == existing_text:
            if preview:
                return {"target": str(target), "changed": False, "content": rendered}
            return target
        properties["updated"] = now
        rendered = "---\n" + "\n".join(_update_properties(frontmatter, properties)) + "\n---\n" + rendered_body
        if preview:
            return {"target": str(target), "changed": rendered != existing_text, "content": rendered}
        changed = atomic_write(target, rendered.encode())
        if changed:
            try:
                _append_history(root, ref, {
                    "schema_version": "team-dev-flow/local-history/v1",
                    "timestamp": now,
                    "event": "created" if not existing_text else "updated",
                    "ref": ref,
                    "status": status,
                    "health": health,
                    "stage": stage,
                    "evidence": evidence or "",
                    "content_hash": hashlib.sha256(rendered.encode()).hexdigest(),
                })
            except Exception:
                if existing_text:
                    atomic_write(target, existing_text.encode())
                else:
                    with contextlib.suppress(FileNotFoundError):
                        target.unlink()
                raise
    return target


def parse_relation(value: str) -> tuple[str, str]:
    parts = value.split(":", 1)
    if len(parts) != 2 or parts[0] not in KINDS:
        raise StoreError("relations use kind:id, for example epic:EPIC-1")
    validate_identifier(parts[1], "relation id")
    return parts[0], parts[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    init = subparsers.add_parser("init")
    init.add_argument("--vault", type=Path, required=True)
    init.add_argument("--folder", default="Team Dev Flow")
    def add_artifact_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--project", required=True)
        command.add_argument("--kind", choices=sorted(KINDS), required=True)
        command.add_argument("--id", required=True)
        command.add_argument("--title", required=True)
        command.add_argument("--status", choices=sorted(STATUSES), default="backlog")
        command.add_argument("--health", choices=sorted(HEALTH), default="unknown")
        command.add_argument("--stage", choices=sorted(STAGES), default="discovery")
        command.add_argument("--parent", type=parse_relation)
        command.add_argument("--depends", action="append", type=parse_relation, default=[])
        command.add_argument("--due")
        command.add_argument("--description")
        command.add_argument("--evidence")
    add_artifact_arguments(subparsers.add_parser("preview"))
    add_artifact_arguments(subparsers.add_parser("upsert"))
    args = parser.parse_args()
    try:
        if args.command == "init":
            print(init_store(args.vault, args.folder))
        else:
            result = upsert_artifact(
                args.root, project=args.project, kind=args.kind, identifier=args.id,
                title=args.title, status=args.status, health=args.health, stage=args.stage,
                parent=args.parent, dependencies=args.depends, due=args.due,
                description=args.description, evidence=args.evidence,
                preview=args.command == "preview",
            )
            print(json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else result)
    except (OSError, ValueError, json.JSONDecodeError, StoreError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
