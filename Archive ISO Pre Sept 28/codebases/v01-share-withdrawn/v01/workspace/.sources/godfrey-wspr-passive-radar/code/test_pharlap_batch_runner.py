#!/usr/bin/env python3
"""Focused tests for immutable PHaRLAP batch planning and caching."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


CODE = Path(__file__).resolve().parent
SOURCE_ROOT = CODE.parent
sys.path.insert(0, str(CODE))

import pharlap_batch_runner as batch


class BatchRunnerTests(unittest.TestCase):
    def test_immutable_hash_covers_job_and_dependencies(self) -> None:
        job = {"schema": "fixture", "value": 1}
        dependencies = {"library_sha256": "a" * 64}
        identity = batch.job_hash(job, dependencies)
        self.assertEqual(identity, batch.job_hash(dict(job), dict(dependencies)))
        self.assertNotEqual(
            identity, batch.job_hash({**job, "value": 2}, dependencies)
        )
        self.assertNotEqual(
            identity,
            batch.job_hash(job, {"library_sha256": "b" * 64}),
        )

    def test_cache_is_atomic_and_validates_immutable_identity(self) -> None:
        job = {"schema": "fixture", "value": 1}
        dependencies = {"library_sha256": "a" * 64}
        identity = batch.job_hash(job, dependencies)
        envelope = {
            "schema": batch.CACHE_SCHEMA,
            "job_hash": identity,
            "immutable_identity": batch.immutable_job_identity(job, dependencies),
            "worker_result": {"schema": batch.control.WORKER_RESULT_SCHEMA},
            "route_result": {"schema": batch.control.ROUTE_RESULT_SCHEMA},
            "execution": {
                "process_wall_seconds": 1.25,
                "worker_peak_rss_kb": 123_456,
                "native_timing": {"wall_seconds": 1.0},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            batch.atomic_write(path, batch.canonical_json(envelope, pretty=True))
            cached = batch.read_cached_result(path, identity)
            self.assertEqual(cached["job_hash"], identity)
            self.assertEqual(cached["execution"], envelope["execution"])
            document = json.loads(path.read_text())
            document["immutable_identity"]["job"]["value"] = 2
            batch.atomic_write(path, batch.canonical_json(document, pretty=True))
            with self.assertRaises(batch.BatchError):
                batch.read_cached_result(path, identity)

    def test_assembler_rejects_partial_batch_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {
                "schema": batch.MANIFEST_SCHEMA,
                "status": "partial_complete",
            }
            batch.atomic_write(
                root / "manifest.json", batch.canonical_json(manifest, pretty=True)
            )
            with self.assertRaisesRegex(batch.BatchError, "not production-complete"):
                batch.load_complete_route_documents(root)

    def test_canonical_known_flight_plan_uses_frozen_primary_settings(self) -> None:
        data = SOURCE_ROOT / "data" / "known-flight"
        candidates = data / "known_flight_pair_locations.csv.gz"
        spots = data / "known_flight_spot_records.csv.gz"
        if not candidates.exists() or not spots.exists():
            self.skipTest("canonical known-flight fixture is not present")
        plan, jobs, elevations = batch.primary_jobs(
            candidates, spots, "known-flight-test"
        )
        self.assertEqual(len(plan.pairs), 1_723)
        self.assertEqual(len(plan.jobs), 2_406)
        self.assertEqual(len(plan.leg_jobs), 6_892)
        self.assertEqual(len(elevations), 295)
        self.assertEqual(jobs[0]["elevation_fan"]["elevations_deg"], elevations)
        self.assertEqual(
            jobs[0]["reference"]["wspr_slot_midpoint_offset_seconds"], 56.242
        )
        self.assertIn(
            "published geodetic-latitude great-circle sphere",
            jobs[0]["reference"]["geometry_provenance"]["primary"],
        )


if __name__ == "__main__":
    unittest.main()
