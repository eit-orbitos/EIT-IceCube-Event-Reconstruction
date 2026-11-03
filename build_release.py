#!/usr/bin/env python3
"""Byte-reproducible source ZIP with two non-circular internal hash layers.

No timestamps, environment paths, random salt or host-dependent compression.
The outer ZIP SHA-256 must be anchored out-of-band, NEVER inside this ZIP.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_STORED

PROJECT = "EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2"
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "dist", "build"}
EXCLUDED_NAMES = {"MANIFEST.json", "SHA256SUMS.txt", ".DS_Store"}
ALLOWED_EXTENSIONS = {".md", ".json", ".yml", ".yaml", ".py", ".cff", ".txt"}
ALLOWED_BASENAMES = {"LICENSE", ".gitignore", ".zenodo.json", "CITATION.cff"}


def sha256(buf):
    return hashlib.sha256(buf).hexdigest()


def _canonical_json(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def iter_source_files(root):
    """Small audited project file set, no external ZIP/data or local cache files."""
    root = Path(root).resolve()
    files = []
    whitelist_root = {
        ".gitignore", ".zenodo.json", "LICENSE", "CITATION.cff",
        "README.md", "CHANGELOG.md", "CONTRIBUTING.md",
    }
    def allowed(rel):
        name = rel.name
        if len(rel.parts) == 1:
            return name in whitelist_root
        if len(rel.parts) == 2:
            parent = rel.parts[0]
            return (
                (parent == "eit_icecube" and rel.suffix == ".py") or
                (parent == "configs" and name == "benchmark_v0.1.json") or
                (parent == "docs" and rel.suffix == ".md") or
                (parent == "examples" and name in ("reference_results.json", "adversarial_reference_v0.1.2.json")) or
                (parent == "tests" and name.startswith("test_") and rel.suffix == ".py") or
                (parent == "tools" and name in ("build_release.py", "verify_release.py", "reproduce.py", "adversarial_regression.py"))
            )
        return rel.as_posix() == ".github/workflows/ci.yml"

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f"Symlink forbidden: {rel}")
        if any(part in EXCLUDED_PARTS for part in rel.parts) or path.name in EXCLUDED_NAMES:
            continue
        if not allowed(rel):
            continue
        if path.stat().st_size > 5_000_000:
            raise ValueError(f"Unexpected large payload: {rel}")
        files.append(rel.as_posix())
    if "README.md" not in files or "LICENSE" not in files or "examples/reference_results.json" not in files:
        raise ValueError("Required source payload missing")
    return sorted(files)


def create_archive(root, out):
    root = Path(root).resolve()
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    source = {}
    for rel in iter_source_files(root):
        source[rel] = (root / rel).read_bytes()
    sha_lines = [f"{sha256(data)}  {rel}" for rel, data in source.items()]
    checks = ("\n".join(sha_lines) + "\n").encode("utf-8")
    manifest = {
        "project": PROJECT,
        "version": "0.1.2",
        "manifest_format": "EIT_SIMPLE_HASHES_V1",
        "archive_profile": "ZIP_STORED_sorted_fixed_1980-01-01_0644",
        "scientific_status": "UNVALIDATED_SYNTHETIC_CANDIDATE",
        "payload_file_count": len(source),
        "payload_files": {rel: {"sha256": sha256(data), "size_bytes": len(data)}
                          for rel, data in source.items()},
        "sha256sums_sha256": sha256(checks),
        "sha256sums_size_bytes": len(checks),
        "self_hash": "OMITTED_BY_DESIGN_AVOIDS_CIRCULARITY",
        "outer_zip_hash": "STORED_OUTSIDE_ARCHIVE",
    }
    entries = {**source, "SHA256SUMS.txt": checks, "MANIFEST.json": _canonical_json(manifest)}
    with ZipFile(out, "w", compression=ZIP_STORED, allowZip64=True) as zf:
        zf.comment = b""
        for rel in sorted(entries):
            name = PROJECT + "/" + rel
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_STORED
            info.create_system = 3
            info.external_attr = (0o100644 << 16)
            info.extra = b""
            info.comment = b""
            zf.writestr(info, entries[rel])
    return {"zip_path": str(out), "sha256": sha256(out.read_bytes()),
            "zip_size_bytes": out.stat().st_size, "payload_file_count": len(source),
            "archive_file_count": len(entries)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(create_archive(args.source, args.out), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
