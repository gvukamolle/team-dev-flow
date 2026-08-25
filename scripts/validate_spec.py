#!/usr/bin/env python3
"""Validate a Team Dev Flow Spec and verify its canonical hash."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError as exc:
    raise SystemExit("jsonschema is required for Spec validation; install requirements.txt") from exc


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "contracts" / "spec.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


def canonical_payload(spec: dict) -> bytes:
    payload = dict(spec)
    payload.pop("spec_hash", None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def spec_hash(spec: dict) -> str:
    return hashlib.sha256(canonical_payload(spec)).hexdigest()


def validate(spec: dict) -> list[str]:
    errors = []
    for schema_error in sorted(VALIDATOR.iter_errors(spec), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in schema_error.absolute_path) or "$"
        errors.append(f"schema {location}: {schema_error.message}")
    expected = spec_hash(spec)
    if spec.get("spec_hash") != expected:
        errors.append(f"spec_hash mismatch; expected {expected}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--print-hash", action="store_true")
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    if args.print_hash:
        print(spec_hash(spec))
        return 0
    errors = validate(spec)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Spec: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
