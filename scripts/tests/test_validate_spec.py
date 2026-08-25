import unittest

from scripts.validate_spec import spec_hash, validate


def sample_spec():
    value = {
        "schema_version": "team-dev-flow/spec/v1",
        "id": "feature-1",
        "artifact_kind": "spec",
        "spec_type": "feature",
        "title": "Feature",
        "status": "ready",
        "parent_refs": ["local_markdown:vault:epic-1"],
        "problem": "Current flow is provider-specific",
        "outcome": "One core supports task adapters",
        "in_scope": ["contracts"],
        "out_of_scope": ["remote writes"],
        "acceptance_criteria": [{"id": "AC-01", "text": "Spec validates", "verification": "unit test"}],
        "design": {"decisions": [], "interfaces": []},
        "constraints": ["preserve Jira"],
        "risks": [],
        "open_questions": [],
        "tasks": [],
        "source_refs": [],
        "revision": {"updated": "2026-08-25", "content_hash": "a" * 64},
        "verification": [],
        "spec_hash": "",
    }
    value["spec_hash"] = spec_hash(value)
    return value


class ValidateSpecTests(unittest.TestCase):
    def test_valid_spec_hash(self):
        self.assertEqual(validate(sample_spec()), [])

    def test_detects_spec_drift(self):
        value = sample_spec()
        value["outcome"] = "Changed"
        self.assertTrue(any("spec_hash mismatch" in error for error in validate(value)))


if __name__ == "__main__":
    unittest.main()
