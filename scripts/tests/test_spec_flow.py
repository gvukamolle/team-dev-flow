import unittest

from scripts.spec_flow import consistency_errors, transition_errors


def sample_spec(status="draft"):
    return {
        "artifact_kind": "spec",
        "spec_type": "feature",
        "status": status,
        "in_scope": ["provider-neutral contracts"],
        "acceptance_criteria": [{"id": "AC-01", "text": "works", "verification": "tests"}],
        "design": {"decisions": [{"id": "DES-01", "text": "Use adapter boundary"}], "interfaces": []},
        "open_questions": [],
        "tasks": [],
        "verification": [],
    }


class SpecFlowTests(unittest.TestCase):
    def test_ready_requires_closed_questions_and_acceptance_criteria(self):
        value = sample_spec()
        value["open_questions"] = ["Which provider?"]
        value["acceptance_criteria"] = []
        errors = transition_errors(value, "ready")
        self.assertTrue(any("open_questions" in error for error in errors))
        self.assertTrue(any("acceptance_criteria" in error for error in errors))

    def test_verifying_can_finish_only_with_tasks_and_evidence_complete(self):
        value = sample_spec("verifying")
        value["tasks"] = [{"ref": "local:task-1", "kind": "implementation", "status": "active", "acceptance_refs": ["AC-01"], "design_refs": ["DES-01"]}]
        errors = transition_errors(value, "done")
        self.assertTrue(any("unfinished tasks" in error for error in errors))
        self.assertTrue(any("verification evidence" in error for error in errors))
        value["tasks"][0]["status"] = "done"
        value["verification"] = ["tests pass at SHA abc"]
        self.assertEqual(transition_errors(value, "done"), [])

    def test_disallows_skipping_from_draft_to_active(self):
        self.assertTrue(transition_errors(sample_spec(), "active"))

    def test_active_requires_acceptance_and_design_traceability(self):
        value = sample_spec("ready")
        value["tasks"] = [{"ref": "local:task-1", "kind": "implementation", "status": "ready", "acceptance_refs": [], "design_refs": []}]
        errors = transition_errors(value, "active")
        self.assertTrue(any("acceptance criteria without a Task" in error for error in errors))
        self.assertTrue(any("design decisions without a Task" in error for error in errors))

    def test_research_spec_cannot_authorize_production_implementation(self):
        value = sample_spec("ready")
        value["spec_type"] = "research"
        value["tasks"] = [{"ref": "local:task-1", "kind": "implementation", "status": "ready", "acceptance_refs": ["AC-01"], "design_refs": ["DES-01"]}]
        self.assertTrue(any("Research Spec" in error for error in consistency_errors(value)))

    def test_cancelled_tasks_do_not_satisfy_active_traceability(self):
        value = sample_spec("ready")
        value["tasks"] = [{"ref": "local:task-1", "kind": "implementation", "status": "cancelled", "acceptance_refs": ["AC-01"], "design_refs": ["DES-01"]}]
        self.assertTrue(any("at least one Task" in error for error in transition_errors(value, "active")))


if __name__ == "__main__":
    unittest.main()
