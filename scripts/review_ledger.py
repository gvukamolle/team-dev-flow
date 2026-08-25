#!/usr/bin/env python3
"""Record SHA-bound review passes and compute PASS from evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ModuleNotFoundError as exc:
    raise SystemExit("jsonschema is required; install requirements.txt") from exc


ROOT = Path(__file__).resolve().parents[1]
DISPOSITION_SCHEMA = json.loads((ROOT / "contracts/review-disposition.schema.json").read_text(encoding="utf-8"))
LEDGER_SCHEMAS = {
    "team-dev-flow/review-ledger/v1": json.loads((ROOT / "contracts/review-ledger.schema.json").read_text(encoding="utf-8")),
    "team-dev-flow/review-ledger/v2": json.loads((ROOT / "contracts/review-ledger-v2.schema.json").read_text(encoding="utf-8")),
}
VERIFICATION_SCHEMAS = {
    "team-dev-flow/verification-report/v1": json.loads((ROOT / "contracts/verification-report.schema.json").read_text(encoding="utf-8")),
    "team-dev-flow/verification-report/v2": json.loads((ROOT / "contracts/verification-report-v2.schema.json").read_text(encoding="utf-8")),
}
PASS_INPUT_SCHEMAS = {
    "v1": json.loads((ROOT / "contracts/review-pass-input.schema.json").read_text(encoding="utf-8")),
    "v2": json.loads((ROOT / "contracts/review-pass-input-v2.schema.json").read_text(encoding="utf-8")),
}
SCHEMA_REGISTRY = Registry()
for schema in (*VERIFICATION_SCHEMAS.values(), DISPOSITION_SCHEMA, *PASS_INPUT_SCHEMAS.values(), *LEDGER_SCHEMAS.values()):
    SCHEMA_REGISTRY = SCHEMA_REGISTRY.with_resource(schema["$id"], Resource.from_contents(schema))
LEDGER_VALIDATORS = {version: Draft202012Validator(schema, registry=SCHEMA_REGISTRY) for version, schema in LEDGER_SCHEMAS.items()}
VERIFICATION_VALIDATORS = {version: Draft202012Validator(schema) for version, schema in VERIFICATION_SCHEMAS.items()}
PASS_INPUT_VALIDATORS = {version: Draft202012Validator(schema, registry=SCHEMA_REGISTRY) for version, schema in PASS_INPUT_SCHEMAS.items()}
FULL_SHA = re.compile(r"^(?:[a-f0-9]{40}|[a-f0-9]{64})$")
BLOCKING_SEVERITIES = {"P0", "P1", "P2"}


def load(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": "team-dev-flow/review-ledger/v1", "passes": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_ledger(data)
    return data


def save(path: Path, data: dict) -> None:
    validate_ledger(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_ledger(data: dict) -> None:
    validator = LEDGER_VALIDATORS.get(data.get("schema_version"))
    if validator is None:
        raise ValueError(f"unsupported ledger schema_version: {data.get('schema_version')!r}")
    errors = sorted(validator.iter_errors(data), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "$"
        raise ValueError(f"ledger schema {location}: {first.message}")


def validate_verification_report(report: dict) -> None:
    validator = VERIFICATION_VALIDATORS.get(report.get("schema_version"))
    if validator is None:
        raise ValueError(f"unsupported verification schema_version: {report.get('schema_version')!r}")
    errors = sorted(validator.iter_errors(report), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "$"
        raise ValueError(f"verification report schema {location}: {first.message}")
    if report["result"] == "PASS" and any(check["result"] != "pass" for check in report["checks"]):
        raise ValueError("PASS verification report may contain only passing checks")


def validate_review_packet(packet: dict) -> None:
    validator = PASS_INPUT_VALIDATORS["v2" if "scope_ref" in packet else "v1"]
    errors = sorted(validator.iter_errors(packet), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "$"
        raise ValueError(f"review packet schema {location}: {first.message}")


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_findings(findings: list[dict]) -> list[dict]:
    normalized = json.loads(json.dumps(findings, ensure_ascii=False))
    for finding in normalized:
        disagreement = finding.get("disagreement")
        if disagreement is None:
            continue
        claim = " ".join(disagreement.get("claim", "").split())
        evidence = sorted({" ".join(item.split()) for item in disagreement["evidence"]})
        disagreement["claim"] = claim
        disagreement["evidence"] = evidence
        disagreement["fingerprint"] = canonical_hash({"claim": claim})
        disagreement["evidence_revision"] = canonical_hash(evidence)
    return normalized


def finding_resolved(finding: dict, reviewed_sha: str) -> bool:
    status = finding["status"]
    if status == "needs_evidence":
        return False
    if status == "accepted":
        return finding.get("resolution_sha") == reviewed_sha and bool(finding.get("verification"))
    if status == "deferred":
        return finding["scope"] != "in_scope" and bool(finding.get("follow_up_ticket") or finding.get("follow_up_ref"))
    return status in {"rejected_with_reason", "duplicate"} and bool(finding.get("resolution"))


def repeated_without_new_evidence(finding: dict, prior_passes: list[dict]) -> bool:
    disagreement = finding.get("disagreement")
    if (
        finding.get("status") != "needs_evidence"
        or finding.get("scope") != "in_scope"
        or finding.get("severity") not in BLOCKING_SEVERITIES
        or not disagreement
    ):
        return False
    identity = (disagreement["fingerprint"], disagreement["evidence_revision"])
    for prior in prior_passes:
        for old in prior.get("findings", []):
            old_disagreement = old.get("disagreement")
            if (
                old.get("status") != "needs_evidence"
                or old.get("scope") != "in_scope"
                or old.get("severity") not in BLOCKING_SEVERITIES
                or not old_disagreement
            ):
                continue
            if (old_disagreement["fingerprint"], old_disagreement["evidence_revision"]) == identity:
                return True
    return False


def compute_result(packet: dict, pass_number: int, prior_passes: list[dict]) -> tuple[str, list[str]]:
    errors: list[str] = []
    sha = packet.get("reviewed_sha", "")
    if not FULL_SHA.fullmatch(sha):
        errors.append("reviewed_sha must be a full 40- or 64-character SHA")
    verification = packet.get("verification_report") or {}
    if verification.get("verified_sha") != sha:
        errors.append("verification report is bound to a different SHA")
    if verification.get("result") != "PASS":
        errors.append("verification report is not PASS")
    binding_field = "scope_ref" if "scope_ref" in packet else "ticket"
    revision_field = "source_revision" if "source_revision" in packet else "jira_revision"
    if verification.get(binding_field) != packet.get(binding_field):
        errors.append(f"verification report is bound to a different {binding_field}")
    if verification.get("contract_hash") != packet.get("contract_hash"):
        errors.append("verification report is bound to a different contract")
    if verification.get(revision_field) != packet.get(revision_field):
        label = "Jira revision" if revision_field == "jira_revision" else "source revision"
        errors.append(f"verification report is bound to a different {label}")
    if packet.get("contract_drift") is not False:
        errors.append("contract drift is unresolved")
    for finding in packet.get("findings", []):
        if finding.get("scope") == "in_scope" and finding.get("severity") in BLOCKING_SEVERITIES:
            if not finding_resolved(finding, sha):
                errors.append(f"blocking finding {finding.get('finding_id')} is unresolved")
    repeated = [
        finding.get("finding_id") for finding in packet.get("findings", [])
        if repeated_without_new_evidence(finding, prior_passes)
    ]
    if repeated:
        errors.append(f"evidence-free disagreement repeated: {', '.join(repeated)}")
    if errors and (pass_number >= 5 or repeated):
        return "ESCALATE", errors
    return ("REQUEST_CHANGES", errors) if errors else ("PASS", [])


def record_pass(ledger: dict, packet: dict) -> dict:
    if len(ledger["passes"]) >= 5:
        raise ValueError("review pass limit reached; escalate to the task owner")
    validate_review_packet(packet)
    validate_verification_report(packet["verification_report"])
    packet = dict(packet)
    packet["findings"] = normalize_findings(packet["findings"])
    provider_neutral = "scope_ref" in packet
    expected_ledger_version = "team-dev-flow/review-ledger/v2" if provider_neutral else "team-dev-flow/review-ledger/v1"
    if not ledger["passes"]:
        ledger["schema_version"] = expected_ledger_version
    elif ledger.get("schema_version") != expected_ledger_version:
        raise ValueError("review ledger binding version does not match the review packet")
    pass_number = len(ledger["passes"]) + 1
    result, reasons = compute_result(packet, pass_number, ledger["passes"])
    binding_field = "scope_ref" if provider_neutral else "ticket"
    revision_field = "source_revision" if provider_neutral else "jira_revision"
    entry = {
        "pass": pass_number,
        binding_field: packet[binding_field],
        "reviewed_sha": packet["reviewed_sha"],
        "contract_hash": packet["contract_hash"],
        revision_field: packet[revision_field],
        "contract_drift": packet["contract_drift"],
        "verification_report": packet["verification_report"],
        "findings": packet["findings"],
        "result": result,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    ledger["passes"].append(entry)
    validate_ledger(ledger)
    return {"result": result, "reasons": reasons, "pass": pass_number}


def check_current(
    ledger: dict,
    sha: str,
    contract_hash: str,
    source_updated: str,
    source_content_hash: str,
) -> list[str]:
    if not ledger["passes"]:
        return ["no review pass recorded"]
    latest = ledger["passes"][-1]
    expected = {
        "result": "PASS",
        "reviewed_sha": sha,
        "contract_hash": contract_hash,
    }
    errors = [f"latest {key} does not match current value" for key, value in expected.items() if latest.get(key) != value]
    revision = latest.get("source_revision") or latest.get("jira_revision") or {}
    if revision.get("updated") != source_updated or revision.get("content_hash") != source_content_hash:
        errors.append("latest PASS does not match the current source revision")
    if latest.get("contract_drift") is not False:
        errors.append("latest PASS contains contract drift")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add-pass")
    add.add_argument("ledger", type=Path)
    add.add_argument("--packet", type=Path, required=True)
    check = sub.add_parser("check-current")
    check.add_argument("ledger", type=Path)
    check.add_argument("--sha", required=True)
    check.add_argument("--contract-hash", required=True)
    check.add_argument("--source-updated", "--jira-updated", dest="source_updated", required=True)
    check.add_argument("--source-content-hash", "--jira-content-hash", dest="source_content_hash", required=True)
    args = parser.parse_args()
    try:
        ledger = load(args.ledger)
        if args.command == "add-pass":
            packet = json.loads(args.packet.read_text(encoding="utf-8"))
            outcome = record_pass(ledger, packet)
            save(args.ledger, ledger)
            print(json.dumps(outcome, ensure_ascii=False))
            return 0 if outcome["result"] == "PASS" else 1
        errors = check_current(
            ledger, args.sha, args.contract_hash, args.source_updated, args.source_content_hash
        )
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        print("Review ledger: current SHA and source revision have PASS")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
