import json
import tempfile
import unittest
from pathlib import Path

from scripts.secret_scan import scan_paths


class SecretScanTests(unittest.TestCase):
    def scan_json(self, value):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "probe.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            return scan_paths([path], root)

    def test_detects_quoted_and_nested_json_secret_keys(self):
        token_value = "abcdefghijkl" + "mnopqrstuvwx"
        errors = self.scan_json({"outer": {"personal_access_token": token_value}})
        self.assertEqual(errors, ["possible secret assignment: probe.json"])

    def test_example_substring_is_not_a_placeholder_bypass(self):
        token_value = "prefix" + "example" + "realcredentialvalue"
        errors = self.scan_json({"api_key": token_value})
        self.assertEqual(errors, ["possible secret assignment: probe.json"])

    def test_exact_documented_placeholder_is_allowed(self):
        self.assertEqual(self.scan_json({"personal_access_token": "<INSERT_LOCALLY>"}), [])

    def test_detects_scalar_nested_under_secret_json_key(self):
        token_value = "abcdefghijkl" + "mnopqrstuvwx"
        errors = self.scan_json({"personal_access_token": {"value": token_value}})
        self.assertEqual(errors, ["possible secret assignment: probe.json"])

    def test_nested_secret_json_wrapper_allows_exact_placeholder(self):
        self.assertEqual(
            self.scan_json({"personal_access_token": {"value": "<INSERT_LOCALLY>"}}),
            [],
        )

    def test_detects_indented_yaml_secret_assignment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "probe.yaml"
            value = "abcdefghijkl" + "mnopqrstuvwx"
            path.write_text("service:\n  personal_access_token: " + value + "\n", encoding="utf-8")
            self.assertEqual(scan_paths([path], root), ["possible secret assignment: probe.yaml"])

    def test_indented_yaml_safe_counterexample_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "probe.yaml"
            path.write_text("service:\n  base_url: https://jira.example.local\n", encoding="utf-8")
            self.assertEqual(scan_paths([path], root), [])

    def test_detects_bearer_and_private_key_without_printing_value(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bearer_path = root / "header.txt"
            bearer_path.write_text("Authorization: Bearer " + ("a" * 24), encoding="utf-8")
            key_path = root / "key.txt"
            key_path.write_text(
                "-----" + "BEGIN PRIVATE KEY-----\n" + ("b" * 32) + "\n-----" + "END PRIVATE KEY-----",
                encoding="utf-8",
            )
            errors = scan_paths([bearer_path, key_path], root)
            self.assertEqual(
                errors,
                ["possible bearer credential: header.txt", "possible private key: key.txt"],
            )


if __name__ == "__main__":
    unittest.main()
