#!/usr/bin/env python3
"""Validate the organization-neutral Universal plugin repository."""

from __future__ import annotations

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

try:
    from scripts.release_inventory import collect_inventory
    from scripts.secret_scan import scan_paths
except ModuleNotFoundError:
    from release_inventory import collect_inventory
    from secret_scan import scan_paths


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {"index", "setup", "start-work", "discover-and-scope", "execute-ticket", "review-loop", "address-feedback", "finish-ticket", "specify", "plan-work", "local-task-store"}
LOCAL_LINK = re.compile(r"\[[^]]*]\((?!https?://|#|mailto:)([^)]+)\)")
INTERNAL_MARKERS = (
    "b2" + "serv",
    "b2" + "pos",
    "jira." + "b2" + "serv.local",
    "git." + "b2" + "serv.local",
    "customfield_" + "10102",
    "customfield_" + "10107",
)
INTERNAL_IDS = re.compile(r"\b(?:ML-(?:314|350)|POS-(?:6114|6250)|EPIC-(?:1470|1921)|INIT-(?:20|24|276)|TARGET-" + "69)\b", re.I)


def main() -> int:
    errors: list[str] = []
    manifest_path = ROOT / ".codex-plugin/plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for field in ("name", "version", "description", "author", "license", "skills", "interface"):
            if not manifest.get(field):
                errors.append(f"manifest missing {field}")
        if "mcpServers" in manifest:
            errors.append("Universal manifest must not bundle an organization-specific MCP server")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid plugin manifest: {exc}")

    skill_names = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    if skill_names != EXPECTED_SKILLS:
        errors.append(f"skill set mismatch: {sorted(skill_names)}")

    for schema in sorted((ROOT / "contracts").glob("*.schema.json")):
        try:
            value = json.loads(schema.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(value)
        except Exception as exc:
            errors.append(f"invalid schema {schema.relative_to(ROOT)}: {exc}")

    capability_schema = json.loads((ROOT / "contracts/capability-manifest.schema.json").read_text(encoding="utf-8"))
    flow_schema = json.loads((ROOT / "contracts/flow-profile.schema.json").read_text(encoding="utf-8"))
    manifests: dict[str, dict] = {}
    for path in sorted((ROOT / "profiles/providers").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        for issue in Draft202012Validator(capability_schema).iter_errors(value):
            errors.append(f"invalid provider {path.name}: {issue.message}")
        manifests[value.get("id")] = value
    for path in sorted((ROOT / "profiles/flow").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        for issue in Draft202012Validator(flow_schema).iter_errors(value):
            errors.append(f"invalid flow {path.name}: {issue.message}")
        for kind, adapter_id in value.get("adapters", {}).items():
            if adapter_id and adapter_id not in manifests:
                errors.append(f"flow {path.name} references missing {kind} adapter {adapter_id}")

    try:
        files = collect_inventory(ROOT)
        errors.extend(scan_paths(files, ROOT))
    except ValueError as exc:
        files = []
        errors.append(f"invalid release inventory: {exc}")

    forbidden_paths = ("mcp/jira/", "profiles/jira/", "templates/corporate/", "templates/jira/")
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if any(relative.startswith(prefix) for prefix in forbidden_paths):
            errors.append(f"corporate-only path in release: {relative}")
        if path.suffix.lower() in {".cjs", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"} or path.name in {"LICENSE", ".gitignore", ".gitattributes"}:
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for marker in INTERNAL_MARKERS:
                if marker in lowered:
                    errors.append(f"internal marker in {relative}")
            if INTERNAL_IDS.search(text):
                errors.append(f"internal task identifier in {relative}")

    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for raw in LOCAL_LINK.findall(text):
            target = raw.split("#", 1)[0]
            if target and "{{" not in target and not (path.parent / target).resolve().exists():
                errors.append(f"broken local link in {path.relative_to(ROOT)}: {raw}")

    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1
    print(f"Universal repository validation: PASS ({len(skill_names)} skills, {len(files)} release files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
