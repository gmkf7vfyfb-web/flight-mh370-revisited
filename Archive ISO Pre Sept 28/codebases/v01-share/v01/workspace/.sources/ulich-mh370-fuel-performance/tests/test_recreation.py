#!/usr/bin/env python3
"""Focused scientific and reproducibility checks for the source recreation."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE_ROOT / "src"))

from public_performance import (  # noqa: E402
    FlightState,
    PublicPerformanceModel,
    convergence_check,
    recreate_acars,
    recreate_official_post_acars,
    recreate_stress_family,
)
from workbook_audit import audit_workbook  # noqa: E402


PRESERVED_WORKBOOK = Path(
    "/jackbox/home/.iso/thread-storage/MH370-legacy-pre-refactor-20260824/"
    "corpus/repositories/flight-mh370-revisited-e0115e817975d073bdf2b09a428fbce62aeda35c/"
    "downloads/MH370/9M-MRO Fuel Model V5.X.xlsm"
)


def load(name: str) -> dict:
    return json.loads((PACKAGE_ROOT / "data" / name).read_text(encoding="utf-8"))


class RecreationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model_document = load("model_parameters.json")
        cls.model = PublicPerformanceModel(cls.model_document)
        cls.acars = load("official_acars.json")
        cls.official = load("official_post_acars.json")
        cls.stress = load("stress_families.json")

    def test_official_anchor_and_six_fuel_values_are_exact(self) -> None:
        self.assertEqual(
            self.acars["required_anchor"],
            {
                "utc": "2014-03-07T17:06:43Z",
                "zero_fuel_weight_kg": 174369.0,
                "fuel_kg": 43800.0,
                "altitude_ft": 35004.0,
                "mach": 0.821,
                "sat_c": -43.8,
            },
        )
        self.assertEqual(
            [row["fuel_kg"] for row in self.acars["records"]],
            [49200.0, 47800.0, 46500.0, 45400.0, 44500.0, 43800.0],
        )

    def test_untuned_acars_discrepancy_is_reproduced(self) -> None:
        result = recreate_acars(self.model, self.acars)
        expected = [
            1563.867207860858,
            1256.1742032121983,
            1042.942624878131,
            867.6542159302262,
            653.6415873099395,
        ]
        for actual, target in zip(
            [row["predicted_burn_kg"] for row in result["intervals"]], expected
        ):
            self.assertAlmostEqual(actual, target, places=8)
        self.assertAlmostEqual(
            result["total_error_predicted_minus_observed_kg"], -15.720160808647051, places=8
        )
        self.assertAlmostEqual(result["interval_rmse_kg"], 83.93337656287558, places=8)
        self.assertEqual(
            [row["error_predicted_minus_observed_kg"] > 0 for row in result["intervals"]],
            [True, False, False, False, False],
        )
        self.assertEqual(self.model.p("fuel_flow_scale"), 1.0)

    def test_anchor_flow_independent_limiting_invariants(self) -> None:
        anchor = self.acars["required_anchor"]
        state = FlightState(anchor["altitude_ft"], anchor["mach"], anchor["sat_c"])
        diagnostic = self.model.flow(
            anchor["zero_fuel_weight_kg"] + anchor["fuel_kg"], state
        )
        self.assertGreater(diagnostic.total_fuel_flow_kg_s, 0.0)
        self.assertGreater(diagnostic.drag_n, 0.0)
        self.assertGreater(diagnostic.lift_coefficient, 0.0)
        self.assertGreater(diagnostic.used_thrust_fraction, 0.07)
        self.assertLess(diagnostic.used_thrust_fraction, 0.30)

    def test_arc1_overburn_is_reproduced_not_tuned(self) -> None:
        result = recreate_official_post_acars(self.model, self.acars, self.official)
        self.assertAlmostEqual(result["printed_duration_s"], 4878.0, places=8)
        self.assertAlmostEqual(result["official_arc1_offset_s"], 4882.9, places=8)
        self.assertAlmostEqual(
            result["overburn_vs_official_calculation_kg"], 4226.524014838407, places=6
        )
        self.assertAlmostEqual(result["predicted_ending_fuel_kg"], 29297.580867121596, places=6)
        self.assertEqual(self.official["epistemic_role"], "official-calculated-output-not-measurement")

    def test_midpoint_integration_converges_well_below_one_kg(self) -> None:
        runs = convergence_check(
            self.model, self.acars, self.model.p("convergence_step_sizes_s")
        )
        burns = [row["predicted_total_burn_kg"] for row in runs]
        self.assertLess(max(burns) - min(burns), 1.0)

    def test_pulau_perak_family_is_unweighted_and_ineligible(self) -> None:
        result = recreate_stress_family(self.model, self.acars, self.stress)
        self.assertEqual(result["epistemic_role"], "unweighted-stress-only")
        self.assertTrue(result["profiles"])
        for row in result["profiles"]:
            self.assertEqual(row["likelihood_weight"], 0.0)
            self.assertFalse(row["initializer_eligible"])

    def test_workbook_is_nonexecuting_hash_only_evidence(self) -> None:
        self.assertTrue(PRESERVED_WORKBOOK.is_file())
        audit = audit_workbook(PRESERVED_WORKBOOK, load("workbook_pins.json"))
        self.assertTrue(audit["audit_passed"])
        self.assertFalse(audit["audit_policy"]["macros_executed"])
        self.assertFalse(audit["audit_policy"]["formulas_recalculated"])
        self.assertFalse(audit["audit_policy"]["table_values_exported"])
        self.assertTrue(audit["rights_and_circularity"]["confidential_content_present"])
        self.assertTrue(all(row["matches_pin"] for row in audit["range_pins"]))
        self.assertTrue(all("values" not in row for row in audit["range_pins"]))

    def test_initializer_contract_is_blocked_and_forbids_circular_inputs(self) -> None:
        contract = load("initializer_contract.json")
        self.assertEqual(contract["integration_status"], "blocked")
        prohibited = " ".join(contract["prohibited_calibrations"])
        self.assertIn("18:22", prohibited)
        self.assertIn("0.45 t", prohibited)
        self.assertIn("00:17:30", prohibited)
        self.assertEqual(len(contract["blockers"]), 2)

    def test_no_binary_sources_or_toolchain_are_packaged(self) -> None:
        forbidden_suffixes = {".xlsm", ".xlsx", ".xls", ".pdf", ".pyc"}
        offending = [
            path.relative_to(PACKAGE_ROOT).as_posix()
            for path in PACKAGE_ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden_suffixes
        ]
        self.assertEqual(offending, [])
        self.assertFalse(any(path.name in {"venv", ".venv", "__pycache__"} for path in PACKAGE_ROOT.rglob("*")))


if __name__ == "__main__":
    unittest.main()
