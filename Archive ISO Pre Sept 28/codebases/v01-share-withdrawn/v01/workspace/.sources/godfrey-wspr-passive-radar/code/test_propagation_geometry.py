#!/usr/bin/env python3

import importlib.util
import json
import math
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("propagation_geometry.py")
SPEC = importlib.util.spec_from_file_location("propagation_geometry", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PropagationGeometryTest(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.parameters = json.loads(
            (root / "data" / "physics_parameters.json").read_text()
        )

    def test_triangular_fraction(self) -> None:
        self.assertAlmostEqual(MODULE.fraction_below_altitude(10.0, 100.0), 0.1)
        self.assertAlmostEqual(MODULE.fraction_below_altitude(12.0, 300.0), 0.04)

    def test_representative_five_hop_route(self) -> None:
        metrics = MODULE.triangular_route_metrics(15000.0, 5, 250.0, 10.0)
        self.assertAlmostEqual(metrics["path_fraction_below_altitude"], 0.04)
        self.assertAlmostEqual(
            metrics["total_geometric_path_km"],
            5.0 * 2.0 * math.hypot(1500.0, 250.0),
        )
        self.assertAlmostEqual(metrics["total_geometric_time_ms"], 50.725, 3)
        self.assertAlmostEqual(metrics["time_below_altitude_ms"], 2.029, 3)
        self.assertAlmostEqual(metrics["ground_half_width_per_landing_km"], 60.0)


    def test_low_angle_offsets_are_material(self) -> None:
        self.assertAlmostEqual(MODULE.horizontal_offset_km(10.0, 2.0), 286.36, 2)
        self.assertAlmostEqual(MODULE.horizontal_offset_km(10.0, 3.5), 163.50, 2)
        self.assertAlmostEqual(MODULE.horizontal_offset_km(10.0, 8.0), 71.15, 2)

    def test_published_example_does_not_land_at_aircraft_altitude(self) -> None:
        hop = self.parameters["triangular_hop"]
        altitude_km = hop["published_example_altitude_ft"] * 0.0003048
        offset = MODULE.horizontal_offset_km(
            altitude_km, hop["published_example_elevation_deg"]
        )
        self.assertGreater(offset, 19.0)
        self.assertLess(offset, 20.5)

    def test_loss_free_bistatic_benchmark(self) -> None:
        result = MODULE.bistatic_link_budget(self.parameters["bistatic_link_budget"])
        self.assertAlmostEqual(result["scattered_power_dbm"], -210.037, 3)
        self.assertAlmostEqual(result["threshold_deficit_db"], 51.037, 3)
        self.assertGreater(result["direct_to_scatter_db"], 100.0)
        self.assertLess(result["maximum_coherent_carrier_perturbation_db"], 0.001)


if __name__ == "__main__":
    unittest.main()
