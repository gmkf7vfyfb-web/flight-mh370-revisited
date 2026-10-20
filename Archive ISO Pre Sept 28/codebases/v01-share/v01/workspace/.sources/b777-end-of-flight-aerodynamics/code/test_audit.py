#!/usr/bin/env python3
"""Focused scientific and provenance checks for the B777 source audit."""

from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("b777_audit", HERE / "audit.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load audit.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cache = Path(
            os.environ.get("B777_AUDIT_CACHE", "/tmp/b777-end-of-flight-audit")
        )
        cls.results = audit.execute(cls.cache, offline=True, write_outputs=False)

    def test_exact_admission_is_a_plain_blocker(self) -> None:
        admission = self.results["admission"]
        self.assertEqual(admission["status"], "blocked")
        self.assertEqual(
            admission["code"],
            "NO_PUBLIC_REDISTRIBUTABLE_MODEL_SPANS_REQUIRED_ENVELOPE",
        )
        self.assertIsNone(admission["admitted_candidate_family"])
        self.assertIsNone(admission["implementation_ready_conditional_aerodynamic_parameters"])

    def test_every_download_is_hash_verified(self) -> None:
        verified = self.results["verified_sources"]
        self.assertEqual(len(verified), 9)
        for source in verified.values():
            self.assertRegex(source["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(source["bytes"], 0)

    def test_openap_identity_and_empirical_scope(self) -> None:
        result = self.results["candidate_execution"]["openap"]
        self.assertEqual(result["current_clean_polar"], {"cd0": 0.024, "k": 0.047, "oswald_e": 0.783})
        self.assertFalse(result["trent_892_is_listed_option"])
        self.assertNotIn("Trent 892", result["engine_options"])
        self.assertEqual(result["drag_estimation_dataset"]["estimation_rows"], 100)
        self.assertEqual(result["drag_estimation_dataset"]["finite_estimates"], 97)
        coverage = result["drag_estimation_dataset"]["coverage"]
        self.assertLessEqual(coverage["mach"]["max"], 0.768)
        self.assertLessEqual(coverage["alt"]["max"], 24_975)
        correlation = result["drag_estimation_dataset"]["correlation"]
        self.assertGreater(correlation["cd0"]["k"], 0.999)
        self.assertLess(correlation["cd0"]["e"], -0.99)
        runtime = self.results["candidate_execution"]["openap_runtime_probe"]
        self.assertEqual(runtime["source"]["commit"], result["commit"])
        self.assertAlmostEqual(runtime["probe"]["clean_drag_N"], 159_899.86051114558)
        unforced = [
            engine for engine in runtime["probe"]["engines"]
            if engine["engine"] == "Trent 892" and not engine["force_engine"]
        ]
        self.assertEqual(unforced[0]["status"], "rejected")

    def test_public_engine_points_are_not_a_flameout_map(self) -> None:
        engine = self.results["candidate_execution"]["trent892_certification"]
        self.assertEqual(engine["uid"], "2RR027")
        self.assertAlmostEqual(engine["rated_static_thrust_kN"], 411.48)
        self.assertEqual(
            engine["fuel_flow_kg_s"],
            {"takeoff": 3.91, "climbout": 3.1, "approach": 1, "idle": 0.3},
        )
        self.assertIn("not an altitude/Mach", engine["scope_warning"])

    def test_community_yasim_files_fail_engine_identity(self) -> None:
        models = self.results["candidate_execution"]["flightgear_yasim"]
        modern = models["modern_gpl"]
        historical = models["historical_unlicensed"]
        self.assertTrue(modern["comment_mentions"]["ge90_115b"])
        self.assertFalse(modern["comment_mentions"]["trent_892"])
        self.assertEqual({jet["thrust"] for jet in modern["active_jets"]}, {115_540.0})
        self.assertEqual({jet["thrust"] for jet in historical["active_jets"]}, {93_400.0})
        self.assertEqual(historical["license_status"], "unresolved")

    def test_official_jsbsim_has_no_b777_family(self) -> None:
        result = self.results["candidate_execution"]["official_jsbsim"]
        self.assertFalse(result["B777_model_present"])
        self.assertEqual(result["B777_path_hits"], [])
        self.assertIn("787-8", result["aircraft_directories"])
        self.assertIn("B747", result["aircraft_directories"])

    def test_boeing_export_reproduces_published_case_partition(self) -> None:
        result = self.results["candidate_execution"]["boeing_trajectory_exports"]
        self.assertEqual(result["reproduced_high_rate_cases"], [3, 4, 5, 6, 10])
        self.assertEqual(result["published_high_rate_cases"], [3, 4, 5, 6, 10])
        lower, upper = result["high_case_chord_distance_range_nm"]
        self.assertAlmostEqual(lower, 4.707313059550038)
        self.assertAlmostEqual(upper, 7.9234454758708655)
        self.assertTrue(all(
            case["last_altitude_ft"] > 0
            for case in result["one_second_case_metrics"].values()
        ))

    def test_trajectory_derivative_sample_sensitivity_is_exposed(self) -> None:
        sensitivity = self.results["candidate_execution"]["boeing_trajectory_exports"]["time_sample_sensitivity"]
        for step in ["1", "2", "4", "8"]:
            self.assertEqual(sensitivity[step]["high_rate_cases"], [3, 4, 5, 6, 10])
        self.assertEqual(sensitivity["16"]["high_rate_cases"], [3, 4, 6, 10])

    def test_parabolic_best_ld_has_independent_grid_check(self) -> None:
        for model in self.results["numerical_checks"]["polars"].values():
            coefficients = model["coefficients"]
            cd0 = coefficients["cd0"]
            k = coefficients["k"]
            analytic = model["equilibrium_cruise"]["analytic_best_lift_to_drag"]
            # Independent bounded grid, rather than calling the audit's analytic formula.
            grid = [index / 10_000 for index in range(1, 20_001)]
            numerical = max(cl / (cd0 + k * cl * cl) for cl in grid)
            self.assertLess(abs(numerical - analytic) / analytic, 1e-7)

    def test_equilibrium_and_limit_invariants(self) -> None:
        for model in self.results["numerical_checks"]["polars"].values():
            equilibrium = model["equilibrium_cruise"]
            self.assertLess(abs(equilibrium["vertical_force_residual_N"]), 1e-6)
            self.assertEqual(equilibrium["longitudinal_force_residual_N_with_required_thrust"], 0.0)
            limits = model["limiting_cases"]
            self.assertTrue(limits["drag_is_positive_for_positive_dynamic_pressure"])
            self.assertTrue(limits["low_q_induced_drag_diverges"])
            self.assertTrue(limits["no_stall_or_cl_ceiling"])
            self.assertGreater(limits["samples"][0]["implied_cl"], 100_000)

    def test_glide_energy_and_time_step_convergence(self) -> None:
        for model in self.results["numerical_checks"]["polars"].values():
            runs = model["unpowered_glide_energy_check"]
            by_step = {run["step_s"]: run for run in runs}
            self.assertLess(by_step[4.0]["relative_energy_balance_error"], 1e-8)
            self.assertLess(abs(by_step[4.0]["range_difference_from_0_125s_m"]), 0.01)
            self.assertLess(abs(by_step[4.0]["height_difference_from_0_125s_m"]), 0.01)
            self.assertLess(abs(by_step[8.0]["range_difference_from_0_125s_m"]), 0.1)
            self.assertGreater(by_step[1.0]["mechanical_energy_loss_J"], 0)

    def test_generated_html_carries_the_machine_decision(self) -> None:
        page = (audit.OUTPUT_DIR / "comparison.html").read_text(encoding="utf-8")
        self.assertIn("NO_PUBLIC_REDISTRIBUTABLE_MODEL_SPANS_REQUIRED_ENVELOPE", page)
        self.assertIn('id="audit-results"', page)
        payload = (audit.OUTPUT_DIR / "results.json").read_text(encoding="utf-8")
        self.assertIn(self.results["admission"]["code"], payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
