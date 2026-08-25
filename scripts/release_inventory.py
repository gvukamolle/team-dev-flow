#!/usr/bin/env python3
"""Resolve the explicit, reviewable release inventory."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "packaging" / "release-files.json"


def load_manifest(root: Path = ROOT) -> dict:
    path = root / "packaging" / "release-files.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "team-dev-flow/release-files/v1":
        raise ValueError("unsupported release inventory schema")
    return manifest


def _is_denied(relative: Path, manifest: dict) -> bool:
    return (
        relative.name in set(manifest["denied_names"])
        or relative.suffix.lower() in set(manifest["denied_suffixes"])
        or "__pycache__" in relative.parts
        or relative.name == ".DS_Store"
    )


def is_release_candidate(relative: Path, manifest: dict) -> bool:
    if relative.is_absolute() or ".." in relative.parts or _is_denied(relative, manifest):
        return False
    normalized = relative.as_posix()
    if normalized in set(manifest["include_files"]):
        return True
    if relative.suffix.lower() not in set(manifest["allowed_suffixes"]):
        return False
    return any(relative.parts and relative.parts[0] == tree for tree in manifest["include_trees"])


def collect_inventory(root: Path = ROOT) -> list[Path]:
    manifest = load_manifest(root)
    inventory: list[Path] = []
    for relative_name in manifest["include_files"]:
        path = root / relative_name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"required release file is missing or is a symlink: {relative_name}")
        inventory.append(path)
    for tree_name in manifest["include_trees"]:
        tree = root / tree_name
        if not tree.is_dir() or tree.is_symlink():
            raise ValueError(f"required release tree is missing or is a symlink: {tree_name}")
        for path in tree.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if path.is_symlink():
                raise ValueError(f"release inventory cannot contain symlink: {relative}")
            if is_release_candidate(relative, manifest):
                inventory.append(path)
    return sorted(set(inventory), key=lambda path: path.relative_to(root).as_posix())


if __name__ == "__main__":
    for item in collect_inventory():
        print(item.relative_to(ROOT).as_posix())
