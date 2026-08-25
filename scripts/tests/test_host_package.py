import tempfile
import unittest
from pathlib import Path

from scripts.host_package import ROOT, check_host, install_kilo
from scripts.local_task_store import StoreError


class HostPackageTests(unittest.TestCase):
    def workspace(self, root: str) -> Path:
        path = Path(root) / "project"
        path.mkdir()
        return path

    def test_preview_then_install_check_and_idempotent_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.workspace(tmp)
            preview = install_kilo(workspace, preview=True)
            self.assertGreater(len(preview["changed"]), 10)
            self.assertFalse((workspace / ".kilo").exists())
            result = install_kilo(workspace)
            self.assertTrue(result["verified"])
            self.assertEqual(check_host(workspace), [])
            self.assertTrue((workspace / ".kilo/agents/team-dev-flow.md").is_file())
            self.assertTrue((workspace / ".team-dev-flow/plugin/skills/index/SKILL.md").is_file())
            self.assertEqual(install_kilo(workspace)["changed"], 0)

    def test_refuses_unowned_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.workspace(tmp)
            target = workspace / ".kilo/agents/team-dev-flow.md"
            target.parent.mkdir(parents=True)
            target.write_text("mine", encoding="utf-8")
            with self.assertRaisesRegex(StoreError, "unowned"):
                install_kilo(workspace)
            self.assertEqual(target.read_text(encoding="utf-8"), "mine")

    def test_detects_owned_file_drift_and_refuses_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.workspace(tmp)
            install_kilo(workspace)
            target = workspace / ".kilo/rules/team-dev-flow.md"
            target.write_text("changed", encoding="utf-8")
            self.assertIn("installed file drift", check_host(workspace)[0])
            with self.assertRaisesRegex(StoreError, "drifted"):
                install_kilo(workspace)

    def test_failure_rolls_back_every_written_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.workspace(tmp)
            with self.assertRaisesRegex(RuntimeError, "injected"):
                install_kilo(workspace, fail_after=2)
            files = [path for path in workspace.rglob("*") if path.is_file()]
            self.assertEqual(files, [])
            self.assertEqual(check_host(workspace), ["host package is not installed"])

    def test_rejects_symlinked_install_path(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            workspace = self.workspace(tmp)
            (workspace / ".kilo").symlink_to(Path(outside), target_is_directory=True)
            with self.assertRaisesRegex(StoreError, "symlink"):
                install_kilo(workspace)


if __name__ == "__main__":
    unittest.main()
