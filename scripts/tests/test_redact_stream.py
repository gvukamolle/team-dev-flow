import unittest

from scripts.redact_stream import redact_line, redact_text


class RedactStreamTests(unittest.TestCase):
    def test_redacts_personal_access_token(self):
        self.assertEqual(
            redact_line('personal_access_token = "value"\n'),
            "personal_access_token = <redacted>\n",
        )

    def test_redacts_nested_api_key_name(self):
        self.assertEqual(
            redact_line("service.api_key: value\n"),
            "service.api_key: <redacted>\n",
        )

    def test_preserves_safe_line(self):
        self.assertEqual(
            redact_line('base_url = "https://jira.example"\n'),
            'base_url = "https://jira.example"\n',
        )

    def test_redacts_embedded_json_and_header_values(self):
        original = 'comment {"personal_access_token":"synthetic-sensitive-value"} Authorization: Bearer synthetic-bearer-value'
        result = redact_text(original)
        self.assertNotIn("synthetic-sensitive-value", result)
        self.assertNotIn("synthetic-bearer-value", result)
        self.assertIn("<redacted>", result)

    def test_redacts_multiline_private_key(self):
        private_key = "-----" + "BEGIN PRIVATE KEY-----\nsynthetic\n-----" + "END PRIVATE KEY-----"
        result = redact_text("before\n" + private_key + "\nafter")
        self.assertNotIn("synthetic", result)
        self.assertIn("<redacted-private-key>", result)


if __name__ == "__main__":
    unittest.main()
