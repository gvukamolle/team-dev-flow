import tempfile
import unittest
from pathlib import Path

from scripts.release_inventory import collect_inventory


class ReleaseInventoryUniversalTests(unittest.TestCase):
    def test_inventory_is_explicit_and_contains_universal_runtime(self):
        root = Path(__file__).resolve().parents[2]
        relative = {path.relative_to(root).as_posix() for path in collect_inventory(root)}
        self.assertIn("scripts/local_task_store.py", relative)
        self.assertIn("scripts/github_adapter.py", relative)
        self.assertIn("host-packages/kilo/skills/team-dev-flow/SKILL.md", relative)
        self.assertNotIn(".mcp.json", relative)

    def test_rejects_unlisted_or_unsafe_inventory_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "packaging").mkdir()
            (root / "packaging/release-files.json").write_text(
                '{"include_files":["missing.md"],"include_trees":[],"allowed_suffixes":[".md"],"denied_names":[],"denied_suffixes":[]}',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                collect_inventory(root)


if __name__ == "__main__":
    unittest.main()
