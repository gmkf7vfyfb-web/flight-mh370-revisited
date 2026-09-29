#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hydro_release_workflow as release
import raw_triad_adapter as adapter
import raw_triad_search as raw_search


class HydroReleaseTests(unittest.TestCase):
    @staticmethod
    def write_triad_fixture(
        root: Path,
        station_id: str,
        longitude: float,
        samples: np.ndarray,
    ) -> Path:
        sample_path = root / f"{station_id}.csv"
        with sample_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["time_offset_s", "one", "two", "three"])
            writer.writeheader()
            for index in range(samples.size):
                writer.writerow(
                    {
                        "time_offset_s": index / 100.0,
                        "one": samples[index],
                        "two": 0.8 * samples[index],
                        "three": 1.2 * samples[index],
                    }
                )
        metadata = {
            "schema_id": adapter.SCHEMA_ID,
            "schema_version": adapter.SCHEMA_VERSION,
            "station_id": station_id,
            "station_position_wgs84": {"latitude_deg": 0.0, "longitude_deg_e": longitude},
            "start_time_utc": "2014-03-08T00:00:00Z",
            "sample_rate_hz": 100.0,
            "pressure_unit": "pascal",
            "sample_file": sample_path.name,
            "time_offset_column": "time_offset_s",
            "channels": [
                {"id": "one", "input_column": "one", "local_east_m": 0.0, "local_north_m": 0.0, "local_up_m": 0.0, "pascal_per_count": None},
                {"id": "two", "input_column": "two", "local_east_m": 1.0, "local_north_m": 0.0, "local_up_m": 0.0, "pascal_per_count": None},
                {"id": "three", "input_column": "three", "local_east_m": 0.0, "local_north_m": 1.0, "local_up_m": 0.0, "pascal_per_count": None},
            ],
            "instrument_response_id": "fixture-response",
            "timing_correction_id": "fixture-clock",
        }
        metadata_path = root / f"{station_id}.json"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        output = root / f"prepared-{station_id}"
        adapter.prepare(metadata_path, output)
        return output

    def test_scenario_bank_is_normalized_and_covers_declared_family_time_product(self) -> None:
        configuration = json.loads(release.CONFIG_PATH.read_text(encoding="utf-8"))
        scenarios = release.scenario_bank(configuration)
        expected = (
            len(configuration["impact_scenario_bank"]["impact_families"])
            * int(configuration["impact_scenario_bank"]["time_count"])
        )
        self.assertEqual(len(scenarios), expected)
        self.assertAlmostEqual(sum(row["sampling_weight"] for row in scenarios), 1.0)
        self.assertTrue(all(row["log_weight_increment"] == 0.0 for row in scenarios))
        self.assertTrue(all(not row["likelihood_evaluated"] for row in scenarios))

    def test_geometry_matches_existing_cape_leeuwin_scale(self) -> None:
        distance = float(release.haversine_km(-34.9167, 92.0472, -34.892, 114.141))
        self.assertLess(abs(distance - 2011.0), 10.0)
        bearing = release.initial_bearing_deg(-34.892, 114.141, -34.9167, 92.0472)
        self.assertTrue(250.0 < bearing < 275.0)

    def test_release_hygiene_rejects_cache_and_temporary_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "clean.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(release.rejected_artifacts(root), [])
            cache = root / "code" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "module.pyc").write_bytes(b"cache")
            (root / "result.tmp").write_bytes(b"partial")
            rejected = release.rejected_artifacts(root)
            self.assertIn("code/__pycache__", rejected)
            self.assertIn("code/__pycache__/module.pyc", rejected)
            self.assertIn("result.tmp", rejected)
            with self.assertRaises(ValueError):
                release.assert_release_tree_clean(root)

    def test_raw_adapter_calibrates_counts_and_writes_deterministic_arrays(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sample_path = root / "samples.csv"
            with sample_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["time_offset_s", "one", "two", "three"])
                writer.writeheader()
                for index in range(8):
                    writer.writerow(
                        {
                            "time_offset_s": index / 4.0,
                            "one": index,
                            "two": 2 * index,
                            "three": 3 * index,
                        }
                    )
            metadata = {
                "schema_id": adapter.SCHEMA_ID,
                "schema_version": adapter.SCHEMA_VERSION,
                "station_id": "FIXTURE",
                "station_position_wgs84": {"latitude_deg": -35.0, "longitude_deg_e": 92.0},
                "start_time_utc": "2014-03-08T00:00:00Z",
                "sample_rate_hz": 4.0,
                "pressure_unit": "instrument_counts",
                "sample_file": sample_path.name,
                "time_offset_column": "time_offset_s",
                "channels": [
                    {"id": "one", "input_column": "one", "local_east_m": 0.0, "local_north_m": 0.0, "local_up_m": 0.0, "pascal_per_count": 0.1},
                    {"id": "two", "input_column": "two", "local_east_m": 1.0, "local_north_m": 0.0, "local_up_m": 0.0, "pascal_per_count": 0.2},
                    {"id": "three", "input_column": "three", "local_east_m": 0.0, "local_north_m": 1.0, "local_up_m": 0.0, "pascal_per_count": 0.3},
                ],
                "instrument_response_id": "fixture-response",
                "timing_correction_id": "fixture-clock",
            }
            metadata_path = root / "metadata.json"
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            output = root / "prepared"
            first = adapter.prepare(metadata_path, output)
            first_hash = first["outputs"]["pressure-pa.npy"]
            second = adapter.prepare(metadata_path, output)
            self.assertEqual(first_hash, second["outputs"]["pressure-pa.npy"])
            pressure = np.load(output / "pressure-pa.npy", allow_pickle=False)
            self.assertAlmostEqual(pressure[0, 7], 0.7)
            self.assertAlmostEqual(pressure[1, 7], 2.8)
            self.assertAlmostEqual(pressure[2, 7], 6.3)

    def test_fft_response_recovers_known_station_delay(self) -> None:
        first = np.zeros(2000)
        second = np.zeros(2000)
        first[300:320] = np.hanning(20)
        second[425:445] = np.hanning(20)
        steps, response = raw_search.fft_response(first, second, 0.0, 0.0, 25.0)
        best = int(steps[np.nanargmax(response)])
        self.assertEqual(best, 125)
        self.assertAlmostEqual(best / 25.0, 5.0)

    def test_raw_complete_grid_smoke_keeps_evidence_zero_weight(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rng = np.random.default_rng(3700112)
            first_samples = rng.normal(0.0, 0.1, 4000)
            first_samples[800:900] += 2.0 * np.hanning(100)
            second_samples = np.roll(first_samples, 222)
            first = self.write_triad_fixture(root, "FIRST", 0.0, first_samples)
            second = self.write_triad_fixture(root, "SECOND", 0.03, second_samples)
            grid = root / "grid.csv"
            with grid.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["id", "alongNm", "crossNm", "latitude", "longitude"])
                writer.writeheader()
                writer.writerow({"id": "near-first", "alongNm": 0, "crossNm": 0, "latitude": 0.0, "longitude": 0.0})
                writer.writerow({"id": "midpoint", "alongNm": 5, "crossNm": 0, "latitude": 0.0, "longitude": 0.015})
            summary = raw_search.run(
                first,
                second,
                grid,
                root / "search",
                1.5,
                2.0,
                40.0,
                0.25,
                3,
                3700113,
            )
            self.assertEqual(summary["source_cell_count"], 2)
            self.assertFalse(summary["likelihood_evaluated"])
            self.assertEqual(summary["log_weight_increment"], 0.0)
            self.assertTrue((root / "search" / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
