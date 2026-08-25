import tempfile
import unittest
from pathlib import Path

from scripts.local_task_store import StoreError, init_store, upsert_artifact


class LocalTaskStoreUniversalTests(unittest.TestCase):
    def test_creates_and_updates_a_task_idempotently(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            vault.mkdir()
            root = init_store(vault, "Projects/Flow")
            upsert_artifact(root, project="FLOW", kind="project", identifier="FLOW", title="Flow")
            first = upsert_artifact(root, project="FLOW", kind="task", identifier="TASK-1", title="First task", status="active")
            second = upsert_artifact(root, project="FLOW", kind="task", identifier="TASK-1", title="First task", status="active")
            self.assertEqual(first, second)
            self.assertTrue(first.is_file())
            self.assertTrue((root / "Dashboard.base").is_file())

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            vault.mkdir()
            with self.assertRaises(StoreError):
                init_store(vault, "../outside")


if __name__ == "__main__":
    unittest.main()
