#!/usr/bin/env python3
"""Scan an exact file inventory for likely embedded credentials."""

from __future__ import annotations

import json
import re
from pathlib import Path


SECRET_KEY = re.compile(
    r"(?:token|secret|password|api[_-]?key|authorization|cookie|credential)",
    re.IGNORECASE,
)
SECRET_ASSIGNMENT = re.compile(
    r"(?im)(?:^[ \t]*|[,{;]\s*)(?P<key>[\"']?[A-Za-z0-9_.-]*(?:token|secret|password|api[_-]?key|authorization|cookie|credential)[A-Za-z0-9_.-]*[\"']?)\s*[:=]\s*(?P<value>\"(?:\\.|[^\"\r\n])*\"|'(?:\\.|[^'\r\n])*'|[^\s,;}\]]+)",
)
BEARER = re.compile(r"(?i)bearer\s+(?P<value>[A-Za-z0-9._~+/-]{16,})")
PRIVATE_KEY_BEGIN = r"-----" + r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
PRIVATE_KEY_END = r"-----" + r"END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
PRIVATE_KEY = re.compile(PRIVATE_KEY_BEGIN + r".*?" + PRIVATE_KEY_END, re.DOTALL)
SAFE_PLACEHOLDERS = {
    "<redacted>",
    "[redacted]",
    "redacted",
    "synthetic-placeholder",
    "synthetic-sensitive-value",
    "synthetic-bearer-value",
    "personal_access_token",
}
ANGLE_PLACEHOLDER = re.compile(r"^<[A-Z][A-Z0-9_-]{2,63}>$")
SAFE_PRIVATE_KEY = "-----" + "BEGIN PRIVATE KEY-----\nsynthetic\n-----" + "END PRIVATE KEY-----"


def decode_assignment_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        if value[0] == '"':
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return value[1:-1]
    return value


def is_safe_placeholder(value: object) -> bool:
    if value is None or isinstance(value, bool):
        return True
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    return stripped.lower() in SAFE_PLACEHOLDERS or bool(ANGLE_PLACEHOLDER.fullmatch(stripped))


def json_secret_assignments(value: object, under_secret_key: bool = False) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            secret_context = under_secret_key or bool(SECRET_KEY.search(str(key)))
            if json_secret_assignments(item, secret_context):
                return True
    elif isinstance(value, list):
        return any(json_secret_assignments(item, under_secret_key) for item in value)
    elif under_secret_key:
        return len(str(value)) >= 16 and not is_safe_placeholder(value)
    return False


def scan_paths(paths: list[Path], root: Path) -> list[str]:
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(root)
        if path.suffix.lower() == ".json":
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None
            if parsed is not None and json_secret_assignments(parsed):
                errors.append(f"possible secret assignment: {relative}")
                continue
        bearer_matches = [match.group("value") for match in BEARER.finditer(text)]
        if any(not is_safe_placeholder(value) for value in bearer_matches):
            errors.append(f"possible bearer credential: {relative}")
            continue
        key_matches = [match.group(0) for match in PRIVATE_KEY.finditer(text)]
        if any(value != SAFE_PRIVATE_KEY for value in key_matches):
            errors.append(f"possible private key: {relative}")
            continue
        for match in SECRET_ASSIGNMENT.finditer(text):
            raw_value = match.group("value")
            if path.suffix.lower() in {".py", ".js", ".cjs", ".mjs", ".ts", ".tsx"}:
                if not raw_value.startswith(('"', "'")):
                    continue
            value = decode_assignment_value(raw_value)
            if is_safe_placeholder(value):
                continue
            if len(value) >= 16:
                errors.append(f"possible secret assignment: {relative}")
                break
    return errors
