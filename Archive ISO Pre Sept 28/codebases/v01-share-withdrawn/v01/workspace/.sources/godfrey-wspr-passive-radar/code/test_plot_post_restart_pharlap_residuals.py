#!/usr/bin/env python3
"""Focused contract tests for post-restart WSPR publication figures."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import plot_post_restart_pharlap_residuals as plotter


TIMES = {
    "m1825": "2014-03-07 18:25:34",
    "m1941": "2014-03-07 19:41:02",
    "m2041": "2014-03-07 20:41:04",
    "m2141": "2014-03-07 21:41:26",
    "m2241": "2014-03-07 22:41:21",
    "m0011": "2014-03-08 00:10:59",
    "m0019a": "2014-03-08 00:19:29",
}
FLIGHT = "MH370 post-radar"
CLUSTER_FIELDS = (
    "epoch_id", "flight", "arc_time_utc", "condition", "screen",
    "physical_slot", "cluster_rank", "center_candidate_id", "latitude_deg",
    "longitude_deg_e", "pair_intersections", "support_links",
    "independent_links", "altitude_km", "altitude_minimum_km",
    "altitude_maximum_km", "feasible_altitude_count",
    "feasible_altitudes_km", "source_altitude_clusters",
    "source_altitude_cluster_ids", "support_spot_ids",
    "nearest_other_condition_km", "is_residual",
)
ARC_FIELDS = (
    "epoch_id", "sequence", "flight", "arc_time_utc", "arc_point_index",
    "latitude_deg", "longitude_deg_e",
)
COMPARISON_FIELDS = (
    "epoch_id", "sequence", "flight", "arc_time_utc", "screen", "measure",
    "minus_60_min", "actual_time", "plus_60_min", "control_mean",
    "actual_minus_control_mean", "actual_to_control_mean_ratio",
)


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fixture(root: Path) -> tuple[Path, Path, Path, Path]:
    arcs: list[dict[str, object]] = []
    clusters: list[dict[str, object]] = []
    comparisons: list[dict[str, object]] = []
    for sequence, epoch in enumerate(plotter.EXPECTED_EPOCHS, 1):
        for index, latitude in enumerate((-45.0, 10.0)):
            arcs.append({
                "epoch_id": epoch, "sequence": sequence, "flight": FLIGHT,
                "arc_time_utc": TIMES[epoch], "arc_point_index": index,
                "latitude_deg": latitude, "longitude_deg_e": 80.0 + sequence,
            })
        for screen in plotter.SCREENS:
            for condition in plotter.CONDITIONS:
                altitude = screen == "common_aircraft_altitude"
                clusters.append({
                    "epoch_id": epoch, "flight": FLIGHT,
                    "arc_time_utc": TIMES[epoch], "condition": condition,
                    "screen": screen, "physical_slot": "2014-03-07 18:24:00",
                    "cluster_rank": 1, "center_candidate_id": f"{epoch}-{screen}-{condition}",
                    "latitude_deg": -20.0 + sequence, "longitude_deg_e": 82.0 + sequence,
                    "pair_intersections": 3, "support_links": 3,
                    "independent_links": 3, "altitude_km": "",
                    "altitude_minimum_km": 1.0 if altitude else "",
                    "altitude_maximum_km": 3.0 if altitude else "",
                    "feasible_altitude_count": 3 if altitude else 0,
                    "feasible_altitudes_km": "1;2;3" if altitude else "",
                    "source_altitude_clusters": 1 if altitude else 0,
                    "source_altitude_cluster_ids": "source-1" if altitude else "",
                    "support_spot_ids": "1;2;3", "nearest_other_condition_km": 30,
                    "is_residual": "true",
                })
                if screen == "surface_endpoint" and condition == "actual_time":
                    extra = dict(clusters[-1])
                    extra.update({
                        "cluster_rank": 2,
                        "center_candidate_id": f"{epoch}-surface-subtracted",
                        "latitude_deg": -10.0,
                        "nearest_other_condition_km": 5,
                        "is_residual": "false",
                    })
                    clusters.append(extra)
            if screen == "surface_endpoint":
                raw_counts = {"minus_60_min": 1, "actual_time": 2, "plus_60_min": 1}
            else:
                raw_counts = {condition: 2 for condition in plotter.CONDITIONS}
            residual_counts = {condition: 1 for condition in plotter.CONDITIONS}
            for measure, counts in (
                ("raw_clusters", raw_counts), ("residual_clusters", residual_counts),
            ):
                control_mean = (counts["minus_60_min"] + counts["plus_60_min"]) / 2
                comparisons.append({
                    "epoch_id": epoch, "sequence": sequence, "flight": FLIGHT,
                    "arc_time_utc": TIMES[epoch], "screen": screen, "measure": measure,
                    **counts, "control_mean": control_mean,
                    "actual_minus_control_mean": counts["actual_time"] - control_mean,
                    "actual_to_control_mean_ratio": counts["actual_time"] / control_mean,
                })

    metadata = {
        "schema": plotter.METADATA_SCHEMA,
        "run_id": "fixture-run",
        "known_aircraft_truth_available": False,
        "known_aircraft_truth_used_in_candidate_selection": False,
        "control_offsets_minutes": {
            "minus_60_min": -60, "actual_time": 0, "plus_60_min": 60,
        },
        "map_extent_lon_lat": [64.0, 110.0, -45.0, 10.0],
        "route_geometry": "PublishedSphericalRouteResolver",
        "ionosphere_model": "PHaRLAP 4.7.4 IRI-2020 spherical 2-D",
        "assembly_scientific_settings": {
            "surface_endpoint_tolerance_km": 25.0,
            "aircraft_path_horizontal_tolerance_km": 25.0,
            "cluster_radius_km": 25.0,
            "source_residual_tolerance_km": 25.0,
            "altitude_survivor_collapse_radius_km": 25.0,
            "minimum_independent_links": 3,
            "source_residual_altitude_matching": "ignore_modeled_altitude",
        },
        "pharlap_batch_scientific_settings": {
            "aircraft_altitudes_km": [0.5, 1.0, 2.0, 3.0, 13.0],
        },
    }
    arc_path, cluster_path = root / "arcs.csv", root / "clusters.csv"
    comparison_path, metadata_path = root / "comparison.csv", root / "metadata.json"
    write_csv(arc_path, ARC_FIELDS, arcs)
    write_csv(cluster_path, CLUSTER_FIELDS, clusters)
    write_csv(comparison_path, COMPARISON_FIELDS, comparisons)
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    return cluster_path, arc_path, comparison_path, metadata_path


class PostRestartPlotTests(unittest.TestCase):
    def test_contract_covers_exact_seven_epochs_and_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = fixture(Path(directory))
            clusters = plotter.shared.read_clusters(paths[0])
            arcs = plotter.shared.read_arcs(paths[1])
            comparisons = plotter._read_comparisons(paths[2])
            epochs = plotter._validate_contract(arcs, clusters, comparisons)
            self.assertEqual(tuple(row.epoch_id for row in epochs), plotter.EXPECTED_EPOCHS)
            self.assertEqual(len(plotter._table_rows(comparisons)), 14)

    def test_generate_writes_audited_suite_without_truth(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = fixture(root)
            output = root / "output"

            def fake_draw(screen, page_index, pages, *args, **kwargs):
                stem = plotter._figure_stem(screen, page_index, len(pages))
                result = tuple(output / f"{stem}.{suffix}" for suffix in ("png", "pdf", "svg"))
                for path in result:
                    path.write_bytes(f"{screen}-{page_index}-{path.suffix}".encode())
                return result

            with patch.object(plotter, "_draw_page", side_effect=fake_draw):
                table, manifest_path = plotter.generate(*paths, output, rows_per_page=3)
            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(manifest["schema"], plotter.PLOT_SCHEMA)
            self.assertEqual(manifest["figure_contract"]["truth_or_trajectory_overlay"],
                             "none; unavailable post-18:22")
            self.assertEqual(len(manifest["outputs"]), 21)
            with table.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 14)
            self.assertEqual(rows[0]["actual_time_raw"], "2")
            self.assertEqual(rows[0]["actual_time_residual"], "1")

    def test_truth_available_metadata_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = fixture(Path(directory))
            metadata = json.loads(paths[3].read_text())
            metadata["known_aircraft_truth_available"] = True
            paths[3].write_text(json.dumps(metadata), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "truth_available=false"):
                plotter._read_metadata(paths[3])

    def test_inconsistent_comparison_count_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = fixture(Path(directory))
            with paths[2].open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            rows[0]["control_mean"] = "99"
            write_csv(paths[2], COMPARISON_FIELDS, rows)
            with self.assertRaisesRegex(ValueError, "control mean"):
                plotter._read_comparisons(paths[2])


if __name__ == "__main__":
    unittest.main()
