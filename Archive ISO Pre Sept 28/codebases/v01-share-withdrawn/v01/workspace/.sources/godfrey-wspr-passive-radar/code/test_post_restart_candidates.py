#!/usr/bin/env python3
"""Regression checks for the frozen post-restart PHaRLAP inputs."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


CODE = Path(__file__).resolve().parent
REPOSITORY = CODE.parents[2]
DATA = CODE.parent / "data" / "post-restart"
sys.path.insert(0, str(CODE))

import materialize_post_restart_candidates as materializer


class PostRestartCandidateTests(unittest.TestCase):
    def test_configured_epochs_match_canonical_product_inputs(self) -> None:
        observations = REPOSITORY / "inputs" / "accident" / "satcom-observations.csv"
        satellite = REPOSITORY / "inputs" / "accident" / "satellite-ephemeris.csv"
        materializer.validate_canonical_observations(observations)
        frame = pd.read_csv(satellite).set_index("epoch_id")
        states = {
            int(case["ephemeris_second"]): frame.loc[
                epoch, ["x_km", "y_km", "z_km"]
            ].to_numpy(dtype=float)
            for epoch, case in materializer.EPOCHS.items()
        }
        materializer.validate_canonical_satellite(satellite, states)

        # The canonical first arc at radar latitude is near the radar position;
        # this catches the superseded exploratory 17,120-us first curve.
        arc = materializer.construct_arc("m1825", states[66_334])
        nearest = int(np.argmin(np.abs(arc.latitude_deg - 6.75)))
        self.assertAlmostEqual(arc.longitude_deg_e[nearest], 96.105, places=3)
        self.assertEqual(len(materializer.physical_slots(arc.handshake)), 10)

    def test_frozen_counts_identity_and_no_truth_fields(self) -> None:
        pairs_path = DATA / "post_restart_pair_locations.csv.gz"
        spots_path = DATA / "post_restart_spot_records.csv.gz"
        audit_path = DATA / "post_restart_arc_audit.csv"
        arcs_path = DATA / "post_restart_arcs.csv"
        manifest_path = DATA / "post_restart_candidate_manifest.json"
        for path in (pairs_path, spots_path, audit_path, arcs_path, manifest_path):
            self.assertTrue(path.is_file(), path)

        manifest = json.loads(manifest_path.read_text())
        with gzip.open(pairs_path, "rt", newline="") as handle:
            pairs = list(csv.DictReader(handle))
        with gzip.open(spots_path, "rt", newline="") as handle:
            spots = list(csv.DictReader(handle))
        with audit_path.open(newline="") as handle:
            audit = list(csv.DictReader(handle))

        self.assertEqual(manifest["schema"], materializer.SCHEMA)
        self.assertEqual(len(pairs), 38_581)
        self.assertEqual(len(spots), 9_828)
        self.assertEqual(len(audit), 7)
        self.assertEqual(
            manifest["anomaly_audit"]["input_rows_in_included_bands"], 179_023
        )
        coverage = manifest["baseline_coverage_audit"]
        self.assertTrue(coverage["full_baseline_coverage"])
        self.assertEqual(coverage["leading_margin_minutes"], 46.0)
        self.assertEqual(coverage["trailing_margin_minutes"], 30.0)
        self.assertEqual(set(row["epoch"] for row in pairs), set(materializer.EPOCHS))
        self.assertEqual(
            Counter(row["condition"] for row in pairs),
            Counter({"minus_60_min": 14_136, "actual_time": 12_525,
                     "plus_60_min": 11_920}),
        )
        used = {row["spot_id_1"] for row in pairs} | {
            row["spot_id_2"] for row in pairs
        }
        self.assertEqual(used, {row["id"] for row in spots})
        self.assertTrue(all(row["physical_wspr_slot_count"] == "10" for row in audit))
        self.assertTrue(all(row["truth_used_in_candidate_selection"] == "False" for row in audit))
        forbidden = {"truth_lat", "truth_lon", "reference_lat", "reference_lon"}
        self.assertFalse(forbidden.intersection(pairs[0]))

        for name, path in (
            ("post_restart_pair_locations.csv.gz", pairs_path),
            ("post_restart_spot_records.csv.gz", spots_path),
            ("post_restart_arc_audit.csv", audit_path),
            ("post_restart_arcs.csv", arcs_path),
        ):
            expected = manifest["outputs"][name]["sha256"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        self.assertEqual(int.from_bytes(pairs_path.read_bytes()[4:8], "little"), 0)
        self.assertEqual(int.from_bytes(spots_path.read_bytes()[4:8], "little"), 0)

    def test_truncated_wspr_baseline_is_rejected(self) -> None:
        truncated = pd.DataFrame({
            "time": [
                pd.Timestamp("2014-03-07 14:17:00"),
                pd.Timestamp("2014-03-08 04:28:00"),
            ]
        })
        with self.assertRaisesRegex(materializer.MaterializationError, "full plus/minus"):
            materializer.baseline_coverage_audit(truncated)

    def test_constant_local_window_has_no_manufactured_z_score(self) -> None:
        times = list(pd.date_range("2014-03-07 00:00:00", periods=12, freq="1min"))
        times.append(pd.Timestamp("2014-03-07 04:00:00"))
        frame = pd.DataFrame({
            "id": range(1, 14),
            "time": times,
            "tx_sign": ["TX"] * 13,
            "rx_sign": ["RX"] * 13,
            "band": [10] * 13,
            "frequency": [10_140_270.0] * 12 + [10_141_270.0],
        })
        scores = materializer._window_z_scores(frame, "frequency")
        self.assertTrue(np.isnan(scores[0]))


if __name__ == "__main__":
    unittest.main()
