from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1]
SCRIPT = BUNDLE / "code" / "publication_controls.py"
SPEC = importlib.util.spec_from_file_location("publication_controls", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import publication control generator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PublicationControlTests(unittest.TestCase):
    def test_flight_mapping_and_primary_statistics(self) -> None:
        MODULE.validate_frozen_inputs()
        events, summary = MODULE.gain_by_flight()
        counts = events.groupby("flight").size().to_dict()
        self.assertEqual(counts, {"MH371": 13, "early MH370": 3})
        by_flight = summary.set_index("flight")
        self.assertEqual(int(by_flight.loc["MH371", "channel_event_points"]), 57)
        self.assertEqual(int(by_flight.loc["early MH370", "channel_event_points"]), 12)
        self.assertAlmostEqual(
            by_flight.loc[
                "MH371",
                "mean_event_log_density_difference_per_point_no_minus_full",
            ],
            0.29442314881434994,
        )
        self.assertAlmostEqual(
            by_flight.loc[
                "early MH370",
                "mean_event_log_density_difference_per_point_no_minus_full",
            ],
            -0.6564278876601192,
        )

    def test_early_control_is_calibration_then_forward_holdout(self) -> None:
        raw, summary = MODULE.early_mh370_burst_summary()
        self.assertEqual(
            len(raw.loc[raw["calibration_role"].str.contains("calibration")]),
            6,
        )
        pooled = summary.loc[summary["burst"] == "pooled_1656_1707"].iloc[0]
        self.assertEqual(int(pooled["channel_event_points"]), 12)
        self.assertAlmostEqual(float(pooled["no_precomp_rmse_db"]), 1.2942570897095054)
        self.assertAlmostEqual(float(pooled["full_precomp_rmse_db"]), 1.4555786231637986)

    def test_mh371_endpoints_are_paired_and_outputs_exist(self) -> None:
        frame = MODULE.mh371_comparison()
        self.assertEqual(len(frame), 24)
        self.assertEqual(frame["seed"].nunique(), 2)
        for name in (
            "figure_4_mh371_spatial_endpoint_comparison.png",
            "figure_4_mh371_spatial_endpoint_comparison.pdf",
            "figure_5_early_mh370_forward_power_control.png",
            "figure_5_early_mh370_forward_power_control.pdf",
            "figure_6_gain_hypothesis_by_flight.png",
            "figure_6_gain_hypothesis_by_flight.pdf",
            "publication_controls_manifest.json",
        ):
            path = MODULE.OUTPUT / name
            self.assertTrue(path.is_file(), path)
            self.assertGreater(path.stat().st_size, 1000, path)


if __name__ == "__main__":
    unittest.main()
