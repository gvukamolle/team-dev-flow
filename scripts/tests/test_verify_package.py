import gzip
import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.verify_package import verify_archive


class VerifyPackageTests(unittest.TestCase):
    def make_root(self, directory: str) -> Path:
        root = Path(directory)
        (root / ".codex-plugin").mkdir()
        (root / "packaging").mkdir()
        (root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "probe", "version": "1.0.0"}), encoding="utf-8"
        )
        (root / "packaging" / "release-files.json").write_text(
            json.dumps({
                "schema_version": "team-dev-flow/release-files/v1",
                "include_files": ["README.md"],
                "include_trees": [],
                "allowed_suffixes": [".md"],
                "denied_names": [".env"],
                "denied_suffixes": [".token"],
            }),
            encoding="utf-8",
        )
        (root / "README.md").write_text("reviewed bytes\n", encoding="utf-8")
        return root

    def make_archive(self, root: Path, payloads: list[bytes]) -> Path:
        archive = root / "probe-1.0.0.tar.gz"
        with archive.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as bundle:
                    for payload in payloads:
                        info = tarfile.TarInfo("probe-1.0.0/README.md")
                        info.size = len(payload)
                        info.uid = info.gid = 0
                        info.uname = info.gname = ""
                        info.mtime = 0
                        info.mode = 0o644
                        bundle.addfile(info, io.BytesIO(payload))
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        archive.with_suffix(archive.suffix + ".sha256").write_text(
            f"{digest}  {archive.name}\n", encoding="utf-8"
        )
        return archive

    def test_valid_archive_matches_reviewed_source_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            archive = self.make_archive(root, [(root / "README.md").read_bytes()])
            count, _ = verify_archive(archive, root)
            self.assertEqual(count, 1)

    def test_rejects_tampered_content_even_with_recomputed_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            archive = self.make_archive(root, [b"TAMPERED BYTES\n"])
            with self.assertRaisesRegex(ValueError, "content mismatch"):
                verify_archive(archive, root)

    def test_rejects_duplicate_member_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            payload = (root / "README.md").read_bytes()
            archive = self.make_archive(root, [payload, payload])
            with self.assertRaisesRegex(ValueError, "duplicate package members"):
                verify_archive(archive, root)


if __name__ == "__main__":
    unittest.main()
