import tempfile
import unittest
from pathlib import Path

from scripts.github_marketplace import generate, load, promote, release, rollback, set_canary, verify
from scripts.local_task_store import StoreError


class GitHubMarketplaceTests(unittest.TestCase):
    def test_generate_verify_update_promote_and_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "marketplace"
            generate(root, "owner", "team-dev-flow", "team-flow", "0.3.0-dev.1", "a" * 40, "1" * 64, "private", "UNLICENSED")
            self.assertEqual(verify(root), [])
            promote(root)
            set_canary(root, release("0.3.0-dev.2", "b" * 40, "2" * 64))
            promote(root)
            self.assertEqual(load(root, "channels/stable.json")["current"]["git_ref"], "b" * 40)
            rollback(root)
            self.assertEqual(load(root, "channels/stable.json")["current"]["git_ref"], "a" * 40)
            self.assertEqual(verify(root), [])

    def test_public_scaffold_requires_license(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(StoreError, "license"):
                generate(Path(tmp) / "market", "owner", "repo", "team", "1.0.0", "a" * 40, "1" * 64, "public", "UNLICENSED")

    def test_refuses_nonempty_output_and_mutable_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "market"
            root.mkdir()
            (root / "mine").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(StoreError, "empty"):
                generate(root, "owner", "repo", "team", "1.0.0", "a" * 40, "1" * 64, "private", "UNLICENSED")
            with self.assertRaises(StoreError):
                release("1.0.0", "main", "1" * 64)


if __name__ == "__main__":
    unittest.main()
