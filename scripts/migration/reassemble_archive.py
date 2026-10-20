#!/usr/bin/env python3
"""Reassemble ordered migration transport parts and verify SHA-256."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parts", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args()

    ordered = sorted(args.parts, key=lambda path: path.name)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    with temporary.open("wb") as output:
        for part in ordered:
            with part.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    output.write(block)

    observed = sha256(temporary)
    expected = args.expected_sha256.lower()
    if observed != expected:
        temporary.unlink(missing_ok=True)
        raise SystemExit(
            f"SHA-256 mismatch: expected {expected}, observed {observed}"
        )
    temporary.replace(args.output)
    print(f"Reassembled {len(ordered)} parts: {args.output}")
    print(f"SHA-256 verified: {observed}")


if __name__ == "__main__":
    main()
