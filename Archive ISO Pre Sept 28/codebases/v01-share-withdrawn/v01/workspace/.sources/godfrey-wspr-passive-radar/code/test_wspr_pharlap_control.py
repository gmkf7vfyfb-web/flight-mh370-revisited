#!/usr/bin/env python3
"""Focused tests for the blind WSPR/PHaRLAP control pipeline."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))

import wspr_pharlap_control as control


class FixtureRouteResolver:
    """Simple sphere used only to test grouping; never a production default."""

    radius_km = 6378.137

    @staticmethod
    def _maidenhead_center(locator: str) -> tuple[float, float]:
        value = locator.strip().upper()
        if len(value) != 6:
            raise ValueError("fixture requires exact six-character locators")
        longitude = (
            -180.0 + (ord(value[0]) - ord("A")) * 20.0
            + int(value[2]) * 2.0 + (ord(value[4]) - ord("A")) / 12.0
            + 1.0 / 24.0
        )
        latitude = (
            -90.0 + (ord(value[1]) - ord("A")) * 10.0
            + int(value[3]) + (ord(value[5]) - ord("A")) / 24.0
            + 1.0 / 48.0
        )
        return latitude, longitude

    @staticmethod
    def _unit(latitude: float, longitude: float) -> tuple[float, float, float]:
        phi, lam = math.radians(latitude), math.radians(longitude)
        cosine = math.cos(phi)
        return cosine * math.cos(lam), cosine * math.sin(lam), math.sin(phi)

    @staticmethod
    def _cross(a, b):
        return (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        )

    @staticmethod
    def _dot(a, b):
        return sum(first * second for first, second in zip(a, b))

    @classmethod
    def _normalize(cls, value):
        norm = math.sqrt(cls._dot(value, value))
        return tuple(component / norm for component in value)

    def resolve(self, spot, endpoint, candidate_latitude_deg, candidate_longitude_deg_e):
        transmitter = self._unit(*self._maidenhead_center(spot.transmitter_locator))
        receiver = self._unit(*self._maidenhead_center(spot.receiver_locator))
        candidate = self._unit(candidate_latitude_deg, candidate_longitude_deg_e)
        normal = self._normalize(self._cross(transmitter, receiver))
        if endpoint == "transmitter":
            origin, tangent = transmitter, self._cross(normal, transmitter)
            latitude, longitude = self._maidenhead_center(spot.transmitter_locator)
        else:
            origin = receiver
            tangent = tuple(-value for value in self._cross(normal, receiver))
            latitude, longitude = self._maidenhead_center(spot.receiver_locator)
        phase = math.atan2(self._dot(candidate, tangent), self._dot(candidate, origin))
        phase %= 2.0 * math.pi
        toward_other = phase <= math.pi
        distance_angle = phase if toward_other else 2.0 * math.pi - phase

        phi, lam = math.radians(latitude), math.radians(longitude)
        east = (-math.sin(lam), math.cos(lam), 0.0)
        north = (
            -math.sin(phi) * math.cos(lam),
            -math.sin(phi) * math.sin(lam),
            math.cos(phi),
        )
        direction = tangent if toward_other else tuple(-value for value in tangent)
        bearing = math.degrees(math.atan2(self._dot(direction, east), self._dot(direction, north))) % 360.0
        if math.isclose(bearing, 360.0, abs_tol=1e-12):
            bearing = 0.0
        return control.ResolvedRoute(
            branch="toward_other_endpoint" if toward_other else "away_from_other_endpoint",
            origin_latitude_deg=latitude,
            origin_longitude_deg_e=longitude,
            initial_bearing_deg=bearing,
            target_range_km=self.radius_km * distance_angle,
            geometry_model="test-only-6378.137-km-geodetic-sphere",
        )


def make_spot(spot_id: int, transmitter: str, receiver: str) -> control.SpotRecord:
    return control.SpotRecord(
        spot_id=spot_id,
        time_utc="2014-03-08 00:20:00",
        frequency_hz=14_097_100.0,
        transmitter=transmitter,
        receiver=receiver,
        transmitter_locator="IO90IW",
        receiver_locator="JN49CM",
        archive_transmitter_lat_deg=50.938,
        archive_transmitter_lon_deg_e=-1.292,
        archive_receiver_lat_deg=49.521,
        archive_receiver_lon_deg_e=8.208,
    )


def make_pair(
    candidate_id: str,
    first: int,
    second: int,
    latitude: float,
    altitude_slot="2014-03-08 00:20:00",
    epoch_id="fixture-epoch",
):
    return control.CandidatePair(
        candidate_id=candidate_id,
        epoch_id=epoch_id,
        condition="actual_time",
        physical_slot=altitude_slot,
        radio_time="2014-03-08 00:20:00",
        spot_id_1=first,
        spot_id_2=second,
        transmitter_1=f"TX{first}", receiver_1=f"RX{first}",
        transmitter_2=f"TX{second}", receiver_2=f"RX{second}",
        latitude_deg=latitude, longitude_deg_e=95.0,
    )


def result_documents(
    plan: control.RoutePlan,
    surface_candidates: set[str],
    altitude_candidates: dict[str, tuple[float, ...]],
):
    documents = []
    for job in plan.jobs:
        targets = []
        for target in job.targets:
            surface = None
            if target.candidate_id in surface_candidates:
                surface = {"minimum_error_km": 2.0, "mode": {"hop": 3, "ray_label": 1}}
            altitude_rows = [{
                "altitude_km": altitude,
                "match": {"minimum_error_km": 3.0, "mode": {"hop": 2, "ray_label": 1}},
            } for altitude in altitude_candidates.get(target.candidate_id, ())]
            targets.append({
                "candidate_id": target.candidate_id,
                "epoch_id": target.epoch_id,
                "surface_endpoint": surface,
                "aircraft_altitudes": altitude_rows,
            })
        documents.append({
            "schema": control.ROUTE_RESULT_SCHEMA,
            "job_key": {
                "spot_id": job.key.spot_id,
                "endpoint": job.key.endpoint,
                "branch": job.key.branch,
            },
            "targets": targets,
        })
    return documents


class ControlPipelineTests(unittest.TestCase):
    def test_published_spherical_worked_geometry(self):
        origin = control.maidenhead_six_character_center("IO90IW")
        distance, bearing = control.published_spherical_inverse(
            *origin, -21.502, 94.972
        )
        self.assertAlmostEqual(bearing, 99.342747247, places=7)
        self.assertAlmostEqual(distance, 12_289.639301, places=5)
        # The screenshot annotation is about 12,273.9 km; the declared
        # R=6378.137 sphere is within 16 km of that rounded/displayed value.
        self.assertLess(abs(distance - 12_273.9), 20.0)
        self.assertIsInstance(
            control.default_route_resolver(), control.PublishedSphericalRouteResolver
        )

    def test_surface_and_aircraft_altitude_screens_are_parallel(self):
        pairs = (
            make_pair("surface-only", 1, 2, -35.0),
            make_pair("altitude-only", 3, 4, -35.1),
        )
        spots = {index: make_spot(index, f"TX{index}", f"RX{index}") for index in range(1, 5)}
        plan = control.build_route_plan(pairs, spots, FixtureRouteResolver())
        results = control.parse_route_results(result_documents(
            plan,
            surface_candidates={"surface-only"},
            altitude_candidates={"altitude-only": (9.5,)},
        ))
        surface = control.apply_surface_endpoint_screen(plan, results, 25.0)
        altitude = control.apply_common_altitude_screen(plan, results, 25.0)
        self.assertEqual([item.pair.candidate_id for item in surface], ["surface-only"])
        self.assertEqual([item.pair.candidate_id for item in altitude], ["altitude-only"])
        self.assertEqual(altitude[0].altitude_km, 9.5)

    def test_altitude_must_be_common_to_all_four_legs(self):
        pair = make_pair("candidate", 1, 2, -35.0)
        spots = {index: make_spot(index, f"TX{index}", f"RX{index}") for index in (1, 2)}
        plan = control.build_route_plan((pair,), spots, FixtureRouteResolver())
        documents = result_documents(plan, set(), {"candidate": (9.0, 10.0)})
        documents[0]["targets"][0]["aircraft_altitudes"] = [{
            "altitude_km": 11.0,
            "match": {"minimum_error_km": 1.0, "mode": {"hop": 2}},
        }]
        results = control.parse_route_results(documents)
        self.assertEqual(control.apply_common_altitude_screen(plan, results, 25.0), ())

    def test_incomplete_route_results_are_rejected_not_silently_omitted(self):
        pair = make_pair("candidate", 1, 2, -35.0)
        spots = {
            index: make_spot(index, f"TX{index}", f"RX{index}")
            for index in (1, 2)
        }
        plan = control.build_route_plan((pair,), spots, FixtureRouteResolver())
        documents = result_documents(plan, {"candidate"}, {})
        results = control.parse_route_results(documents[:-1])
        with self.assertRaisesRegex(ValueError, "incomplete propagation results"):
            control.apply_surface_endpoint_screen(plan, results, 25.0)

    def test_clustering_never_combines_altitudes(self):
        pair_a = make_pair("a", 1, 2, -35.000)
        pair_b = make_pair("b", 3, 4, -35.005)
        one_each = (
            control.ScreenedPair(pair_a, control.ALTITUDE_SCREEN, 9.0, {}),
            control.ScreenedPair(pair_b, control.ALTITUDE_SCREEN, 10.0, {}),
        )
        self.assertEqual(control.cluster_screened_pairs(one_each), ())
        same_height = (
            control.ScreenedPair(pair_a, control.ALTITUDE_SCREEN, 9.0, {}),
            control.ScreenedPair(pair_b, control.ALTITUDE_SCREEN, 9.0, {}),
        )
        clusters = control.cluster_screened_pairs(same_height)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0].altitude_km, 9.0)
        self.assertEqual(clusters[0].independent_links, 4)

    def test_clustering_never_manufactures_support_across_slots_or_panels(self):
        first = make_pair(
            "first", 1, 2, -35.000,
            altitude_slot="2014-03-08 00:20:00",
        )
        second_slot = make_pair(
            "second-slot", 3, 4, -35.001,
            altitude_slot="2014-03-08 00:22:00",
        )
        screened = (
            control.ScreenedPair(first, control.SURFACE_SCREEN, None, {}),
            control.ScreenedPair(
                second_slot, control.SURFACE_SCREEN, None, {}
            ),
        )
        # Each slot contains only two independent reports. Pooling the two
        # slots would incorrectly create a four-link cluster above threshold.
        self.assertEqual(control.cluster_screened_pairs(screened), ())

        other_panel = control.replace(
            second_slot,
            candidate_id="second-panel",
            condition="minus_60_min",
            physical_slot=first.physical_slot,
        )
        screened = (
            control.ScreenedPair(first, control.SURFACE_SCREEN, None, {}),
            control.ScreenedPair(
                other_panel, control.SURFACE_SCREEN, None, {}
            ),
        )
        # The same invariant applies to the three control conditions.
        self.assertEqual(control.cluster_screened_pairs(screened), ())

    def test_residualization_is_symmetric_with_exact_altitude_sensitivity(self):
        def cluster(condition, latitude, altitude):
            return control.SpatialCluster(
                screen=control.ALTITUDE_SCREEN,
                epoch_id="epoch",
                condition=condition,
                physical_slot="slot",
                altitude_km=altitude,
                feasible_altitudes_km=(altitude,),
                cluster_rank=1,
                latitude_deg=latitude,
                longitude_deg_e=95.0,
                pair_intersections=3,
                support_links=4,
                independent_links=4,
                support_spot_ids=(1, 2, 3, 4),
                center_candidate_id=condition,
                source_altitude_clusters=1,
            )
        values = (
            cluster("minus_60_min", -35.00, 10.0),
            cluster("actual_time", -35.01, 10.0),
            cluster("plus_60_min", -37.00, 10.0),
            cluster("plus_60_min", -35.01, 11.0),
        )
        residuals = control.symmetric_residuals(
            values, 25.0, altitude_matching="exact_altitude_sensitivity"
        )
        flags = [item.is_residual for item in residuals]
        self.assertEqual(flags, [False, False, True, True])

    def test_altitude_collapse_prevents_slice_pseudoreplication(self):
        def cluster(condition, latitude, altitude, rank):
            return control.SpatialCluster(
                screen=control.ALTITUDE_SCREEN,
                epoch_id="epoch",
                condition=condition,
                physical_slot="slot",
                altitude_km=altitude,
                feasible_altitudes_km=(altitude,),
                cluster_rank=rank,
                latitude_deg=latitude,
                longitude_deg_e=95.0,
                pair_intersections=3,
                support_links=4,
                independent_links=4,
                support_spot_ids=(1, 2, 3, 4),
                center_candidate_id=f"{condition}-{altitude}",
                source_altitude_clusters=1,
                source_altitude_cluster_ids=(f"{condition}-{altitude}",),
            )
        slices = (
            cluster("actual_time", -35.000, 9.5, 1),
            cluster("actual_time", -35.002, 10.0, 2),
            cluster("actual_time", -35.004, 10.5, 3),
            cluster("minus_60_min", -35.003, 10.0, 1),
        )
        source_residuals = control.symmetric_residuals(slices, 25.0)
        self.assertEqual(
            [item.is_residual for item in source_residuals],
            [False, False, False, False],
        )
        collapsed = control.collapse_altitude_clusters(
            tuple(
                item.cluster for item in source_residuals if item.is_residual
            ),
            25.0,
        )
        self.assertEqual(collapsed, ())

    def test_source_residual_precedes_collapse_when_absorbed_member_is_persistent(self):
        def cluster(condition, latitude, altitude, rank, support):
            return control.SpatialCluster(
                screen=control.ALTITUDE_SCREEN,
                epoch_id="epoch",
                condition=condition,
                physical_slot="slot",
                altitude_km=altitude,
                feasible_altitudes_km=(altitude,),
                cluster_rank=rank,
                latitude_deg=latitude,
                longitude_deg_e=95.0,
                pair_intersections=support,
                support_links=support,
                independent_links=min(4, support),
                support_spot_ids=tuple(range(1, support + 1)),
                center_candidate_id=f"{condition}-{rank}",
                source_altitude_clusters=1,
                source_altitude_cluster_ids=(f"{condition}-{rank}",),
            )
        actual_representative = cluster("actual_time", 0.00, 9.5, 1, 6)
        actual_absorbed = cluster("actual_time", 0.20, 10.0, 2, 4)
        control_member = cluster("minus_60_min", 0.40, 11.0, 1, 4)
        values = (actual_representative, actual_absorbed, control_member)
        collapsed_first = control.collapse_altitude_clusters(values, 25.0)
        self.assertEqual(len(collapsed_first), 2)
        source_residuals = control.symmetric_residuals(values, 25.0)
        flags = {
            item.cluster.center_candidate_id: item.is_residual
            for item in source_residuals
        }
        self.assertEqual(flags, {
            "actual_time-1": True,
            "actual_time-2": False,
            "minus_60_min-1": False,
        })
        display = control.collapse_altitude_clusters(
            tuple(item.cluster for item in source_residuals if item.is_residual),
            25.0,
        )
        self.assertEqual(len(display), 1)
        self.assertEqual(display[0].center_candidate_id, "actual_time-1")

    def test_overlapping_slots_never_mix_or_subtract_across_epochs(self):
        def cluster(epoch, condition, latitude):
            return control.SpatialCluster(
                screen=control.SURFACE_SCREEN,
                epoch_id=epoch,
                condition=condition,
                physical_slot="overlapping-slot",
                altitude_km=None,
                feasible_altitudes_km=(),
                cluster_rank=1,
                latitude_deg=latitude,
                longitude_deg_e=100.0,
                pair_intersections=2,
                support_links=4,
                independent_links=3,
                support_spot_ids=(1, 2, 3, 4),
                center_candidate_id=f"{epoch}-{condition}",
            )
        values = (
            cluster("mh370_1642", "actual_time", 4.0),
            cluster("mh370_1656", "minus_60_min", 4.0),
        )
        residuals = control.symmetric_residuals(values, 25.0)
        self.assertEqual([item.is_residual for item in residuals], [True, True])
        blocks = control.count_clusters_by_block(values)
        self.assertEqual(len(blocks), 2)

    def test_primary_inference_blocks_adjacent_slots_by_epoch(self):
        base = control.SpatialCluster(
            screen=control.SURFACE_SCREEN,
            epoch_id="epoch",
            condition="actual_time",
            physical_slot="slot-one",
            altitude_km=None,
            feasible_altitudes_km=(),
            cluster_rank=1,
            latitude_deg=4.0,
            longitude_deg_e=100.0,
            pair_intersections=2,
            support_links=4,
            independent_links=3,
            support_spot_ids=(1, 2, 3, 4),
            center_candidate_id="one",
        )
        other = control.replace(
            base, physical_slot="slot-two", center_candidate_id="two"
        )
        primary = control.count_clusters_by_block((base, other))
        sensitivity = control.count_clusters_by_block(
            (base, other), "physical_slot_sensitivity"
        )
        self.assertEqual(len(primary), 1)
        self.assertEqual(primary["epoch|surface_endpoint"]["actual_time"], 2)
        self.assertEqual(len(sensitivity), 2)

    def test_truth_is_scored_only_after_selection(self):
        cluster = control.SpatialCluster(
            screen=control.SURFACE_SCREEN,
            epoch_id="epoch",
            condition="actual_time",
            physical_slot="slot",
            altitude_km=None,
            feasible_altitudes_km=(),
            cluster_rank=1,
            latitude_deg=-35.0,
            longitude_deg_e=95.0,
            pair_intersections=4,
            support_links=6,
            independent_links=4,
            support_spot_ids=(1, 2, 3, 4),
            center_candidate_id="center",
        )
        score = control.score_truth_references(
            (cluster,),
            (control.TruthReference(
                "known", "epoch", "actual_time", -35.01, 95.0,
                physical_slot="slot",
            ),),
            25.0,
        )[0]
        self.assertTrue(score.recovered)
        self.assertLess(score.nearest_distance_km, 2.0)

    def test_truth_cannot_recover_from_another_epoch_or_physical_slot(self):
        cluster = control.SpatialCluster(
            screen=control.SURFACE_SCREEN,
            epoch_id="epoch-a",
            condition="actual_time",
            physical_slot="slot-a",
            altitude_km=None,
            feasible_altitudes_km=(),
            cluster_rank=1,
            latitude_deg=-35.0,
            longitude_deg_e=95.0,
            pair_intersections=4,
            support_links=6,
            independent_links=4,
            support_spot_ids=(1, 2, 3, 4),
            center_candidate_id="same-position",
        )
        scores = control.score_truth_references(
            (cluster,),
            (
                control.TruthReference(
                    "wrong-epoch", "epoch-b", "actual_time", -35.0, 95.0,
                    physical_slot="slot-a",
                ),
                control.TruthReference(
                    "wrong-slot", "epoch-a", "actual_time", -35.0, 95.0,
                    physical_slot="slot-b",
                ),
            ),
        )
        self.assertEqual([score.eligible_clusters for score in scores], [0, 0])
        self.assertEqual([score.recovered for score in scores], [False, False])

    def test_altitude_truth_requires_horizontal_and_feasible_altitude(self):
        cluster = control.SpatialCluster(
            screen=control.ALTITUDE_SCREEN,
            epoch_id="epoch",
            condition="actual_time",
            physical_slot="slot",
            altitude_km=None,
            feasible_altitudes_km=(9.0, 9.5, 10.0),
            cluster_rank=1,
            latitude_deg=-35.0,
            longitude_deg_e=95.0,
            pair_intersections=4,
            support_links=6,
            independent_links=4,
            support_spot_ids=(1, 2, 3, 4),
            center_candidate_id="center",
            source_altitude_clusters=3,
        )
        close_altitude, far_altitude = control.score_truth_references(
            (cluster,),
            (
                control.TruthReference(
                    "close", "epoch", "actual_time", -35.01, 95.0,
                    physical_slot="slot", screen=control.ALTITUDE_SCREEN,
                    altitude_km=10.4,
                ),
                control.TruthReference(
                    "far", "epoch", "actual_time", -35.01, 95.0,
                    physical_slot="slot", screen=control.ALTITUDE_SCREEN,
                    altitude_km=11.0,
                ),
            ),
            25.0,
            altitude_allowance_km=0.5,
        )
        self.assertTrue(close_altitude.recovered)
        self.assertAlmostEqual(close_altitude.nearest_altitude_gap_km, 0.4)
        self.assertFalse(far_altitude.recovered)
        self.assertAlmostEqual(far_altitude.nearest_altitude_gap_km, 1.0)

    def test_primary_truth_requires_time_matched_slot(self):
        with self.assertRaises(ValueError):
            control.score_truth_references(
                (),
                (control.TruthReference(
                    "known", "epoch", "actual_time", -35.0, 95.0
                ),),
            )

    def test_exact_blocked_sign_flip(self):
        result = control.exact_blocked_sign_flip({
            "one": {"minus_60_min": 1, "actual_time": 4, "plus_60_min": 1},
            "two": {"minus_60_min": 2, "actual_time": 1, "plus_60_min": 2},
        })
        self.assertEqual(result["blocks"], 2)
        self.assertEqual(result["nonzero_blocks"], 2)
        self.assertAlmostEqual(result["observed_sum_difference"], 2.0)

    def test_worker_adapter_restores_candidate_identity(self):
        pair = make_pair("candidate", 1, 2, -35.0)
        spots = {index: make_spot(index, f"TX{index}", f"RX{index}") for index in (1, 2)}
        plan = control.build_route_plan((pair,), spots, FixtureRouteResolver())
        route = plan.jobs[0]
        worker_input = control.worker_job_inputs(plan, aircraft_altitudes_km=(10.0,))[0]
        self.assertEqual(worker_input["schema"], control.WORKER_JOB_SCHEMA)
        target_range = route.targets[0].target_range_km
        worker_result = {
            "schema": control.WORKER_RESULT_SCHEMA,
            "job": {"job_id": worker_input["job_id"]},
            "surface_endpoint_screen": [{
                "target_ground_range_km": target_range,
                "minimum_absolute_error_km": 2.0,
                "best_topology": {"ray_index": 1, "hop_index": 3},
            }],
            "aircraft_altitude_screen": [{
                "target_ground_range_km": target_range,
                "aircraft_altitude_km": 10.0,
                "minimum_absolute_error_km": 4.0,
                "best_topology": {"ray_index": 2, "hop_index": 2},
            }],
        }
        adapted = control.adapt_worker_result(route, worker_result)
        parsed = control.parse_route_results((adapted,))
        result = parsed[(route.key, "candidate")]
        self.assertEqual(result.surface_endpoint.minimum_error_km, 2.0)
        self.assertEqual(result.aircraft_altitudes[10.0].minimum_error_km, 4.0)
        self.assertEqual(result.surface_endpoint.mode["worker_job_id"], worker_input["job_id"])

    def test_generated_job_passes_worker_schema_validation(self):
        try:
            import pharlap_raytrace_worker as worker
        except ImportError:
            self.skipTest("PHaRLAP worker numerical environment is unavailable")
        pair = make_pair("candidate", 1, 2, -35.0)
        spots = {index: make_spot(index, f"TX{index}", f"RX{index}") for index in (1, 2)}
        plan = control.build_route_plan((pair,), spots, FixtureRouteResolver())
        raw = control.worker_job_inputs(plan, aircraft_altitudes_km=(9.5, 10.0))[0]
        normalized = worker.validate_and_normalize_job(raw)
        self.assertEqual(normalized["schema"], worker.SCHEMA)
        self.assertEqual(normalized["utc"].isoformat(), "2014-03-08T00:20:56.242000+00:00")
        self.assertEqual(normalized["aircraft_altitudes_km"], [9.5, 10.0])
        self.assertEqual(normalized["runtime"]["nrt_num_threads"], 1)
        self.assertEqual(
            normalized["reference"]["wspr_slot_midpoint_offset_seconds"], 56.242
        )
        self.assertEqual(
            normalized["reference"]["wspr_transmission_duration_seconds"], 110.484
        )


class FrozenCandidateRegressionTests(unittest.TestCase):
    legacy = Path(
        "/jackbox/home/.iso/thread-storage/"
        "MH370-legacy-pre-refactor-20260824/analyses"
    )

    def setUp(self):
        if not self.legacy.exists():
            self.skipTest("read-only frozen legacy analyses are not mounted")

    def test_frozen_seventh_and_sixth_candidate_counts(self):
        seventh = control.read_candidate_pairs(
            self.legacy / "D-0029-public-core-post7-wspr-panels/outputs/"
            "public_core_sixchar_pair_locations.csv.gz",
            "seventh-arc",
        )
        sixth = control.read_candidate_pairs(
            self.legacy / "D-0030-sixth-arc-public-core-wspr/outputs/"
            "sixth_arc_pair_locations.csv.gz",
            "sixth-arc",
        )
        self.assertEqual(len(seventh), 14_026)
        self.assertEqual(control.condition_counts(seventh), {
            "minus_60_min": 5_136, "actual_time": 4_406, "plus_60_min": 4_484,
        })
        self.assertEqual(len(sixth), 7_272)
        self.assertEqual(control.condition_counts(sixth), {
            "minus_60_min": 3_033, "actual_time": 2_420, "plus_60_min": 1_819,
        })

    def test_frozen_sixth_fixed_branch_jobs_are_grouped(self):
        pairs = control.read_candidate_pairs(
            self.legacy / "D-0030-sixth-arc-public-core-wspr/outputs/"
            "sixth_arc_pair_locations.csv.gz",
            "sixth-arc",
        )
        spots = control.read_spot_records(
            self.legacy / "D-0010-wspr-trajectory-diagnostic/inputs/"
            "wspr_20140307_1330_20140308_0500.csv.gz"
        )
        plan = control.build_route_plan(
            pairs, spots,
            control.PublishedSphericalRouteResolver(include_auxiliary_diagnostics=False),
        )
        self.assertEqual(len(plan.jobs), 3_863)
        self.assertEqual(len(plan.leg_jobs), 4 * len(pairs))
        self.assertTrue(any(len(job.targets) > 1 for job in plan.jobs))

    def test_known_flight_truth_audit_remains_separate(self):
        path = self.legacy / (
            "D-0033-known-flight-wspr-controls/outputs/"
            "known_flight_bto_arc_input_audit.csv"
        )
        with path.open(newline="") as handle:
            import csv
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 6)
        self.assertEqual({row["flight"] for row in rows}, {"MH370", "MH371"})


if __name__ == "__main__":
    unittest.main()
