import json
import subprocess
import unittest

from scripts.github_adapter import (
    GitHubAdapterError,
    normalize_issue,
    preview_issue,
    preview_pull_request,
    read_issue,
    validate_repository,
)


class Result:
    def __init__(self, value, returncode=0):
        self.returncode = returncode
        self.stdout = json.dumps(value)
        self.stderr = ""


class GitHubAdapterTests(unittest.TestCase):
    def test_reads_and_normalizes_a_bounded_issue(self):
        calls = []
        def runner(argv, **kwargs):
            calls.append((argv, kwargs))
            return Result({
                "number": 17, "title": "Portable flow", "body": "Scope", "state": "OPEN",
                "labels": [{"name": "feature"}], "assignees": [{"login": "owner"}],
                "milestone": {"title": "M4"}, "url": "https://github.com/acme/flow/issues/17",
                "updatedAt": "2026-08-25T10:00:00Z",
            })
        value = read_issue("acme/flow", 17, runner)
        self.assertEqual(value["ref"], "github:acme/flow:17")
        self.assertEqual(value["status"]["category"], "backlog")
        self.assertEqual(value["metadata"]["assignees"], ["owner"])
        self.assertEqual(calls[0][0][:4], ["gh", "issue", "view", "17"])
        self.assertEqual(calls[0][1]["timeout"], 20)

    def test_normalizer_truncates_oversized_bodies_explicitly(self):
        value = normalize_issue("acme/flow", {
            "number": 1, "title": "Large", "body": "x" * 100_100, "state": "CLOSED",
            "labels": [], "assignees": [], "url": None,
        })
        self.assertTrue(value["metadata"]["body_truncated"])
        self.assertIn("[truncated by Team Dev Flow]", value["body"])
        self.assertEqual(value["status"]["category"], "done")

    def test_issue_preview_is_argv_not_a_shell_command_and_cannot_authorize(self):
        value = preview_issue("acme/flow", "Add adapter", "Body with $() and `ticks`")
        self.assertEqual(value["argv"][0:3], ["gh", "issue", "create"])
        self.assertEqual(value["stdin"], "Body with $() and `ticks`")
        self.assertFalse(value["mutation_available"])
        self.assertTrue(value["confirmation_required"])
        self.assertNotIn("confirmation_digest", value)

    def test_pr_preview_requires_exact_current_sha(self):
        sha = "a" * 40
        value = preview_pull_request("acme/flow", "main", "feature/FLOW-1", "Title", "Body", sha, sha)
        self.assertEqual(value["source_sha"], sha)
        self.assertIn("--body-file", value["argv"])
        with self.assertRaisesRegex(GitHubAdapterError, "does not match"):
            preview_pull_request("acme/flow", "main", "feature/FLOW-1", "Title", "Body", sha, "b" * 40)

    def test_rejects_unsafe_repositories_branches_and_cli_errors(self):
        for value in ("repo", "../repo", "owner/repo/extra", "owner/.."):
            with self.subTest(value=value):
                with self.assertRaises(GitHubAdapterError):
                    validate_repository(value)
        with self.assertRaisesRegex(GitHubAdapterError, "invalid head"):
            preview_pull_request("acme/flow", "main", "../../bad", "Title", "Body", "a" * 40, "a" * 40)
        def failed(argv, **kwargs):
            return Result({}, returncode=1)
        with self.assertRaisesRegex(GitHubAdapterError, "request failed"):
            read_issue("acme/flow", 1, failed)

    def test_runner_timeout_is_fail_closed_without_stderr_echo(self):
        def timeout(argv, **kwargs):
            raise subprocess.TimeoutExpired(argv, 20, stderr="token=secret")
        with self.assertRaisesRegex(GitHubAdapterError, "TimeoutExpired") as raised:
            read_issue("acme/flow", 1, timeout)
        self.assertNotIn("secret", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
