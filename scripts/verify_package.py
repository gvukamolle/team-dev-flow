#!/usr/bin/env python3
"""Verify a release archive exactly matches the reviewed inventory and checksum."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import tarfile
from pathlib import Path

try:
    from scripts.release_inventory import ROOT, collect_inventory
except ModuleNotFoundError:
    from release_inventory import ROOT, collect_inventory


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(archive: Path, root: Path = ROOT) -> tuple[int, str]:
    manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    prefix = f"{manifest['name']}-{manifest['version']}"
    inventory = collect_inventory(root)
    expected = {
        f"{prefix}/{path.relative_to(root).as_posix()}": path
        for path in inventory
    }
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        unsafe = [member.name for member in members if not member.isfile() or member.issym() or member.islnk()]
        counts = Counter(member.name for member in members)
        duplicates = sorted(name for name, count in counts.items() if count != 1)
        actual = set(counts)
        if unsafe:
            raise ValueError(f"unsafe package members: {unsafe}")
        if duplicates:
            raise ValueError(f"duplicate package members: {duplicates}")
        if len(members) != len(expected) or actual != set(expected):
            missing = sorted(set(expected) - actual)
            extra = sorted(actual - set(expected))
            raise ValueError(f"package inventory mismatch; missing={missing}, extra={extra}")
        for member in members:
            source_path = expected[member.name]
            expected_mode = 0o755 if source_path.stat().st_mode & 0o111 else 0o644
            if (
                member.uid != 0
                or member.gid != 0
                or member.uname != ""
                or member.gname != ""
                or member.mtime != 0
                or member.mode != expected_mode
            ):
                raise ValueError(f"package metadata mismatch: {member.name}")
            source_size = source_path.stat().st_size
            if member.size != source_size:
                raise ValueError(f"package content size mismatch: {member.name}")
            extracted = bundle.extractfile(member)
            if extracted is None:
                raise ValueError(f"package member is unreadable: {member.name}")
            digest = hashlib.sha256()
            remaining = source_size
            while remaining:
                chunk = extracted.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise ValueError(f"package member ended early: {member.name}")
                digest.update(chunk)
                remaining -= len(chunk)
            if extracted.read(1):
                raise ValueError(f"package member exceeds reviewed source size: {member.name}")
            if digest.hexdigest() != file_digest(source_path):
                raise ValueError(f"package content mismatch: {member.name}")
    checksum_path = archive.with_suffix(archive.suffix + ".sha256")
    expected_digest = checksum_path.read_text(encoding="utf-8").split()[0]
    actual_digest = file_digest(archive)
    if actual_digest != expected_digest:
        raise ValueError("package checksum mismatch")
    return len(actual), actual_digest


def main() -> int:
    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    prefix = f"{manifest['name']}-{manifest['version']}"
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path, nargs="?", default=ROOT / "dist" / f"{prefix}.tar.gz")
    args = parser.parse_args()
    try:
        count, digest = verify_archive(args.archive.resolve(), ROOT)
    except (OSError, ValueError, json.JSONDecodeError, tarfile.TarError) as error:
        print(f"ERROR: {error}")
        return 1
    print(f"Package verification: PASS ({count} files, {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
