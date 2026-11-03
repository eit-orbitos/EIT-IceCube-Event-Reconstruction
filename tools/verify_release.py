#!/usr/bin/env python3
"""Independent hash-path-CRC verifier. Does not certify scientific validity."""
from __future__ import annotations
import argparse
import hashlib
import json
import tempfile
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZIP_STORED
if __package__ in (None, ""):
    # Direct execution: python tools/<script>.py
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build_release import PROJECT, create_archive, sha256


class IntegrityError(ValueError):
    pass


def verify_archive(archive, source=None):
    archive = Path(archive).resolve()
    if not archive.is_file():
        raise IntegrityError("Archive does not exist")
    with ZipFile(archive, "r") as zf:
        infos = zf.infolist()
        names = [i.filename for i in infos]
        if not names or len(names) != len(set(names)):
            raise IntegrityError("Missing or duplicate ZIP entries")
        root_prefix = PROJECT + "/"
        rel_names = []
        for zi in infos:
            name = zi.filename
            if not name.startswith(root_prefix) or name.endswith("/"):
                raise IntegrityError("Unexpected ZIP entry/root")
            rel = name[len(root_prefix):]
            parts = PurePosixPath(rel).parts
            if not parts or any(p in ("", ".", "..") for p in parts) or "\\" in rel:
                raise IntegrityError("Unsafe ZIP path")
            if zi.compress_type != ZIP_STORED or zi.date_time != (1980, 1, 1, 0, 0, 0):
                raise IntegrityError("Noncanonical compression or timestamp")
            if zi.create_system != 3 or (zi.external_attr >> 16) != 0o100644:
                raise IntegrityError("Noncanonical UNIX permissions")
            if zi.flag_bits & 1 or zi.extra or zi.comment:
                raise IntegrityError("Encrypted, extended or commented file")
            if zi.file_size > 5_000_000:
                raise IntegrityError("Unexpected large file")
            rel_names.append(rel)
        if rel_names != sorted(rel_names):
            raise IntegrityError("Entries are not sorted")
        if zf.testzip() is not None:
            raise IntegrityError("ZIP CRC verification failed")
        actual = {rel: zf.read(root_prefix + rel) for rel in rel_names}
    if "MANIFEST.json" not in actual or "SHA256SUMS.txt" not in actual:
        raise IntegrityError("Required internal integrity records missing")
    try:
        manifest = json.loads(actual["MANIFEST.json"].decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise IntegrityError("Malformed manifest") from exc
    entries = {k: v for k, v in actual.items() if k not in ("MANIFEST.json", "SHA256SUMS.txt")}
    if manifest["project"] != PROJECT or manifest["version"] != "0.1.2":
        raise IntegrityError("Project/version mismatch")
    if manifest["payload_file_count"] != len(entries):
        raise IntegrityError("Payload count mismatch")
    if set(manifest["payload_files"]) != set(entries):
        raise IntegrityError("Files mismatch internal manifest")
    if set(actual) != set(entries) | {"MANIFEST.json", "SHA256SUMS.txt"}:
        raise IntegrityError("Unexpected archive files")
    for rel, data in entries.items():
        record = manifest["payload_files"][rel]
        if record != {"sha256": sha256(data), "size_bytes": len(data)}:
            raise IntegrityError(f"SHA/size mismatch: {rel}")
    lines = actual["SHA256SUMS.txt"].decode("utf-8").splitlines()
    if len(lines) != len(entries):
        raise IntegrityError("SHA256SUMS line count mismatch")
    expected_lines = [f"{sha256(v)}  {k}" for k, v in sorted(entries.items())]
    if lines != expected_lines:
        raise IntegrityError("SHA256SUMS mismatch")
    if manifest["sha256sums_sha256"] != sha256(actual["SHA256SUMS.txt"]):
        raise IntegrityError("SHA256SUMS manifest digest mismatch")
    if manifest["sha256sums_size_bytes"] != len(actual["SHA256SUMS.txt"]):
        raise IntegrityError("SHA256SUMS size mismatch")
    if source is not None:
        with tempfile.TemporaryDirectory() as td:
            reference = Path(td) / "regenerated.zip"
            create_archive(source, reference)
            if reference.read_bytes() != archive.read_bytes():
                raise IntegrityError("Source tree does not regenerate identical archive")
    return {
        "status": "LOCAL_ARCHIVE_INTEGRITY_PASS",
        "zip_sha256": sha256(archive.read_bytes()),
        "payload_files_verified": len(entries),
        "sha256sums_verified": len(lines),
        "archive_entries_verified": len(actual),
        "crc": "PASS",
        "canonical_zip": "PASS",
        "regenerated_source_byte_identical": True if source is not None else "NOT_CHECKED",
        "scientific_validation": "NOT_TESTED",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_archive(args.archive, args.source), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
