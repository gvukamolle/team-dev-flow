#!/usr/bin/env python3
"""Deterministic Agentic SDD lifecycle checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TRANSITIONS = {
    "draft": {"clarifying", "ready", "superseded"},
    "clarifying": {"draft", "ready", "superseded"},
    "ready": {"active", "clarifying", "superseded"},
    "active": {"clarifying", "verifying", "superseded"},
    "verifying": {"active", "clarifying", "done", "superseded"},
    "done": {"superseded"},
    "superseded": set(),
}


def consistency_errors(spec: dict) -> list[str]:
    """Check traceability across acceptance, design, and executable tasks."""
    if spec.get("artifact_kind") != "spec":
        return []
    errors: list[str] = []
    acceptance_ids = {item.get("id") for item in spec.get("acceptance_criteria", []) if item.get("id")}
    design_ids = {item.get("id") for item in spec.get("design", {}).get("decisions", []) if item.get("id")}
    tasks = [task for task in spec.get("tasks", []) if task.get("status") != "cancelled"]
    if not tasks:
        errors.append("at least one Task is required before implementation")
        return errors
    acceptance_refs = {ref for task in tasks for ref in task.get("acceptance_refs", [])}
    design_refs = {ref for task in tasks for ref in task.get("design_refs", [])}
    unknown_acceptance = sorted(acceptance_refs - acceptance_ids)
    unknown_design = sorted(design_refs - design_ids)
    uncovered_acceptance = sorted(acceptance_ids - acceptance_refs)
    uncovered_design = sorted(design_ids - design_refs)
    if unknown_acceptance:
        errors.append(f"Tasks reference unknown acceptance criteria: {', '.join(unknown_acceptance)}")
    if unknown_design:
        errors.append(f"Tasks reference unknown design decisions: {', '.join(unknown_design)}")
    if uncovered_acceptance:
        errors.append(f"acceptance criteria without a Task: {', '.join(uncovered_acceptance)}")
    if uncovered_design:
        errors.append(f"design decisions without a Task: {', '.join(uncovered_design)}")
    if spec.get("spec_type") == "research":
        production_tasks = [task.get("ref", "<unknown>") for task in tasks if task.get("kind") == "implementation"]
        if production_tasks:
            errors.append(f"Research Spec cannot authorize implementation Tasks: {', '.join(production_tasks)}")
    return errors


def transition_errors(spec: dict, target: str) -> list[str]:
    current = spec.get("status")
    errors: list[str] = []
    if target not in TRANSITIONS.get(current, set()):
        errors.append(f"transition {current!r} -> {target!r} is not allowed")
        return errors
    if target in {"ready", "active"}:
        if spec.get("open_questions"):
            errors.append("open_questions must be empty before a spec becomes ready")
        if not spec.get("acceptance_criteria"):
            errors.append("acceptance_criteria are required before a spec becomes ready")
        if not spec.get("in_scope"):
            errors.append("in_scope must be non-empty before a spec becomes ready")
    if target == "active":
        errors.extend(consistency_errors(spec))
    if target == "done":
        unfinished = [task.get("ref", "<unknown>") for task in spec.get("tasks", []) if task.get("status") not in {"done", "cancelled"}]
        if unfinished:
            errors.append(f"unfinished tasks prevent completion: {', '.join(unfinished)}")
        if not spec.get("verification"):
            errors.append("verification evidence is required before completion")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("target")
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    errors = transition_errors(spec, args.target)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Spec transition: allowed ({spec.get('status')} -> {args.target})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
