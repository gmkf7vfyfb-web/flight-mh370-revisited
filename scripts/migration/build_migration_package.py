#!/usr/bin/env python3
"""Create the immutable MH370 migration snapshot and integrity manifests."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tarfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "migration" / "package"
DATE = "2026-08-14"
PREFIX = "flight-mh370-revisited"

EXCLUDED_TOP_LEVEL = {".git", ".agents", ".codex", "pids"}
EXCLUDED_PARTS = {"__pycache__"}

LFS_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".xlsm", ".xls", ".png", ".jpg",
    ".jpeg", ".zip", ".bin",
}

TEXT_EXTENSIONS = {
    ".py", ".mjs", ".js", ".md", ".txt", ".csv", ".json",
    ".geojson", ".html", ".yml", ".yaml", ".toml",
}

SECRET_PATTERNS = {
    "GitHub token prefix": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    "GitHub fine-grained token prefix": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "AWS access key prefix": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "OpenAI-style key prefix": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Private key header": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def include_file(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.parts[0] in EXCLUDED_TOP_LEVEL:
        return False
    if rel.parts[:2] == ("migration", "package"):
        return False
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    # The Library materialization helper can leave partial, uniquely named
    # transfer files if an atomic publish falls back between transfer modes.
    # They are staging residue, not additional Library versions.
    if ".openai-download-" in path.name:
        return False
    if path.suffix.lower() in {".pyc", ".pyo"}:
        return False
    return path.is_file()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_tar_gz(output: Path, files: list[Path]) -> None:
    """Create an archive atomically using repository-relative member names."""
    temporary = output.with_suffix(output.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz", compresslevel=6) as archive:
        for path in files:
            rel = path.relative_to(ROOT)
            archive.add(path, arcname=(Path(PREFIX) / rel).as_posix(), recursive=False)
    os.replace(temporary, output)


def split_binary(source: Path, chunk_bytes: int) -> list[Path]:
    """Create ordered transport parts without changing the canonical archive."""
    parts: list[Path] = []
    with source.open("rb") as handle:
        index = 1
        while block := handle.read(chunk_bytes):
            part = PACKAGE / f"{source.name}.part-{index:03d}.bin"
            temporary = part.with_suffix(part.suffix + ".tmp")
            with temporary.open("wb") as output:
                output.write(block)
            os.replace(temporary, part)
            parts.append(part)
            index += 1
    return parts


def category(rel: Path) -> str:
    first = rel.parts[0]
    if first == "library_full_audit":
        return "library_master_archive"
    if first in {"downloads", "downloads_refined_bfo", "upload"}:
        return "source_data"
    if first in {"library_materialized", "library_no_precomp"}:
        return "materialized_artifact"
    if first in {"outputs", "output", "generated_images"}:
        return "research_output"
    if first == "tmp":
        return "intermediate"
    if first in {"handoff", "history", "environment", "scripts"}:
        return "handoff_or_tooling"
    if rel.suffix.lower() in {".py", ".mjs", ".js"}:
        return "source_code"
    return "project_root"


def is_lfs_candidate(rel: Path, size: int) -> bool:
    name = rel.name
    return (
        rel.suffix.lower() in LFS_EXTENSIONS
        or ".openai-download-" in name
        or "posterior_sample" in name
        or size >= 10 * 1024 * 1024
    )


def scan_credentials(files: list[Path]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in files:
        if path.suffix.lower() not in TEXT_EXTENSIONS or path.stat().st_size > 10 * 1024 * 1024:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        {
                            "path": path.relative_to(ROOT).as_posix(),
                            "line": line_no,
                            "pattern": label,
                            "value": "REDACTED",
                        }
                    )
    return findings


def main() -> None:
    PACKAGE.mkdir(parents=True, exist_ok=True)

    files = sorted(
        (path for path in ROOT.rglob("*") if include_file(path)),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )

    rows: list[dict[str, object]] = []
    manifest_lines: list[str] = []
    category_counts: Counter[str] = Counter()
    extension_counts: Counter[str] = Counter()
    total_bytes = 0

    print(f"Hashing {len(files)} files...")
    for path in files:
        rel = path.relative_to(ROOT)
        stat = path.stat()
        digest = sha256(path)
        size = stat.st_size
        cat = category(rel)
        extension = rel.suffix.lower() or "[none]"
        row = {
            "relative_path": rel.as_posix(),
            "size_bytes": size,
            "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "sha256": digest,
            "category": cat,
            "git_lfs_candidate": "yes" if is_lfs_candidate(rel, size) else "no",
        }
        rows.append(row)
        manifest_lines.append(f"{digest}  {rel.as_posix()}")
        category_counts[cat] += 1
        extension_counts[extension] += 1
        total_bytes += size

    inventory_path = PACKAGE / f"MH370_file_inventory_{DATE}.csv"
    with inventory_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = PACKAGE / f"MH370_file_manifest_{DATE}.sha256"
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    findings = scan_credentials(files)
    security_path = PACKAGE / f"MH370_credential_scan_{DATE}.json"
    security_path.write_text(
        json.dumps(
            {
                "scope": "text-pattern scan only; not a substitute for manual review",
                "finding_count": len(findings),
                "findings": findings,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    stats = {
        "snapshot_date_utc": DATE,
        "file_count": len(files),
        "total_uncompressed_bytes": total_bytes,
        "categories": dict(sorted(category_counts.items())),
        "extensions": dict(sorted(extension_counts.items())),
        "excluded": {
            "top_level": sorted(EXCLUDED_TOP_LEVEL),
            "path_parts": sorted(EXCLUDED_PARTS),
            "generated_package_directory": "migration/package",
            "compiled_python": ["*.pyc", "*.pyo"],
            "library_transfer_staging": "*.openai-download-*",
        },
        "credential_pattern_findings": len(findings),
    }
    stats_path = PACKAGE / f"MH370_snapshot_statistics_{DATE}.json"
    stats_path.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    archive_path = PACKAGE / f"MH370_complete_workspace_expanded_{DATE}.tar.gz"
    print(f"Creating {archive_path.name}...")
    create_tar_gz(archive_path, files)

    archive_digest = sha256(archive_path)
    archive_sha_path = PACKAGE / f"MH370_complete_workspace_expanded_{DATE}.sha256"
    archive_sha_path.write_text(
        f"{archive_digest}  {archive_path.name}\n", encoding="utf-8"
    )

    # ChatGPT Library has a lower per-file ingestion ceiling than GitHub
    # Releases. These two semantic component archives reconstruct the same
    # snapshot while keeping each transfer independently useful and verifiable.
    working_archive_path = PACKAGE / f"MH370_working_workspace_{DATE}.tar.gz"
    working_files = [
        path for path in files
        if path.relative_to(ROOT).parts[0] != "library_full_audit"
    ]
    print(f"Creating {working_archive_path.name}...")
    create_tar_gz(working_archive_path, working_files)
    working_archive_sha_path = PACKAGE / f"MH370_working_workspace_{DATE}.sha256"
    working_archive_sha_path.write_text(
        f"{sha256(working_archive_path)}  {working_archive_path.name}\n",
        encoding="utf-8",
    )

    library_archive_path = PACKAGE / f"MH370_library_master_archive_{DATE}.tar.gz"
    library_files = [
        path for path in files
        if path.relative_to(ROOT).parts[0] == "library_full_audit"
    ]
    print(f"Creating {library_archive_path.name}...")
    create_tar_gz(library_archive_path, library_files)
    library_archive_sha_path = PACKAGE / f"MH370_library_master_archive_{DATE}.sha256"
    library_archive_sha_path.write_text(
        f"{sha256(library_archive_path)}  {library_archive_path.name}\n",
        encoding="utf-8",
    )
    library_transport_parts = split_binary(
        library_archive_path,
        chunk_bytes=200 * 1024 * 1024,
    )

    dossier_path = PACKAGE / f"MH370_handoff_dossier_{DATE}.zip"
    dossier_roots = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / ".gitattributes",
        ROOT / ".gitignore",
        ROOT / "handoff",
        ROOT / "history",
        ROOT / "environment",
        ROOT / "scripts" / "migration",
    ]
    with zipfile.ZipFile(dossier_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in dossier_roots:
            if item.is_file():
                archive.write(item, item.relative_to(ROOT).as_posix())
            elif item.is_dir():
                for path in sorted(item.rglob("*")):
                    if path.is_file() and include_file(path):
                        archive.write(path, path.relative_to(ROOT).as_posix())
        for item in [
            inventory_path,
            manifest_path,
            stats_path,
            security_path,
            archive_sha_path,
            working_archive_sha_path,
            library_archive_sha_path,
        ]:
            archive.write(item, f"migration/package/{item.name}")

    readme_path = PACKAGE / "MIGRATION_PACKAGE_README.md"
    transport_part_lines = "\n".join(
        f"- `{part.name}` — ordered Library transport part."
        for part in library_transport_parts
    )
    readme_path.write_text(
        f"""# MH370 migration package ({DATE})

Files:

- `{archive_path.name}` — immutable scientific workspace snapshot.
- `{archive_sha_path.name}` — archive-level SHA-256 checksum.
- `{working_archive_path.name}` — working workspace component for Library transfer.
- `{working_archive_sha_path.name}` — working-component checksum.
- `{library_archive_path.name}` — immutable 148-file Library-source component.
- `{library_archive_sha_path.name}` — Library-component checksum.
{transport_part_lines}
- `{inventory_path.name}` — file inventory, sizes, categories and hashes.
- `{manifest_path.name}` — file-level SHA-256 manifest.
- `{dossier_path.name}` — compact handoff documents and migration tooling.
- `{stats_path.name}` — snapshot statistics and explicit exclusions.
- `{security_path.name}` — redacted pattern scan requiring manual review.

The full archive includes scientific source data, code, outputs and temporary
reconstruction material, plus the 148-file ChatGPT Library master archive under
`library_full_audit/MH370/`. Runtime metadata (`.git`, `.agents`, `.codex`,
`pids`), compiled Python caches, partial Library-transfer staging files and the
package directory itself are excluded.

The two component archives together contain the same project files as the
single archive and are provided for services with lower per-file upload limits.
If the Library-source archive itself exceeds a service limit, reconstruct it
from the ordered `.bin` parts with `scripts/migration/reassemble_archive.py` and
verify it against `{library_archive_sha_path.name}`.

Keep the archive private until the provenance and redistribution review in
`handoff/DATA_AND_PROVENANCE.md` is complete.
""",
        encoding="utf-8",
    )

    package_manifest = PACKAGE / "PACKAGE_SHA256SUMS.txt"
    # Use an explicit allow-list so filesystem-level atomic-write residue can
    # never become part of the published package checksum set.
    package_files = sorted([
        archive_path,
        archive_sha_path,
        working_archive_path,
        working_archive_sha_path,
        library_archive_path,
        library_archive_sha_path,
        dossier_path,
        inventory_path,
        manifest_path,
        stats_path,
        security_path,
        readme_path,
        *library_transport_parts,
    ])
    package_manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in package_files) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "file_count": len(files),
        "uncompressed_bytes": total_bytes,
        "archive": str(archive_path),
        "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": archive_digest,
        "dossier": str(dossier_path),
        "credential_pattern_findings": len(findings),
    }, indent=2))


if __name__ == "__main__":
    main()
