#!/usr/bin/env python3
"""Focused regressions for known-flight PHaRLAP result assembly."""

from __future__ import annotations

import csv
import math
import sys
import unittest
from pathlib import Path


CODE = Path(__file__).resolve().parent
DATA = CODE.parent / "data" / "known-flight"
sys.path.insert(0, str(CODE))

import assemble_known_flight_pharlap as assembler
import wspr_pharlap_control as control


def altitude_cluster(
    *,
    latitude: float,
    altitude: float | None,
    source_ids: tuple[str, ...],
    rank: int,
) -> control.SpatialCluster:
    return control.SpatialCluster(
        screen=control.ALTITUDE_SCREEN,
        epoch_id="epoch-a",
        condition="actual_time",
        physical_slot="2014-03-07 04:04:00",
        altitude_km=altitude,
        feasible_altitudes_km=(
            (9.0, 10.0) if altitude is None else (altitude,)
        ),
        cluster_rank=rank,
        latitude_deg=latitude,
        longitude_deg_e=0.0,
        pair_intersections=3,
        support_links=3,
        independent_links=3,
        support_spot_ids=(1, 2, 3),
        center_candidate_id=f"candidate-{rank}",
        source_altitude_clusters=len(source_ids),
        source_altitude_cluster_ids=source_ids,
    )


class KnownFlightAssemblyTests(unittest.TestCase):
    def test_publication_results_are_a_pivot_not_a_recalculation(self) -> None:
        comparisons = []
        truth_scores = []
        counts = {
            control.SURFACE_SCREEN: {
                "raw_clusters": (3, 1, 5),
                "residual_clusters": (2, 1, 4),
            },
            control.ALTITUDE_SCREEN: {
                "raw_clusters": (7, 2, 9),
                "residual_clusters": (5, 2, 8),
            },
        }
        for screen, measures in counts.items():
            for measure, values in measures.items():
                minus, actual, plus = values
                control_mean = (minus + plus) / 2.0
                comparisons.append({
                    "epoch_id": "epoch-a",
                    "sequence": "1",
                    "flight": "MH371",
                    "arc_time_utc": "2014-03-07 04:04:09.457000",
                    "screen": screen,
                    "measure": measure,
                    "minus_60_min": minus,
                    "actual_time": actual,
                    "plus_60_min": plus,
                    "control_mean": control_mean,
                    "actual_minus_control_mean": actual - control_mean,
                })
            truth_scores.append({
                "epoch_id": "epoch-a",
                "screen": screen,
                "condition": "actual_time",
                "recovered": False,
            })
        diagnostic = {
            "screens": {
                screen: {
                    "residual": {
                        "epoch_effects": {
                            "one_sided_actual_excess_p": 1.0,
                            "two_sided_p": 0.5,
                        },
                        "connected_window_sensitivity": {
                            "one_sided_actual_excess_p": 1.0,
                            "two_sided_p": 1.0,
                        },
                    }
                }
                for screen in counts
            }
        }
        rows = assembler.publication_result_rows(
            comparisons, truth_scores, diagnostic
        )
        self.assertEqual(len(rows), 4)
        surface_pooled = rows[0]
        self.assertEqual(surface_pooled["scope"], "pooled")
        self.assertEqual(surface_pooled["raw_minus_60_min"], 3)
        self.assertEqual(surface_pooled["residual_actual_time"], 1)
        self.assertEqual(
            surface_pooled["residual_actual_minus_control_mean"], -2.0
        )
        self.assertEqual(surface_pooled["actual_time_references_recovered"], 0)
        self.assertEqual(surface_pooled["actual_time_references_scored"], 1)
        document = assembler.publication_markdown(rows).decode("utf-8")
        self.assertIn("3 / 1 / 5", document)
        self.assertIn("one-sided actual-excess p = 1.000", document)

    def test_batch_scientific_identity_excludes_runtime_and_paths(self) -> None:
        manifest = {
            "schema": "batch-v1",
            "scope": {
                "dataset_name": "fixture",
                "candidate_pairs": 1,
                "route_jobs_total": 1,
                "route_jobs_selected": 1,
                "partial_job_limit": None,
                "truth_used_in_candidate_or_propagation_selection": False,
            },
            "inputs": {
                "candidate_pairs": {"path": "/first/pairs", "sha256": "a" * 64},
                "spot_records": {"path": "/first/spots", "sha256": "b" * 64},
            },
            "scientific_settings": {"rays": 295},
            "scientific_dependencies": {"library": "c" * 64},
            "worker_reported_external_identity": {"release": "4.7.4"},
            "runner_source_sha256": "d" * 64,
            "execution": {"elapsed_seconds": 10.0},
            "jobs": [{
                "sequence": 1,
                "job_id": "job-a",
                "job_hash": "e" * 64,
                "result_path": "/first/result",
                "process_wall_seconds": 9.0,
            }],
        }
        first = assembler.batch_scientific_identity(manifest)
        manifest["inputs"]["candidate_pairs"]["path"] = "/second/pairs"
        manifest["execution"]["elapsed_seconds"] = 99.0
        manifest["jobs"][0]["result_path"] = "/second/result"
        manifest["jobs"][0]["process_wall_seconds"] = 98.0
        self.assertEqual(first, assembler.batch_scientific_identity(manifest))

    def test_declared_radio_windows_have_three_connected_components(self) -> None:
        with (DATA / "known_flight_arc_truth_audit.csv").open(newline="") as handle:
            epochs = {row["epoch"]: row for row in csv.DictReader(handle)}
        intervals = assembler.declared_radio_intervals(epochs)
        self.assertTrue(all(len(value) == 3 for value in intervals.values()))
        self.assertEqual(
            assembler.connected_window_components(intervals),
            (
                ("mh370_1642", "mh370_1656", "mh370_1707"),
                ("mh371_0404", "mh371_0611"),
                ("mh371_0648",),
            ),
        )

    def test_truth_recovery_uses_surviving_source_centres_not_parent_union(self) -> None:
        # A collapsed parent at the near source has a union containing 10 km.
        # Neither source slice itself jointly satisfies the horizontal and
        # altitude tolerances: near/wrong-height and far/right-height.
        near_wrong_height = altitude_cluster(
            latitude=0.10, altitude=9.0, source_ids=("near-9",), rank=1
        )
        far_right_height = altitude_cluster(
            latitude=0.30, altitude=10.0, source_ids=("far-10",), rank=2
        )
        parent = altitude_cluster(
            latitude=0.10,
            altitude=None,
            source_ids=("near-9", "far-10"),
            rank=1,
        )
        sources = tuple(
            control.ResidualCluster(cluster, math.inf, True)
            for cluster in (near_wrong_height, far_right_height)
        )
        parents = (control.ResidualCluster(parent, math.inf, True),)
        truth = [{
            "epoch_id": "epoch-a",
            "truth_id": "truth-a",
            "reference_role": "physical_slot",
            "physical_slot": "2014-03-07 04:04:00",
            "is_nearest_arc_slot": "true",
            "position_time_utc": "2014-03-07 04:04:56.242000",
            "latitude_deg": "0",
            "longitude_deg_e": "0",
            "altitude_km": "10",
            "position_source": "synthetic withheld truth",
            "position_method": "fixture",
            "time_offset_seconds": "0",
        }]
        rows = assembler.truth_score_rows((), sources, parents, truth)
        actual = next(
            row for row in rows
            if row["screen"] == control.ALTITUDE_SCREEN
            and row["condition"] == "actual_time"
        )
        self.assertFalse(actual["recovered"])
        self.assertEqual(actual["eligible_residual_parent_clusters"], 1)
        self.assertEqual(actual["eligible_surviving_source_clusters"], 2)
        self.assertAlmostEqual(actual["minimum_altitude_gap_km"], 0.0)
        self.assertGreater(actual["nearest_horizontal_source_altitude_gap_km"], 0.5)

        # Empty control panels must serialize missing distances as null/blank,
        # never JSON-invalid infinities.
        minus = next(
            row for row in rows
            if row["screen"] == control.ALTITUDE_SCREEN
            and row["condition"] == "minus_60_min"
        )
        self.assertIsNone(minus["nearest_horizontal_km"])
        self.assertIsNone(minus["minimum_altitude_gap_km"])
        assembler.canonical_json(rows)

    def test_nearest_slot_truth_must_be_unique_and_complete(self) -> None:
        truth = {
            "epoch_id": "epoch-a",
            "truth_id": "truth-a",
            "reference_role": "physical_slot",
            "physical_slot": "2014-03-07 04:04:00",
            "is_nearest_arc_slot": "true",
            "position_time_utc": "2014-03-07 04:04:56.242000",
            "latitude_deg": "0",
            "longitude_deg_e": "0",
            "altitude_km": "10",
            "position_source": "synthetic withheld truth",
            "position_method": "fixture",
            "time_offset_seconds": "0",
        }
        with self.assertRaisesRegex(
            assembler.AssemblyError, "duplicate nearest-slot truth"
        ):
            assembler.truth_score_rows(
                (), (), (), (truth, dict(truth)),
                expected_epoch_ids=("epoch-a",),
            )
        with self.assertRaisesRegex(
            assembler.AssemblyError, r"missing=\['epoch-b'\]"
        ):
            assembler.truth_score_rows(
                (), (), (), (truth,),
                expected_epoch_ids=("epoch-a", "epoch-b"),
            )


if __name__ == "__main__":
    unittest.main()
