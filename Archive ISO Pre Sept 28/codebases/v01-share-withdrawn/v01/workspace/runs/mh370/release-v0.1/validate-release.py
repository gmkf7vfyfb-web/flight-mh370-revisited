#!/usr/bin/env python3
"""Validate the portable MH370 v0.1 release documentation bundle.

The release manifest is the canonical documentation data source. The HTML
contains a byte-for-byte JSON copy in a non-executing script element so it can
render when opened directly; this validator proves that the copy agrees with
the manifest and that every linked primary artifact still has the recorded
identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


MANIFEST_SCHEMA = "mh370-release-manifest/1.0.0"
EMBEDDED_MANIFEST_RE = re.compile(
    r'<script\s+id="release-manifest"\s+type="application/json">\s*'
    r"(?P<manifest>.*?)\s*</script>",
    re.DOTALL,
)
HREF_RE = re.compile(r'href="(?P<href>[^"]+)"')
SHA256_RE = re.compile(r"[0-9a-f]{64}")
ALLOWED_CLASSIFICATIONS = {
    "central",
    "conditional",
    "diagnostic_zero_weight",
    "provisional",
}


class ValidationError(RuntimeError):
    """Raised for a release-contract violation."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def safe_repo_path(repo_root: Path, raw_path: str) -> Path:
    require(raw_path != "", "empty repository path")
    require("\\" not in raw_path, f"non-portable path separator: {raw_path}")
    pure = PurePosixPath(raw_path)
    require(not pure.is_absolute(), f"absolute path is forbidden: {raw_path}")
    require(".." not in pure.parts, f"parent traversal is forbidden: {raw_path}")
    require(not raw_path.startswith("file:"), f"file URI is forbidden: {raw_path}")
    candidate = (repo_root / pure).resolve(strict=False)
    root = repo_root.resolve(strict=True)
    require(candidate == root or root in candidate.parents, f"path escapes repository: {raw_path}")
    return candidate


def validate_manifest(manifest: dict[str, object], repo_root: Path) -> set[str]:
    require(manifest.get("schema_version") == MANIFEST_SCHEMA, "unexpected manifest schema")
    require(manifest.get("release_id") == "v0.1", "unexpected release id")
    require("DRAFT" not in str(manifest.get("release_status", "")),
            "release status is still draft")
    serialized_manifest = json.dumps(manifest, sort_keys=True)
    require("/jackbox/" not in serialized_manifest, "manifest contains a host-specific path")
    require("file://" not in serialized_manifest, "manifest contains a file URI")

    contract = manifest.get("scientific_contract")
    require(isinstance(contract, dict), "scientific_contract must be an object")
    require(contract.get("structural_family_pooling_prohibited") is True,
            "structural-family pooling must be prohibited")
    require(contract.get("central_posterior_updated_by_conditional_branches") is False,
            "conditional branches must not update the central posterior")

    items = manifest.get("items")
    require(isinstance(items, list), "items must be an array")
    require([item.get("number") for item in items] == list(range(1, 8)),
            "items must cover exactly 1 through 7 in order")
    for item in items:
        classification = item.get("classification")
        require(classification in ALLOWED_CLASSIFICATIONS,
                f"item {item.get('number')} has invalid classification {classification!r}")

    evidence = manifest.get("evidence_consumption")
    require(isinstance(evidence, list), "evidence_consumption must be an array")
    evidence_ids = [entry.get("evidence_id") for entry in evidence]
    require(len(evidence_ids) == len(set(evidence_ids)), "duplicate evidence_id in release ledger")
    for entry in evidence:
        consumers = entry.get("consumed_by")
        require(isinstance(consumers, list), f"consumed_by must be an array: {entry}")
        require(len(consumers) == len(set(consumers)),
                f"evidence consumed twice by the same branch: {entry.get('evidence_id')}")
        if entry.get("mode") == "diagnostic_only":
            require(not consumers, f"diagnostic evidence has a likelihood consumer: {entry.get('evidence_id')}")

    families = manifest.get("model_families")
    require(isinstance(families, list), "model_families must be an array")
    family_ids = [family.get("family_id") for family in families]
    require(len(family_ids) == len(set(family_ids)), "duplicate model family id")
    for family in families:
        classification = family.get("classification")
        require(classification in ALLOWED_CLASSIFICATIONS,
                f"family {family.get('family_id')} has invalid classification")
        require(family.get("pooled_with") == [],
                f"structural family is pooled: {family.get('family_id')}")
    family_id_set = set(family_ids)
    for entry in evidence:
        unknown_consumers = set(entry.get("consumed_by", [])) - family_id_set
        require(not unknown_consumers,
                f"evidence has unknown likelihood consumer(s): {sorted(unknown_consumers)}")

    artifacts = manifest.get("artifacts")
    require(isinstance(artifacts, list), "artifacts must be an array")
    artifact_ids = [artifact.get("artifact_id") for artifact in artifacts]
    require(len(artifact_ids) == len(set(artifact_ids)), "duplicate artifact id")
    linked_paths: set[str] = set()
    for artifact in artifacts:
        path = artifact.get("path")
        expected_hash = artifact.get("sha256")
        expected_bytes = artifact.get("bytes")
        require(artifact.get("classification") in ALLOWED_CLASSIFICATIONS,
                f"artifact {artifact.get('artifact_id')} has invalid classification")
        require(isinstance(artifact.get("label"), str) and artifact.get("label") != "",
                f"artifact {artifact.get('artifact_id')} has no label")
        require(isinstance(artifact.get("role"), str) and artifact.get("role") != "",
                f"artifact {artifact.get('artifact_id')} has no role")
        require(isinstance(path, str), f"artifact path is not a string: {artifact}")
        require(isinstance(expected_hash, str) and SHA256_RE.fullmatch(expected_hash) is not None,
                f"invalid SHA-256 for {path}")
        require(isinstance(expected_bytes, int) and expected_bytes >= 0,
                f"invalid byte count for {path}")
        target = safe_repo_path(repo_root, path)
        require(target.is_file(), f"missing artifact: {path}")
        require(target.stat().st_size == expected_bytes,
                f"byte count mismatch for {path}")
        require(sha256(target) == expected_hash, f"SHA-256 mismatch for {path}")
        linked_paths.add(path)
    artifact_id_set = set(artifact_ids)
    for item in items:
        references = item.get("artifact_ids")
        require(isinstance(references, list),
                f"item {item.get('number')} artifact_ids must be an array")
        require(len(references) == len(set(references)),
                f"item {item.get('number')} repeats an artifact")
        unknown = set(references) - artifact_id_set
        require(not unknown,
                f"item {item.get('number')} references unknown artifact(s): {sorted(unknown)}")
    return linked_paths


def validate_html(
    html_path: Path,
    manifest: dict[str, object],
    repo_root: Path,
    artifact_paths: set[str],
) -> None:
    html = html_path.read_text(encoding="utf-8")
    match = EMBEDDED_MANIFEST_RE.search(html)
    require(match is not None, "index.html lacks embedded release manifest")
    embedded = json.loads(match.group("manifest"))
    require(canonical_json(embedded) == canonical_json(manifest),
            "index.html embedded manifest disagrees with release-manifest.json")

    release_dir = html_path.parent
    for match in HREF_RE.finditer(html):
        href = match.group("href")
        if "${" in href:
            continue
        split = urlsplit(href)
        if split.scheme in {"http", "https", "mailto"} or href.startswith("#"):
            continue
        require(split.scheme == "", f"non-portable local URI in HTML: {href}")
        href_path = unquote(split.path)
        target = (release_dir / href_path).resolve(strict=False)
        require(target.is_file(), f"broken HTML link: {href}")
        require(repo_root.resolve(strict=True) in target.parents or target == repo_root.resolve(strict=True),
                f"HTML link escapes repository: {href}")
    require('id="artifact-rows"' in html, "index.html lacks the artifact renderer target")
    require('artifact.path' in html and 'repoHref(artifact.path)' in html,
            "index.html does not render manifest artifact links")


def sync_embedded_manifest(html_path: Path, manifest: dict[str, object]) -> None:
    html = html_path.read_text(encoding="utf-8")
    match = EMBEDDED_MANIFEST_RE.search(html)
    require(match is not None, "index.html lacks embedded release manifest")
    rendered = json.dumps(manifest, indent=2, sort_keys=True).replace("</", "<\\/")
    updated = html[: match.start("manifest")] + rendered + html[match.end("manifest") :]
    temporary = html_path.with_suffix(".html.tmp")
    temporary.write_text(updated, encoding="utf-8")
    temporary.replace(html_path)


def refresh_artifact_identities(manifest_path: Path, manifest: dict[str, object], repo_root: Path) -> None:
    artifacts = manifest.get("artifacts")
    require(isinstance(artifacts, list), "artifacts must be an array")
    for artifact in artifacts:
        path = artifact.get("path")
        require(isinstance(path, str), f"artifact path is not a string: {artifact}")
        target = safe_repo_path(repo_root, path)
        require(target.is_file(), f"missing artifact: {path}")
        artifact["bytes"] = target.stat().st_size
        artifact["sha256"] = sha256(target)
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_bytes(canonical_json(manifest))
    temporary.replace(manifest_path)


def default_repo_root() -> Path:
    for candidate in (Path(__file__).resolve().parent, *Path(__file__).resolve().parents):
        if (candidate / "Cargo.toml").is_file() and (candidate / "AGENTS.md").is_file():
            return candidate
    return Path.cwd()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="release directory (defaults to this script's directory)",
    )
    parser.add_argument(
        "--refresh-artifacts",
        action="store_true",
        help="recompute artifact byte counts and SHA-256 identities before validating",
    )
    parser.add_argument(
        "--sync-html",
        action="store_true",
        help="replace the embedded HTML manifest copy before validating",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_repo_root(),
        help="repository root (auto-detected, then defaults to current directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_dir = args.release_dir.resolve(strict=True)
    repo_root = args.repo_root.resolve(strict=True)
    manifest_path = release_dir / "release-manifest.json"
    html_path = release_dir / "index.html"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if args.refresh_artifacts:
            refresh_artifact_identities(manifest_path, manifest, repo_root)
        if args.sync_html:
            sync_embedded_manifest(html_path, manifest)
        artifact_paths = validate_manifest(manifest, repo_root)
        validate_html(html_path, manifest, repo_root, artifact_paths)
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(f"release validation failed: {error}", file=sys.stderr)
        return 1
    print(
        f"release validation passed: {len(artifact_paths)} artifacts; "
        f"manifest_sha256={sha256(manifest_path)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
