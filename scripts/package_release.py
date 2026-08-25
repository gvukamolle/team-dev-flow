#!/usr/bin/env python3
"""Build a deterministic plugin archive and SHA-256 checksum."""

from __future__ import annotations

import hashlib
import gzip
import json
import tarfile
from pathlib import Path

try:
    from scripts.release_inventory import collect_inventory
    from scripts.secret_scan import scan_paths
except ModuleNotFoundError:  # Direct execution from scripts/.
    from release_inventory import collect_inventory
    from secret_scan import scan_paths


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main() -> int:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    name = manifest["name"]
    version = manifest["version"]
    DIST.mkdir(exist_ok=True)
    archive = DIST / f"{name}-{version}.tar.gz"

    files = collect_inventory(ROOT)
    secret_errors = scan_paths(files, ROOT)
    if secret_errors:
        raise SystemExit("Refusing to package unsafe inventory:\n- " + "\n- ".join(secret_errors))
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as bundle:
                for path in files:
                    arcname = Path(f"{name}-{version}") / path.relative_to(ROOT)
                    info = bundle.gettarinfo(str(path), arcname=str(arcname))
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    info.mode = 0o755 if info.mode & 0o111 else 0o644
                    with path.open("rb") as source:
                        bundle.addfile(info, source)

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(archive)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
