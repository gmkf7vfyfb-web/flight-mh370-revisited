#!/usr/bin/env python3
"""Focused tests for the known-flight PHaRLAP publication plotter."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path


CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))

import plot_known_flight_pharlap_residuals as plots


def write_csv(path: Path, fieldnames, rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class PublicationPlotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.clusters = root / "clusters.csv"
        self.raw_clusters = root / "raw_clusters.csv"
        self.arcs = root / "arcs.csv"
        self.truth = root / "truth.csv"
        self.tracks = root / "tracks.csv"
        self.track_metadata = root / "track_metadata.json"
        self.truth_scores = root / "truth_scores.csv"
        self.metadata = root / "metadata.json"
        self.outputs = root / "outputs"
        write_csv(
            self.arcs,
            plots.ARC_COLUMNS,
            [
                {
                    "epoch_id": "mh371_0611",
                    "sequence": 1,
                    "flight": "MH371",
                    "arc_time_utc": "2014-03-07T06:11:01.159Z",
                    "arc_point_index": 0,
                    "latitude_deg": 0.0,
                    "longitude_deg_e": 100.0,
                },
                {
                    "epoch_id": "mh371_0611",
                    "sequence": 1,
                    "flight": "MH371",
                    "arc_time_utc": "2014-03-07T06:11:01.159Z",
                    "arc_point_index": 1,
                    "latitude_deg": 30.0,
                    "longitude_deg_e": 108.0,
                },
            ],
        )
        write_csv(
            self.truth,
            plots.TRUTH_COLUMNS,
            [
                {
                    "epoch_id": "mh371_0611",
                    "truth_id": "acars-arc-epoch",
                    "reference_role": "arc_epoch",
                    "physical_slot": "",
                    "is_nearest_arc_slot": "false",
                    "position_time_utc": "2014-03-07T06:11:01.159Z",
                    "latitude_deg": 9.5,
                    "longitude_deg_e": 107.0,
                    "altitude_km": 12.2,
                    "position_source": "MH371 ACARS workbook",
                    "position_method": "linear interpolation between reports",
                    "time_offset_seconds": 0.0,
                },
                {
                    "epoch_id": "mh371_0611",
                    "truth_id": "acars-slot-midpoint",
                    "reference_role": "physical_slot",
                    "physical_slot": "2014-03-07T06:10:00Z",
                    "is_nearest_arc_slot": "true",
                    "position_time_utc": "2014-03-07T06:10:55.300Z",
                    "latitude_deg": 9.49,
                    "longitude_deg_e": 106.99,
                    "altitude_km": 12.2,
                    "position_source": "MH371 ACARS workbook",
                    "position_method": "linear interpolation to WSPR slot midpoint",
                    "time_offset_seconds": 0.0,
                },
            ],
        )
        track_rows = [
            {
                "flight": "MH371",
                "track_point_index": index,
                "time_utc": f"2014-03-07T06:{minute:02d}:00Z",
                "latitude_deg": latitude,
                "longitude_deg_e": longitude,
                "altitude_ft": 40000,
                "heading_true_deg": 210.0,
                "position_source": "ACARS POSITION AND WIND REPORTS.xlsx",
                "position_method": "reported ACARS position sample",
                "source_sheet": "ACARS",
                "source_excel_row": 20 + index,
            }
            for index, (minute, latitude, longitude) in enumerate(
                ((5, 10.0, 107.3), (15, 9.0, 106.7))
            )
        ]
        write_csv(self.tracks, plots.TRACK_COLUMNS, track_rows)
        track_sha256 = hashlib.sha256(self.tracks.read_bytes()).hexdigest()
        self.track_metadata.write_text(json.dumps({
            "schema": plots.TRACK_PROVENANCE_SCHEMA,
            "track_schema": plots.TRACK_SCHEMA,
            "role": (
                "Post-selection descriptive overlay only; never supplied to WSPR "
                "selection or truth scoring; joined locations are not continuously "
                "observed."
            ),
            "source": {
                "dataset_url": "https://example.test/dataset",
                "file": "ACARS POSITION AND WIND REPORTS.xlsx",
                "license": "CC-BY-4.0",
                "sha256": "0" * 64,
            },
            "output": {
                "file": self.tracks.name,
                "rows": 2,
                "rows_by_flight": {"MH371": 2},
                "sha256": track_sha256,
            },
        }, indent=2) + "\n", encoding="utf-8")
        write_csv(
            self.clusters,
            plots.CLUSTER_COLUMNS,
            [
                self.cluster("minus_60_min", "surface_endpoint", 8.0, 106.0, 3),
                self.cluster("actual_time", "surface_endpoint", 9.6, 107.0, 5),
                self.cluster("actual_time", "surface_endpoint", 20.0, 110.0, 4, residual=False),
                self.cluster("plus_60_min", "surface_endpoint", 12.0, 108.0, 4),
                self.cluster(
                    "actual_time", "common_aircraft_altitude", 9.55, 107.0, 6,
                    altitude=11.5,
                ),
            ],
        )
        with self.clusters.open(newline="", encoding="utf-8") as handle:
            raw_cluster_rows = list(csv.DictReader(handle))
        write_csv(
            self.raw_clusters,
            sorted(plots.RAW_CLUSTER_COLUMNS),
            [
                {key: value for key, value in row.items()
                 if key in plots.RAW_CLUSTER_COLUMNS}
                for row in raw_cluster_rows
            ],
        )
        truth_score_rows = []
        for screen in plots.SCREENS:
            for condition in plots.CONDITIONS:
                recovered = condition == "actual_time"
                altitude = screen == "common_aircraft_altitude"
                truth_score_rows.append({
                    "epoch_id": "mh371_0611",
                    "screen": screen,
                    "condition": condition,
                    "nearest_physical_slot": "2014-03-07T06:10:00Z",
                    "truth_id": "acars-slot-midpoint",
                    "truth_position_time_utc": "2014-03-07T06:10:55.300Z",
                    "truth_latitude_deg": 9.49,
                    "truth_longitude_deg_e": 106.99,
                    "truth_altitude_km": 12.2,
                    "truth_position_source": "MH371 ACARS workbook",
                    "truth_position_method": "linear interpolation to WSPR slot midpoint",
                    "truth_time_offset_seconds": 0.0,
                    "eligible_residual_parent_clusters": 1,
                    "eligible_surviving_source_clusters": 1,
                    "nearest_horizontal_km": 2.0 if recovered else 50.0,
                    "nearest_source_cluster_id": f"source-{screen}-{condition}",
                    "nearest_source_altitude_km": 12.0 if altitude else "",
                    "nearest_horizontal_source_altitude_gap_km": 0.2 if altitude else "",
                    "minimum_altitude_gap_km": 0.2 if altitude else "",
                    "joint_clusters_within_tolerance": 1 if recovered else 0,
                    "horizontal_tolerance_km": 25.0,
                    "altitude_tolerance_km": 0.5 if altitude else "",
                    "recovered": str(recovered).lower(),
                    "parent_collapsed_residual_ids": f"parent-{screen}-{condition}",
                    "altitude_sensitivity_recovered": (
                        '{"0.25": true, "0.5": true, "1": true}'
                        if altitude else "{}"
                    ),
                })
        write_csv(self.truth_scores, plots.TRUTH_SCORE_COLUMNS, truth_score_rows)
        self.metadata.write_text(json.dumps({
            "schema": plots.METADATA_SCHEMA,
            "run_id": "synthetic-test",
            "known_aircraft_truth_used_in_candidate_selection": False,
            "control_offsets_minutes": {
                "minus_60_min": -60,
                "actual_time": 0,
                "plus_60_min": 60,
            },
            "cluster_radius_km": 25.0,
            "residual_tolerance_km": 25.0,
            "minimum_independent_links": 3,
            "surface_endpoint_tolerance_km": 25.0,
            "aircraft_altitude_tolerance_km": 25.0,
            "truth_recovery_tolerance_km": 25.0,
            "truth_recovery_altitude_tolerance_km": 0.5,
            "truth_recovery_altitude_sensitivity_km": [0.25, 0.5, 1.0],
            "route_geometry": "published geodetic-latitude sphere",
            "ionosphere_model": "PHaRLAP 4.7.4 / IRI-2020 historical",
            "map_extent_lon_lat": [64.0, 130.0, 0.0, 30.0],
            "aircraft_altitude_grid_km": [0.5, 1.0, 1.5, 11.0, 11.5, 12.0, 12.5],
            "altitude_collapse_spatial_tolerance_km": 25.0,
            "common_altitude_residual_model": (
                "source_clusters_matched_across_any_altitude_before_survivors_are_"
                "collapsed_for_event_display_and_count;truth_recovery_uses_surviving_"
                "source_centres_and_heights"
            ),
            "epoch_partition_applied_before_clustering": True,
        }, indent=2) + "\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def cluster(
        condition,
        screen,
        latitude,
        longitude,
        independent,
        altitude=None,
        residual=True,
    ):
        collapsed = screen == "common_aircraft_altitude"
        return {
            "epoch_id": "mh371_0611",
            "flight": "MH371",
            "arc_time_utc": "2014-03-07T06:11:01.159Z",
            "condition": condition,
            "screen": screen,
            "physical_slot": "2014-03-07T06:10:00Z",
            "cluster_rank": 1,
            "center_candidate_id": f"{condition}:{screen}:{latitude}",
            "latitude_deg": latitude,
            "longitude_deg_e": longitude,
            "pair_intersections": 3,
            "support_links": independent + 1,
            "independent_links": independent,
            "altitude_km": "",
            "altitude_minimum_km": 11.0 if collapsed else "",
            "altitude_maximum_km": 12.0 if collapsed else "",
            "feasible_altitude_count": 3 if collapsed else 0,
            "feasible_altitudes_km": "11;11.5;12" if collapsed else "",
            "source_altitude_clusters": 3 if collapsed else 0,
            "source_altitude_cluster_ids": (
                "alt-1;alt-2;alt-3" if collapsed else ""
            ),
            "support_spot_ids": ";".join(
                str(value) for value in range(1, independent + 2)
            ),
            "nearest_other_condition_km": 50.0,
            "is_residual": str(residual).lower(),
        }

    def load(self):
        return (
            plots.read_clusters(self.clusters),
            plots.read_arcs(self.arcs),
            plots.read_truth(self.truth),
            plots.read_truth_scores(self.truth_scores),
            plots.read_metadata(self.metadata),
        )

    def test_track_overlay_is_chronological_and_provenance_bound(self):
        tracks = plots.read_tracks(self.tracks)
        self.assertEqual([row.track_point_index for row in tracks["MH371"]], [0, 1])
        provenance = plots.read_track_provenance(
            self.track_metadata, self.tracks, tracks
        )
        self.assertEqual(provenance["output"]["rows_by_flight"], {"MH371": 2})
        value = json.loads(self.track_metadata.read_text(encoding="utf-8"))
        value["output"]["sha256"] = "f" * 64
        self.track_metadata.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "does not match table"):
            plots.read_track_provenance(self.track_metadata, self.tracks, tracks)

    def test_summary_is_paired_and_truth_is_only_a_proximity_overlay(self):
        clusters, arcs, truths, scores, _ = self.load()
        summary = plots.build_summary(
            arcs,
            clusters,
            truths,
            scores,
            ("surface_endpoint",),
        )
        self.assertEqual([row["condition"] for row in summary], list(plots.CONDITIONS))
        self.assertEqual([row["residual_cluster_count"] for row in summary], [1, 1, 1])
        actual = summary[1]
        self.assertLess(actual["nearest_arc_epoch_reference_horizontal_km"], 12.0)
        self.assertLess(actual["nearest_time_aligned_truth_horizontal_km"], 14.0)
        self.assertEqual(actual["nearest_cluster_independent_links"], 5)
        # The non-residual cluster is geographically different but never enters
        # the count or truth proximity calculation.
        self.assertEqual(actual["nearest_cluster_latitude_deg"], 9.6)

    def test_altitude_screen_reports_vertical_difference_without_filtering(self):
        clusters, arcs, truths, scores, _ = self.load()
        summary = plots.build_summary(
            arcs,
            clusters,
            truths,
            scores,
            ("common_aircraft_altitude",),
        )
        actual = summary[1]
        self.assertEqual(actual["residual_cluster_count"], 1)
        self.assertAlmostEqual(
            actual["nearest_arc_epoch_reference_altitude_difference_km"], 0.2
        )
        self.assertTrue(actual["recovered_within_tolerance"])
        self.assertEqual(
            actual["recovery_altitude_sensitivity_results"],
            "0.25:true;0.5:true;1:true",
        )

    def test_noncontiguous_feasible_altitudes_use_exact_set_not_range(self):
        clusters, arcs, truths, _, _ = self.load()
        cluster = next(
            row for row in clusters
            if row.screen == "common_aircraft_altitude"
            and row.condition == "actual_time"
        )
        cluster = replace(
            cluster,
            latitude_deg=9.5,
            longitude_deg_e=107.0,
            altitude_minimum_km=1.0,
            altitude_maximum_km=10.0,
            feasible_altitude_count=2,
            feasible_altitudes_km=(1.0, 10.0),
            source_altitude_clusters=2,
            source_altitude_cluster_ids=("low", "high"),
        )
        reference = replace(
            truths.arc_epoch["mh371_0611"], altitude_km=5.0
        )
        summary = plots.summarize_panel(
            arcs[0],
            "common_aircraft_altitude",
            "actual_time",
            (cluster,),
            reference,
            None,
            "fixture",
        )
        self.assertEqual(
            summary["nearest_arc_epoch_reference_altitude_difference_km"], 4.0
        )

    def test_raw_actual_summary_includes_clusters_removed_by_residualization(self):
        raw_clusters = plots.read_clusters(self.raw_clusters, raw_input=True)
        _, arcs, truths, _, _ = self.load()
        summary = plots.build_raw_actual_summary(
            arcs, raw_clusters, truths, ("surface_endpoint",)
        )
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["raw_cluster_count"], 2)
        self.assertLess(
            summary[0]["nearest_arc_epoch_reference_horizontal_km"], 12.0
        )

    def test_truth_centered_latitude_limits_retain_complete_search_domain(self):
        raw_clusters = plots.read_clusters(self.raw_clusters, raw_input=True)
        _, arcs, truths, _, metadata = self.load()
        limits = plots._truth_centered_latitude_limits(
            arcs,
            raw_clusters,
            truths.arc_epoch["mh371_0611"],
            metadata["map_extent_lon_lat"],
        )
        self.assertAlmostEqual(sum(limits) / 2.0, 9.5)
        self.assertLess(limits[0], 0.0)
        self.assertGreater(limits[1], 30.0)

    def test_empty_authoritative_truth_score_is_valid_and_not_recovered(self):
        with self.truth_scores.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        target = next(
            row for row in rows
            if row["screen"] == "surface_endpoint"
            and row["condition"] == "plus_60_min"
        )
        target.update({
            "eligible_residual_parent_clusters": "0",
            "eligible_surviving_source_clusters": "0",
            "nearest_horizontal_km": "",
            "nearest_source_cluster_id": "",
            "nearest_source_altitude_km": "",
            "nearest_horizontal_source_altitude_gap_km": "",
            "minimum_altitude_gap_km": "",
            "joint_clusters_within_tolerance": "0",
            "recovered": "false",
            "parent_collapsed_residual_ids": "",
        })
        write_csv(self.truth_scores, plots.TRUTH_SCORE_COLUMNS, rows)
        scores = plots.read_truth_scores(self.truth_scores)
        score = scores[("mh371_0611", "surface_endpoint", "plus_60_min")]
        self.assertIsNone(score.nearest_horizontal_km)
        self.assertFalse(score.recovered)

    def test_truth_blindness_flag_is_mandatory(self):
        value = json.loads(self.metadata.read_text(encoding="utf-8"))
        value["known_aircraft_truth_used_in_candidate_selection"] = True
        self.metadata.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "blind candidate selection"):
            plots.read_metadata(self.metadata)

    def test_overlapping_physical_slots_remain_partitioned_by_epoch(self):
        clusters, arcs, _, _, _ = self.load()
        first_cluster = next(
            row for row in clusters
            if row.screen == "surface_endpoint" and row.condition == "actual_time"
            and row.is_residual
        )
        second_cluster = replace(
            first_cluster,
            input_row_number=999,
            epoch_id="mh371_second_epoch",
            arc_time_utc="2014-03-07T06:13:01.159Z",
        )
        second_arc = tuple(
            replace(
                point,
                epoch_id="mh371_second_epoch",
                sequence=2,
                arc_time_utc="2014-03-07T06:13:01.159Z",
            )
            for point in arcs
        )
        summary = plots.build_summary(
            arcs + second_arc,
            (first_cluster, second_cluster),
            plots.TruthReferences({}, {}, {}),
            {},
            ("surface_endpoint",),
        )
        actual = [row for row in summary if row["condition"] == "actual_time"]
        self.assertEqual([row["residual_cluster_count"] for row in actual], [1, 1])

    def test_three_epochs_share_one_three_row_flight_figure(self):
        _, arcs, _, _, _ = self.load()
        combined = tuple(arcs)
        for sequence in (2, 3):
            combined += tuple(
                replace(
                    point,
                    epoch_id=f"mh371_epoch_{sequence}",
                    sequence=sequence,
                    arc_time_utc=f"2014-03-07T06:{9 + sequence:02d}:01.159Z",
                )
                for point in arcs
            )
        pages = plots.epoch_pages(combined)
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0][0], "MH371")
        self.assertEqual(len(pages[0][3]), 3)

    def test_recovery_uses_only_time_aligned_nearest_physical_slot(self):
        clusters, arcs, truths, scores, _ = self.load()
        aligned = next(
            row for row in clusters
            if row.screen == "surface_endpoint" and row.condition == "actual_time"
            and row.is_residual
        )
        closer_but_wrong_slot = replace(
            aligned,
            input_row_number=998,
            physical_slot="2014-03-07T06:04:00Z",
            latitude_deg=9.5,
            longitude_deg_e=107.0,
            center_candidate_id="wrong-slot-near-arc-truth",
        )
        summary = plots.build_summary(
            arcs,
            (aligned, closer_but_wrong_slot),
            truths,
            scores,
            ("surface_endpoint",),
        )[1]
        self.assertLess(summary["nearest_arc_epoch_reference_horizontal_km"], 0.1)
        self.assertGreater(summary["nearest_time_aligned_truth_horizontal_km"], 1.0)
        self.assertEqual(summary["recovery_slot_residual_cluster_count"], 1)

    def test_surface_and_altitude_rows_cannot_be_conflated(self):
        with self.clusters.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["altitude_km"] = "10"
        write_csv(self.clusters, plots.CLUSTER_COLUMNS, rows)
        with self.assertRaisesRegex(ValueError, "surface cluster has altitude metadata"):
            plots.read_clusters(self.clusters)

    def test_three_format_render_and_manifest_when_matplotlib_is_available(self):
        try:
            import matplotlib  # noqa: F401
        except ImportError:
            self.skipTest("matplotlib not installed in this interpreter")
        summary, manifest = plots.generate(
            self.clusters,
            self.raw_clusters,
            self.arcs,
            self.truth,
            self.tracks,
            self.track_metadata,
            self.truth_scores,
            self.metadata,
            self.outputs,
            ("surface_endpoint",),
        )
        self.assertTrue(summary.exists())
        self.assertTrue(manifest.exists())
        for suffix in (".png", ".pdf", ".svg"):
            values = list(self.outputs.glob(f"*{suffix}"))
            self.assertEqual(len(values), 2)
            self.assertGreater(values[0].stat().st_size, 1000)
        document = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(
            document["plotter_source_sha256"],
            hashlib.sha256(Path(plots.__file__).read_bytes()).hexdigest(),
        )
        self.assertEqual(document["figures"]["png_dpi"], 300)
        self.assertEqual(document["figures"]["support_scale"], [3, 5])
        self.assertEqual(document["figures"]["raw_support_scale"], [3, 5])
        self.assertEqual(document["figures"]["scale_bar"]["distance_km"], 500.0)
        self.assertTrue(
            document["figures"]["latitude_axis"]["no_frozen_domain_clipping"]
        )
        self.assertEqual(
            document["figures"]["track_overlay"]["label"],
            "ACARS report positions joined in time order (post-selection context)",
        )


if __name__ == "__main__":
    unittest.main()
