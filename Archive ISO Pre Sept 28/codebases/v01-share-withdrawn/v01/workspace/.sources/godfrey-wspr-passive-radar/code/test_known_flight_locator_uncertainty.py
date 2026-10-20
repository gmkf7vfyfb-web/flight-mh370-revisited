#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import sys
import unittest

import numpy as np


CODE = pathlib.Path(__file__).resolve().parent
DATA = CODE.parent / "data" / "known-flight"
sys.path.insert(0, str(CODE))

import audit_known_flight_locator_uncertainty as audit
import audit_locator_witness_controls as control_audit
import run_locator_witness_pharlap as witness_runner
import wspr_pharlap_control as control


class LocatorUncertaintyTests(unittest.TestCase):
    def test_maidenhead_bounds_have_declared_size_and_center(self) -> None:
        south, north, west, east = audit.maidenhead_cell_bounds("JO00bs")
        self.assertAlmostEqual(north - south, 1.0 / 24.0)
        self.assertAlmostEqual(east - west, 1.0 / 12.0)
        self.assertAlmostEqual((south + north) / 2.0, 50.770833333333336)
        self.assertAlmostEqual((west + east) / 2.0, 0.125)

    def test_independent_count_is_bipartite_matching_not_spot_count(self) -> None:
        spots = {
            1: audit.Spot(1, "A", "X", "AA00AA", "BB00BB"),
            2: audit.Spot(2, "A", "Y", "AA00AA", "BB00BB"),
            3: audit.Spot(3, "B", "Y", "AA00AA", "BB00BB"),
        }
        self.assertEqual(audit.maximum_independent_links(spots, spots), 2)

    def test_frozen_nearest_slots_and_cell_centres_reconstruct(self) -> None:
        spots, pairs, truths = audit.read_inputs(
            DATA / "known_flight_pair_locations.csv.gz",
            DATA / "known_flight_spot_records.csv.gz",
            DATA / "known_flight_truth_references.csv",
        )
        self.assertEqual(len(pairs), 59)
        self.assertEqual(
            {epoch: sum(pair.epoch_id == epoch for pair in pairs) for epoch in truths},
            {
                "mh371_0404": 4,
                "mh371_0611": 9,
                "mh371_0648": 8,
                "mh370_1642": 2,
                "mh370_1656": 27,
                "mh370_1707": 9,
            },
        )
        _rows, metadata = audit.evaluate(
            spots, pairs, truths, sample_power=1, seed=370371, batch_size=2
        )
        self.assertLess(metadata["maximum_cell_center_reconstruction_error_km"], 0.002)
        self.assertEqual(metadata["global_station_count"], 62)

    def test_station_sampling_is_coherent_and_inside_cells(self) -> None:
        stations = (("ONE", "JO00BS"), ("TWO", "EN52TA"))
        uniforms = np.asarray([[0.0, 0.0, 1.0, 1.0], [0.5, 0.5, 0.5, 0.5]])
        vectors = audit.station_points(uniforms, stations)
        latitudes = np.degrees(np.arcsin(vectors[:, :, 2]))
        longitudes = np.degrees(np.arctan2(vectors[:, :, 1], vectors[:, :, 0]))
        for station_index, (_callsign, locator) in enumerate(stations):
            south, north, west, east = audit.maidenhead_cell_bounds(locator)
            self.assertTrue(np.all(latitudes[:, station_index] >= south - 1e-12))
            self.assertTrue(np.all(latitudes[:, station_index] <= north + 1e-12))
            self.assertTrue(np.all(longitudes[:, station_index] >= west - 1e-12))
            self.assertTrue(np.all(longitudes[:, station_index] <= east + 1e-12))

    def test_explicit_resolver_reduces_to_primary_resolver_at_cell_centres(self) -> None:
        records = control.read_spot_records(DATA / "known_flight_spot_records.csv.gz")
        source = records[185947658]
        transmitter = control.maidenhead_six_character_center(source.transmitter_locator)
        receiver = control.maidenhead_six_character_center(source.receiver_locator)
        centered = control.SpotRecord(
            spot_id=source.spot_id,
            time_utc=source.time_utc,
            frequency_hz=source.frequency_hz,
            transmitter=source.transmitter,
            receiver=source.receiver,
            transmitter_locator=source.transmitter_locator,
            receiver_locator=source.receiver_locator,
            archive_transmitter_lat_deg=transmitter[0],
            archive_transmitter_lon_deg_e=transmitter[1],
            archive_receiver_lat_deg=receiver[0],
            archive_receiver_lon_deg_e=receiver[1],
        )
        target = (8.16183655021287, 117.437610210462)
        primary = control.PublishedSphericalRouteResolver(
            include_auxiliary_diagnostics=False
        )
        explicit = witness_runner.ExplicitCoordinateResolver()
        for endpoint in control.ENDPOINTS:
            expected = primary.resolve(centered, endpoint, *target)
            actual = explicit.resolve(centered, endpoint, *target)
            self.assertEqual(actual.branch, expected.branch)
            self.assertAlmostEqual(actual.origin_latitude_deg, expected.origin_latitude_deg)
            self.assertAlmostEqual(actual.origin_longitude_deg_e, expected.origin_longitude_deg_e)
            self.assertAlmostEqual(actual.initial_bearing_deg, expected.initial_bearing_deg)
            self.assertAlmostEqual(actual.target_range_km, expected.target_range_km)
            self.assertAlmostEqual(
                actual.primary_cross_track_mismatch_km,
                expected.primary_cross_track_mismatch_km,
            )

    def test_joint_witness_has_no_nearby_retained_control_proposal(self) -> None:
        groups, spots, truth = control_audit.perturbed_epoch(
            "mh370_1642",
            23526,
            DATA / "known_flight_pair_locations.csv.gz",
            DATA / "known_flight_spot_records.csv.gz",
            DATA / "known_flight_truth_references.csv",
            370371,
        )
        actual = next(
            pair
            for pair in groups[("actual_time", truth.physical_slot)]
            if pair.candidate_id == "known-flight:mh370_1642:00000658"
        )
        proposals = control_audit.strict_proposals(groups, spots)
        control_distances = [
            control.great_circle_distance_km(
                actual.latitude_deg,
                actual.longitude_deg_e,
                float(proposal["latitude_deg"]),
                float(proposal["longitude_deg_e"]),
            )
            for proposal in proposals
            if proposal["condition"] != "actual_time"
        ]
        self.assertEqual(len(groups), 29)
        self.assertEqual(sum(map(len, groups.values())), 357)
        self.assertAlmostEqual(min(control_distances), 198.9856239009557, places=6)


if __name__ == "__main__":
    unittest.main()
