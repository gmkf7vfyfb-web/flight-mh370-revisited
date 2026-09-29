#!/usr/bin/env python3
"""Verify the MH370 v0.1 capsule without third-party dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


CAPSULE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = CAPSULE_ROOT / "workspace"
LEDGER = CAPSULE_ROOT / "SHA256SUMS"
PRODUCER = CAPSULE_ROOT / "bin/linux-x86_64/mh370-v0.1"
PRODUCER_SHA256 = "de28b0adc6de796026e6075da614b5e11c78459d4beafbca42f6e30b10758b4b"
SOURCE_LOCK = WORKSPACE / "runs/mh370/release-v0.1/impact/source-tree.lock.json"
RELEASE_VALIDATOR = WORKSPACE / "runs/mh370/release-v0.1/validate-release.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_ledger() -> dict[str, str]:
    entries: dict[str, str] = {}
    for number, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"invalid SHA256SUMS line {number}: {line!r}") from error
        entries[relative] = expected
    return entries


def verify_capsule_files() -> None:
    entries = read_ledger()
    actual = {
        path.relative_to(CAPSULE_ROOT).as_posix()
        for path in CAPSULE_ROOT.rglob("*")
        if path.is_file() and path != LEDGER
    }
    recorded = set(entries)
    missing = sorted(recorded - actual)
    unexpected = sorted(actual - recorded)
    mismatches: list[str] = []
    for relative, expected in sorted(entries.items()):
        path = CAPSULE_ROOT / relative
        if path.is_file():
            observed = sha256(path)
            if observed != expected:
                mismatches.append(f"{relative}: expected {expected}, observed {observed}")
    if missing or unexpected or mismatches:
        for path in missing:
            print(f"MISSING: {path}", file=sys.stderr)
        for path in unexpected:
            print(f"UNRECORDED: {path}", file=sys.stderr)
        for message in mismatches:
            print(f"MISMATCH: {message}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS capsule file ledger: {len(entries)} files")


def verify_producer() -> None:
    observed = sha256(PRODUCER)
    if observed != PRODUCER_SHA256:
        raise SystemExit(
            f"producer binary mismatch: expected {PRODUCER_SHA256}, observed {observed}"
        )
    version = subprocess.run(
        [str(PRODUCER), "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    print(f"PASS producer binary: {observed} ({version})")


def report_source_lock() -> None:
    record = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    matches: list[str] = []
    differences: list[str] = []
    missing: list[str] = []
    for relative, expected in record["files"].items():
        path = WORKSPACE / relative
        if not path.is_file():
            missing.append(relative)
        elif sha256(path) == expected:
            matches.append(relative)
        else:
            differences.append(relative)
    print(
        "INFO historical producer source lock: "
        f"{len(matches)} match, {len(differences)} differ, {len(missing)} missing"
    )
    if differences:
        print("INFO changed-after-release paths:")
        for relative in differences:
            print(f"  {relative}")
    if missing:
        raise SystemExit("locked producer source files are missing from the capsule")


def verify_release() -> None:
    completed = subprocess.run(
        [sys.executable, "-B", str(RELEASE_VALIDATOR.relative_to(WORKSPACE))],
        cwd=WORKSPACE,
        check=False,
        text=True,
    )
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-file-hashes", action="store_true")
    parser.add_argument("--skip-release-validator", action="store_true")
    args = parser.parse_args()

    if not args.skip_file_hashes:
        verify_capsule_files()
    verify_producer()
    report_source_lock()
    if not args.skip_release_validator:
        verify_release()
    print("PASS MH370 v0.1 capsule verification")


if __name__ == "__main__":
    main()
