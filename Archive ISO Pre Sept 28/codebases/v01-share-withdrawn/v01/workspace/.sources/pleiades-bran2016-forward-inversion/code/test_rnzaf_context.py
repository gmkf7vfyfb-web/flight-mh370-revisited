#!/usr/bin/env python3
"""Focused invariants for the RNZAF point-metadata context renderer."""

from __future__ import annotations

import importlib.util
import unittest
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "render_rnzaf_context", ROOT / "code" / "render_rnzaf_context.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RnzafContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = MODULE.normalize_records(
            MODULE.workbook_rows(ROOT / "data" / "2017-11-26-RNZAF-Image-Data.xlsx")
        )

    def test_audited_record_counts(self) -> None:
        georeferenced = [record for record in self.records if record["latitude_deg"] is not None]
        distinct = {
            (round(record["latitude_deg"], 6), round(record["longitude_deg"], 6))
            for record in georeferenced
        }
        self.assertEqual(len(self.records), 183)
        self.assertEqual(len(georeferenced), 132)
        self.assertEqual(len(self.records) - len(georeferenced), 51)
        self.assertEqual(len(distinct), 59)
        self.assertEqual(sum(record["suffix_corrected"] for record in self.records), 6)

    def test_suffix_correction_retains_numeric_column_meaning(self) -> None:
        corrected = [record for record in self.records if record["suffix_corrected"]]
        self.assertTrue(all(record["latitude_deg"] < 0 for record in corrected))
        self.assertTrue(all(record["longitude_deg"] > 0 for record in corrected))
        self.assertTrue(all(abs(record["latitude_deg"]) < 45 for record in corrected))
        self.assertTrue(all(record["longitude_deg"] > 90 for record in corrected))

    def test_coordinate_multiplicity_is_preserved(self) -> None:
        counts = Counter(
            (round(record["latitude_deg"], 6), round(record["longitude_deg"], 6))
            for record in self.records
            if record["latitude_deg"] is not None
        )
        self.assertEqual(sum(counts.values()), 132)
        self.assertEqual(max(counts.values()), 8)
        self.assertEqual(sum(count > 1 for count in counts.values()), 27)

    def test_pleiades_hpd_thresholds_are_nested(self) -> None:
        surface = MODULE.read_pleiades(
            ROOT / "outputs" / "likelihood-handoff" / "grid.csv",
            ROOT / "outputs" / "likelihood-handoff" / "surfaces.csv",
            "equal_transport_family_model_average",
        )
        thresholds = [
            MODULE.hpd_threshold(surface["score"], surface["probability"], target)
            for target in (0.50, 0.90, 0.95, 0.99)
        ]
        self.assertGreaterEqual(thresholds[0], thresholds[1])
        self.assertGreaterEqual(thresholds[1], thresholds[2])
        self.assertGreaterEqual(thresholds[2], thresholds[3])

    def test_effective_sample_size_is_scale_invariant(self) -> None:
        self.assertAlmostEqual(MODULE.effective_sample_size(np.asarray([0.5, 0.5])), 2.0)
        self.assertAlmostEqual(MODULE.effective_sample_size(np.asarray([5.0, 5.0])), 2.0)
        with self.assertRaises(ValueError):
            MODULE.effective_sample_size(np.asarray([0.0, 0.0]))


if __name__ == "__main__":
    unittest.main()
