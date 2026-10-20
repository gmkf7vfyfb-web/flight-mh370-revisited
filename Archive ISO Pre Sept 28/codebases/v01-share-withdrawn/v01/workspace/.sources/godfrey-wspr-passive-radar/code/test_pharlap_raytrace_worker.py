#!/usr/bin/env python3
"""Focused PHaRLAP-independent checks for the spherical route worker."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import unittest

import numpy as np


MODULE_PATH = Path(__file__).with_name("pharlap_raytrace_worker.py")
SPEC = importlib.util.spec_from_file_location("pharlap_raytrace_worker", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CoordinateConventionTest(unittest.TestCase):
    def test_range_zero_returns_geodetic_origin(self) -> None:
        for latitude in (-70.0, -30.0, 0.0, 50.9375, 80.0):
            output_latitude, output_longitude = MODULE.pharlap_slice_coordinate(
                latitude, 94.25, 123.0, 0.0
            )
            self.assertAlmostEqual(output_latitude, latitude, places=8)
            self.assertAlmostEqual(output_longitude, 94.25, places=10)

    def test_auxiliary_sphere_inverse_and_direct_are_consistent(self) -> None:
        origin = (50.9375, -1.2916666666666667)
        target = (-21.502, 94.972)
        route_range, bearing = MODULE.pharlap_spherical_inverse(*origin, *target)
        recovered = MODULE.pharlap_slice_coordinate(
            *origin, bearing, route_range, MODULE.EARTH_EQUATORIAL_RADIUS_KM
        )
        self.assertAlmostEqual(recovered[0], target[0], places=8)
        self.assertAlmostEqual(recovered[1], target[1], places=8)
        self.assertLess(route_range, math.pi * MODULE.EARTH_EQUATORIAL_RADIUS_KM)

    def test_published_simple_sphere_bearing_is_distinct(self) -> None:
        origin = (50.9375, -1.2916666666666667)
        target = (-21.502, 94.972)
        simple_range, simple_bearing = MODULE.geodetic_sphere_inverse(*origin, *target)
        auxiliary_range, auxiliary_bearing = MODULE.pharlap_spherical_inverse(
            *origin, *target
        )
        self.assertAlmostEqual(simple_bearing, 99.34274724706256, places=11)
        self.assertAlmostEqual(simple_range, 12289.639300868475, places=8)
        self.assertNotAlmostEqual(simple_bearing, auxiliary_bearing, places=3)
        self.assertNotAlmostEqual(simple_range, auxiliary_range, places=0)

    def test_published_locator_center(self) -> None:
        latitude, longitude = MODULE.maidenhead_six_character_center("IO90iw")
        self.assertAlmostEqual(latitude, 50.9375)
        self.assertAlmostEqual(longitude, -1.2916666666666667)


class CrossingTopologyTest(unittest.TestCase):
    def test_all_crossings_across_two_hops_are_retained(self) -> None:
        ranges = [0.0, 100.0, 200.0, 300.0, 400.0]
        heights = [0.0, 20.0, 0.0, 20.0, 0.0]
        crossings = MODULE.altitude_crossing_segments(ranges, heights, 10.0)
        self.assertEqual([item[2] for item in crossings], [50.0, 150.0, 250.0, 350.0])
        self.assertEqual(
            [item[3] for item in crossings],
            ["ascending", "descending", "ascending", "descending"],
        )
        self.assertEqual(
            [MODULE.hop_index_for_range(item[2], [200.0, 400.0]) for item in crossings],
            [1, 1, 2, 2],
        )

    def test_exact_vertex_is_not_double_counted(self) -> None:
        crossings = MODULE.altitude_crossing_segments(
            [0.0, 100.0, 200.0], [0.0, 10.0, 20.0], 10.0
        )
        self.assertEqual(len(crossings), 1)
        self.assertAlmostEqual(crossings[0][2], 100.0)

    def test_crossing_records_keep_ray_hop_and_direction(self) -> None:
        path = np.zeros((5, MODULE.PATH_FIELDS), dtype=float)
        path[:, 0] = [0.0, 100.0, 200.0, 300.0, 400.0]
        path[:, 1] = [0.0, 20.0, 0.0, 20.0, 0.0]
        path[:, 2] = path[:, 0] * 1.1
        outcomes = [
            {"ray_label": 1, "ray_label_meaning": "ground_return"},
            {"ray_label": 1, "ray_label_meaning": "ground_return"},
        ]
        records = MODULE.extract_crossing_records(
            path,
            [10.0],
            [200.0, 400.0],
            outcomes,
            7,
            2.0,
            {"latitude_deg": 0.0, "longitude_deg": 0.0},
            90.0,
            MODULE.EARTH_EQUATORIAL_RADIUS_KM,
        )
        self.assertEqual(len(records), 4)
        self.assertEqual([record["hop_index"] for record in records], [1, 1, 2, 2])
        self.assertEqual([record["hop_crossing_ordinal"] for record in records], [1, 2, 1, 2])
        self.assertTrue(all(record["ray_index"] == 7 for record in records))


class ScreenAndValidationTest(unittest.TestCase):
    def test_predeclared_nonuniform_fans_are_explicit_sensitivities(self) -> None:
        primary = MODULE.production_elevations_deg()
        worked = MODULE.production_elevations_deg(include_worked_example=True)
        half = MODULE.production_elevations_deg(half_step=True)
        self.assertEqual(len(primary), 295)
        self.assertEqual(len(worked), 296)
        self.assertIn(1.981, worked)
        self.assertNotIn(1.981, primary)
        self.assertEqual(len(half), 590)
        self.assertEqual((primary[0], primary[-1]), (0.5, 89.5))
        self.assertEqual((half[0], half[-1]), (0.5, 89.75))

    def test_explicit_fan_requires_provenance_and_preserves_exact_values(self) -> None:
        raw = MODULE.published_fixture_job()
        raw["elevation_fan"] = {"elevations_deg": [0.5, 1.981, 2.0]}
        with self.assertRaises(MODULE.WorkerError):
            MODULE.validate_and_normalize_job(raw)
        raw["elevation_fan"]["provenance"] = "worked-example fixture"
        normalized = MODULE.validate_and_normalize_job(raw)
        self.assertEqual(
            normalized["elevation_fan"]["elevations_deg"], [0.5, 1.981, 2.0]
        )

    def test_surface_screen_checks_every_completed_hop(self) -> None:
        landings = [
            {"ground_range_km": 1000.0, "ray_index": 0, "hop_index": 1},
            {"ground_range_km": 1998.0, "ray_index": 0, "hop_index": 2},
            {"ground_range_km": 3100.0, "ray_index": 1, "hop_index": 1},
        ]
        summary = MODULE.minimum_error_summaries([2000.0], landings)[0]
        self.assertEqual(summary["candidate_count"], 3)
        self.assertEqual(summary["minimum_absolute_error_km"], 2.0)
        self.assertEqual(summary["best_topology"]["hop_index"], 2)

    def test_altitude_screen_is_stratified_by_common_altitude(self) -> None:
        records = [
            {
                "ground_range_km": 1001.0,
                "aircraft_altitude_km": 10.0,
                "ray_index": 0,
                "hop_index": 1,
            },
            {
                "ground_range_km": 1020.0,
                "aircraft_altitude_km": 11.0,
                "ray_index": 1,
                "hop_index": 1,
            },
        ]
        summaries = MODULE.minimum_error_summaries([1000.0], records, [10.0, 11.0])
        self.assertEqual([row["minimum_absolute_error_km"] for row in summaries], [1.0, 20.0])

    def test_published_fixture_is_valid_and_uses_primary_radius(self) -> None:
        raw = MODULE.published_fixture_job()
        normalized = MODULE.validate_and_normalize_job(raw)
        self.assertEqual(normalized["earth_radius_km"], 6378.137)
        self.assertEqual(normalized["runtime"]["ray_batch_size"], 24)
        self.assertEqual(normalized["runtime"]["nrt_num_threads"], 1)
        self.assertEqual(normalized["elevation_fan"]["ray_count"], 179)
        self.assertAlmostEqual(normalized["bearing_deg"], 99.34274724706256)
        self.assertEqual(normalized["target_ground_ranges_km"], [12273.9])
        self.assertAlmostEqual(
            normalized["reference"]["simple_sphere_path_from_locator_center_km"],
            12289.639300868475,
        )
        self.assertAlmostEqual(
            normalized["reference"]["declared_minus_simple_sphere_path_km"],
            -15.739300868474966,
        )
        self.assertLessEqual(
            normalized["target_ground_ranges_km"][0],
            math.pi * normalized["earth_radius_km"],
        )

    def test_auxiliary_direct_fixture_is_explicit_sensitivity(self) -> None:
        normalized = MODULE.validate_and_normalize_job(
            MODULE.published_auxiliary_direct_fixture_job()
        )
        self.assertIn("auxiliary-direct-sensitivity", normalized["job_id"])
        self.assertAlmostEqual(normalized["bearing_deg"], 99.31810164983743)
        self.assertAlmostEqual(
            normalized["target_ground_ranges_km"][0], 12275.422925969599
        )

    def test_rejects_target_beyond_shortest_branch(self) -> None:
        raw = MODULE.published_fixture_job()
        raw["target_ground_ranges_km"] = [
            math.pi * MODULE.EARTH_EQUATORIAL_RADIUS_KM + 1.0
        ]
        with self.assertRaises(MODULE.WorkerError):
            MODULE.validate_and_normalize_job(raw)


if __name__ == "__main__":
    unittest.main()
