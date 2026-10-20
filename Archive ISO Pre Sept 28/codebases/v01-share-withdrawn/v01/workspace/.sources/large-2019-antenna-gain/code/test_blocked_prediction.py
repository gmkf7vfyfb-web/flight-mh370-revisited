from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


BUNDLE = Path(__file__).resolve().parents[1]
SCRIPT = BUNDLE / "code" / "blocked_prediction.py"
SPEC = importlib.util.spec_from_file_location("antenna_gain_analysis", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import antenna gain analysis")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class HierarchicalGainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frame = MODULE.load_data()

    def test_frozen_sample_dimensions(self) -> None:
        self.assertEqual(len(self.frame), 69)
        self.assertEqual(self.frame["event"].nunique(), 16)
        self.assertEqual(self.frame["channel"].nunique(), 16)
        self.assertEqual(MODULE.sha256(MODULE.INPUT), MODULE.INPUT_SHA256)

    def test_covariance_is_symmetric_positive_definite(self) -> None:
        config = MODULE.CONFIGS[0]
        parameters = {
            "sigma_channel": 1.1,
            "sigma_time": 0.8,
            "sigma_error": 0.6,
            "time_scale_hours": 1.5,
        }
        covariance = MODULE.covariance_matrix(
            self.frame, self.frame, parameters, config
        )
        self.assertTrue(np.allclose(covariance, covariance.T))
        self.assertGreater(float(np.linalg.eigvalsh(covariance).min()), 0.0)

    def test_primary_purge_removes_nearby_events(self) -> None:
        config = MODULE.CONFIGS[0]
        event_times = self.frame.groupby("event")["event_time_hours"].first()
        for event in sorted(event_times.index):
            mask = MODULE.event_training_mask(self.frame, int(event), config)
            retained_events = self.frame.loc[mask, "event"].unique()
            separations = np.abs(
                event_times.loc[retained_events].to_numpy(float)
                - float(event_times.loc[event])
            )
            self.assertTrue(np.all(separations * 60.0 > 30.0))

    def test_independent_event_covariance_matches_definition(self) -> None:
        config = next(
            item for item in MODULE.CONFIGS if item.independent_event_process
        )
        parameters = {
            "sigma_channel": 1.1,
            "sigma_time": 0.8,
            "sigma_error": 0.6,
            "time_scale_hours": 0.0,
        }
        covariance = MODULE.covariance_matrix(
            self.frame, self.frame, parameters, config
        )
        channel = self.frame["channel"].astype(str).to_numpy()
        event = self.frame["event"].to_numpy(int)
        observation = self.frame["observation_id"].to_numpy(int)
        expected = (
            parameters["sigma_channel"] ** 2
            * (channel[:, None] == channel[None, :])
            + parameters["sigma_time"] ** 2
            * (event[:, None] == event[None, :])
            + parameters["sigma_error"] ** 2
            * (observation[:, None] == observation[None, :])
        )
        self.assertTrue(np.allclose(covariance, expected))

    def test_within_event_gain_identifiability_audit(self) -> None:
        audit = MODULE.sample_audit(self.frame)
        self.assertEqual(
            int(audit["gain_varies_within_event_gt_0_05db"].sum()),
            2,
        )

    def test_hypothesis_names_are_unambiguous(self) -> None:
        self.assertEqual(
            MODULE.MODEL_LABELS,
            {
                0.0: "full_gain_precompensation",
                1.0: "no_gain_precompensation",
            },
        )

    def test_exact_signflip_fixture(self) -> None:
        values = np.asarray([1.0, 2.0, 3.0])
        self.assertAlmostEqual(MODULE.exact_signflip_p(values), 0.25)

    def test_generated_primary_outputs(self) -> None:
        required = (
            "RESULTS.md",
            "hypothesis_comparison.csv",
            "continuous_beta_summary.csv",
            "blocked_event_scores.csv",
            "figure_1_purged_event_predictive_difference.png",
            "figure_2_continuous_beta_profile.png",
            "figure_3_model_sensitivity.png",
        )
        for name in required:
            path = MODULE.OUTPUT / name
            self.assertTrue(path.is_file(), path)
            self.assertGreater(path.stat().st_size, 100, path)

    def test_primary_comparison_is_paired(self) -> None:
        table = pd.read_csv(MODULE.OUTPUT / "hypothesis_comparison.csv")
        row = table.loc[
            table["configuration"] == MODULE.PRIMARY_CONFIG
        ].iloc[0]
        self.assertGreaterEqual(int(row["paired_events"]), 12)
        self.assertEqual(
            int(row["events_lpd_favor_no"])
            + int(row["events_lpd_favor_full"]),
            int(row["paired_events"]),
        )


if __name__ == "__main__":
    unittest.main()

