#!/usr/bin/env python3
"""One-command local reproduction and out-of-band evidence generation.

No author freeze decision and NO independent verification implied.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
if __package__ in (None, ""):
    # Direct execution: python tools/<script>.py
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build_release import create_archive
from tools.verify_release import verify_archive

ROOT = Path(__file__).resolve().parents[1]


def sha256(buf):
    return hashlib.sha256(buf).hexdigest()


def reproduce(out, evidence):
    out, evidence = Path(out).resolve(), Path(evidence).resolve()
    if out == evidence or ROOT in out.parents or ROOT in evidence.parents:
        raise ValueError("Release ZIP/evidence must be stored OUTSIDE the source project directory")
    test = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                          cwd=ROOT, capture_output=True, text=True)
    if test.returncode:
        raise RuntimeError("Tests failed:\n" + test.stdout + "\n" + test.stderr)
    match = re.search(r"Ran (\d+) tests", test.stdout + test.stderr)
    if not match:
        raise RuntimeError("Test count not found")
    run = subprocess.run([sys.executable, "-m", "eit_icecube", "benchmark"],
                         cwd=ROOT, capture_output=True, text=True)
    if run.returncode:
        raise RuntimeError("Benchmark failed:\n" + run.stderr)
    reference = (ROOT / "examples" / "reference_results.json").read_bytes()
    if run.stdout.encode("utf-8") != reference:
        raise RuntimeError("Benchmark reference is NOT BYTE_IDENTICAL")
    adversarial = subprocess.run([sys.executable, "tools/adversarial_regression.py"],
                                 cwd=ROOT, capture_output=True, text=True)
    if adversarial.returncode:
        raise RuntimeError("Adversarial regression failed:\n" + adversarial.stderr)
    adversarial_ref = (ROOT / "examples" / "adversarial_reference_v0.1.2.json").read_bytes()
    if adversarial.stdout.encode("utf-8") != adversarial_ref:
        raise RuntimeError("Adversarial reference is NOT BYTE_IDENTICAL")
    with tempfile.TemporaryDirectory() as td:
        replica = Path(td) / "second.zip"
        first = create_archive(ROOT, out)
        second = create_archive(ROOT, replica)
        if out.read_bytes() != replica.read_bytes():
            raise RuntimeError("Two local builds differ")
    verification = verify_archive(out, ROOT)
    report = {
        "project": "EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2",
        "version": "0.1.2",
        "status": "LOCAL_CANDIDATE_VERIFIED_NOT_FROZEN",
        "test_count_passed": int(match.group(1)),
        "test_suite_status": "PASS",
        "benchmark_reference_bytes": len(reference),
        "benchmark_reference_sha256": sha256(reference),
        "benchmark_reexecution_byte_identical": True,
        "adversarial_reference_sha256": sha256(adversarial_ref),
        "adversarial_reexecution_byte_identical": True,
        "geometry_near_coplanar_rejection": "120/120 per estimator (post-hoc toy test)",
        "input_bool_strict_rejection": "PASS",
        "predecessor_archive_sha256": "8dc859001db30a6298090c6d3f8f6a5233061babfda1808eed4b01e65d7f977f",
        "original_v0_1_archive_sha256": "e89c2b211044392457edb50682e8b65391b3c3dbdc9692d91b6785abac93c935",
        "author_license_choice": "PolyForm-Noncommercial-1.0.0 (author-selected 2026-11-03)",
        "license_notice_url": "https://polyformproject.org/licenses/noncommercial/1.0.0",
        "license_repack_scope": "METADATA_AND_IDENTITY_ONLY_NO_ALGORITHM_CHANGE",
        "zenodo_affiliation": "OMITTED_PENDING_VERIFICATION",
        "two_zip_builds_byte_identical_in_one_environment": True,
        "zip_sha256": first["sha256"],
        "zip_size_bytes": first["zip_size_bytes"],
        "archive_file_count": first["archive_file_count"],
        "payload_file_count": first["payload_file_count"],
        "verification": verification,
        "python_interpreter": sys.version.split()[0],
        "scientific_status": "UNVALIDATED_TOY_ONLY",
        "independent_review": "PENDING",
        "author_freeze": "NO",
        "github_push": "NO",
        "zenodo_doi": "NOT_ISSUED",
        "evidence_is_external_to_zip": True,
    }
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(reproduce(args.out, args.evidence), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
