#!/usr/bin/env python3
"""Redact secret-valued key/value pairs without printing the original value."""

from __future__ import annotations

import re
import sys

SECRET_KEY = re.compile(
    r"(token|secret|password|api[_-]?key|authorization|cookie|credential)",
    re.IGNORECASE,
)
ASSIGNMENT = re.compile(
    r"^(?P<prefix>\s*(?P<key>[A-Za-z0-9_.-]+)\s*[:=]\s*)(?P<value>.*)$"
)
EMBEDDED_ASSIGNMENT = re.compile(
    r"(?P<prefix>[\"']?(?:personal_access_token|api[_-]?key|token|secret|password|authorization|cookie|credential)[A-Za-z0-9_.-]*[\"']?\s*[:=]\s*)"
    r"(?:\"[^\"\r\n]*\"|'[^'\r\n]*'|[^\s,;}\]\r\n]+)",
    re.IGNORECASE,
)
BEARER = re.compile(
    r"(?P<prefix>authorization\s*[:=]\s*)?bearer\s+[A-Za-z0-9._~+/-]+",
    re.IGNORECASE,
)
PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    re.DOTALL,
)


def redact_text(text: str) -> str:
    text = PRIVATE_KEY.sub("<redacted-private-key>", text)
    text = BEARER.sub(lambda match: f'{match.group("prefix") or ""}Bearer <redacted>', text)
    return EMBEDDED_ASSIGNMENT.sub(lambda match: f'{match.group("prefix")}<redacted>', text)


def redact_line(line: str) -> str:
    match = ASSIGNMENT.match(line.rstrip("\n"))
    if not match or not SECRET_KEY.search(match.group("key")):
        return redact_text(line)
    newline = "\n" if line.endswith("\n") else ""
    return f'{match.group("prefix")}<redacted>{newline}'


def main() -> int:
    sys.stdout.write(redact_text(sys.stdin.read()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
