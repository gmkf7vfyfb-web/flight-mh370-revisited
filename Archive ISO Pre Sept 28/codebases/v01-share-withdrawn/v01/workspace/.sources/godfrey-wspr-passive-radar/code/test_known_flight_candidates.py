#!/usr/bin/env python3
"""Regression checks for the frozen known-flight PHaRLAP inputs."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path


CODE = Path(__file__).resolve().parent
DATA = CODE.parent / "data" / "known-flight"
sys.path.insert(0, str(CODE))

import materialize_known_flight_candidates as materializer


class KnownFlightCandidateTests(unittest.TestCase):
    def test_frozen_counts_references_and_hashes(self) -> None:
        pairs_path = DATA / "known_flight_pair_locations.csv.gz"
        spots_path = DATA / "known_flight_spot_records.csv.gz"
        audit_path = DATA / "known_flight_arc_truth_audit.csv"
        arcs_path = DATA / "known_flight_arcs.csv"
        truth_path = DATA / "known_flight_truth_references.csv"
        manifest_path = DATA / "known_flight_candidate_manifest.json"
        for path in (
            pairs_path, spots_path, audit_path, arcs_path, truth_path,
            manifest_path,
        ):
            self.assertTrue(path.is_file(), path)

        manifest = json.loads(manifest_path.read_text())
        with gzip.open(pairs_path, "rt", newline="") as handle:
            pairs = list(csv.DictReader(handle))
        with gzip.open(spots_path, "rt", newline="") as handle:
            spots = list(csv.DictReader(handle))
        with audit_path.open(newline="") as handle:
            audit = list(csv.DictReader(handle))
        with arcs_path.open(newline="") as handle:
            arcs = list(csv.DictReader(handle))
        with truth_path.open(newline="") as handle:
            truth = list(csv.DictReader(handle))

        self.assertEqual(len(pairs), 1_723)
        self.assertEqual(
            Counter(row["epoch"] for row in pairs),
            Counter(materializer.EXPECTED_PAIR_COUNTS),
        )
        self.assertEqual(
            {key: value for key, value in Counter(
                row["epoch"] for row in pairs
            ).items()},
            materializer.EXPECTED_PAIR_COUNTS,
        )
        self.assertEqual(len(spots), 1_177)
        self.assertEqual(len(audit), 6)
        self.assertEqual(len(arcs), 84_006)
        self.assertEqual(len(truth), 12)
        used = {row["spot_id_1"] for row in pairs} | {
            row["spot_id_2"] for row in pairs
        }
        self.assertEqual(used, {row["id"] for row in spots})
        self.assertEqual(
            {row["epoch"] for row in audit}, set(materializer.EXPECTED_PAIR_COUNTS)
        )
        self.assertTrue(all(row["physical_wspr_slot_count"] == "10" for row in audit))
        for row in audit:
            for condition in ("minus_60_min", "actual_time", "plus_60_min"):
                self.assertTrue(row[f"{condition}_radio_window_start"])
                self.assertTrue(row[f"{condition}_radio_window_end"])
        self.assertEqual(
            Counter(row["reference_role"] for row in truth),
            Counter({"arc_epoch": 6, "physical_slot": 6}),
        )
        self.assertEqual(
            {row["epoch_id"] for row in truth},
            set(materializer.EXPECTED_PAIR_COUNTS),
        )
        self.assertEqual(
            {
                row["position_source"]
                for row in truth
                if row["epoch_id"].startswith("mh371_")
            },
            {"MH371 retained ACARS workbook"},
        )
        self.assertEqual(
            {
                row["position_source"]
                for row in truth
                if row["epoch_id"].startswith("mh370_")
            },
            {"MH370 retained SITA workbook"},
        )

        for name, path in (
            ("known_flight_pair_locations.csv.gz", pairs_path),
            ("known_flight_spot_records.csv.gz", spots_path),
            ("known_flight_arc_truth_audit.csv", audit_path),
            ("known_flight_arcs.csv", arcs_path),
            ("known_flight_truth_references.csv", truth_path),
        ):
            expected = manifest["outputs"][name]["sha256"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        self.assertEqual(int.from_bytes(pairs_path.read_bytes()[4:8], "little"), 0)
        self.assertEqual(int.from_bytes(spots_path.read_bytes()[4:8], "little"), 0)


if __name__ == "__main__":
    unittest.main()
