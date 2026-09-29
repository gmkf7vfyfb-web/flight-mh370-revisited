import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import numpy as np


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import broad_snapshot_report as report


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BroadSnapshotReportTest(unittest.TestCase):
    def test_global_display_smoothing_wraps_longitude_but_not_latitude(self) -> None:
        surface = np.zeros((8, 8), dtype=float)
        surface[0, 0] = 1.0
        global_bounds = report.Bounds(-90.0, 90.0, -180.0, 180.0, 45.0, 1.0)
        global_display = report.smooth_display_surface(surface, global_bounds)
        self.assertGreater(global_display[0, -1], 0.0)
        self.assertEqual(global_display[-1, 0], 0.0)

        regional_bounds = report.Bounds(-90.0, 90.0, -90.0, 90.0, 22.5, 1.0)
        regional_display = report.smooth_display_surface(surface, regional_bounds)
        self.assertEqual(regional_display[0, -1], 0.0)

    def make_fixture(self, root: Path) -> tuple[Path, Path]:
        modes = [
            "constant_true_heading",
            "constant_magnetic_heading",
            "constant_true_track",
            "constant_magnetic_track",
            "great_circle_track_continuation",
        ]
        rates = [640.0, 2024.0, 6402.0, 20243.0]
        strata = []
        for rate in rates:
            for mode in modes:
                identifier = len(strata)
                clock = {
                    "mean_interval_s": rate,
                    "minimum_interval_s": 60.0,
                    "gamma_shape": 1.0,
                }
                strata.append(
                    {
                        "id": identifier,
                        "name": f"rate-{rate:g}--{mode}",
                        "initial_lateral_mode": mode,
                        "maneuver_process": {
                            "lateral_clock": clock,
                            "speed_clock": clock,
                            "altitude_clock": clock,
                            "lateral_mode_weights": {
                                "constant_true_heading": 0.2,
                                "constant_magnetic_heading": 0.2,
                                "constant_true_track": 0.2,
                                "constant_magnetic_track": 0.2,
                                "great_circle_track_continuation": 0.2,
                            },
                            "maximum_course_change_deg": 180.0,
                            "target_mach_min": 0.3,
                            "target_mach_max": 0.87,
                            "target_altitude_min_ft": 10000.0,
                            "target_altitude_max_ft": 43000.0,
                            "great_circle_leg_length_nm": 600.0,
                        },
                        "scientific_prior_probability": 0.05,
                        "allocated_particles": 1,
                    }
                )

        sources = []
        for seed, shift in ((101, 0.0), (202, 0.08)):
            directory = root / f"seed-{seed}"
            snapshots = directory / "observation-snapshots"
            snapshots.mkdir(parents=True)
            entries = []
            for index, (
                epoch,
                time_s,
                center_lat,
                center_lon,
                observation_kind,
                evidence_components,
            ) in enumerate(
                (
                    ("arc-one", 600.0, -31.0, 95.0, "checkpoint", []),
                    ("fuel-anchor", 900.0, -31.5, 95.5, "fuel_anchor", []),
                    ("arc-two", 1200.0, -32.0, 96.0, "satcom", ["bto", "bfo"]),
                )
            ):
                path = snapshots / f"observation-{index:04}.csv"
                with path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(
                        [
                            "root",
                            "stratum",
                            "weight",
                            "time_s",
                            "latitude_deg",
                            "longitude_deg",
                            "lateral_mode",
                            "lateral_events",
                            "speed_events",
                            "altitude_events",
                        ]
                    )
                    for particle in range(20):
                        writer.writerow(
                            [
                                particle,
                                particle,
                                0.05,
                                time_s,
                                center_lat + shift + 0.01 * (particle % 5),
                                center_lon + shift + 0.01 * (particle // 5),
                                modes[particle % 5],
                                2 + particle % 2,
                                1 + particle % 3,
                                1 + particle % 4,
                            ]
                        )
                entries.append(
                    {
                        "snapshot_position": index + 1,
                        "observation_index": index,
                        "observation_id": (
                            f"held-out-{epoch}"
                            if observation_kind == "checkpoint"
                            else epoch
                        ),
                        "observation_kind": observation_kind,
                        "enabled_evidence_components": evidence_components,
                        "observation_time_s": time_s,
                        "path": path.name,
                        "sha256": digest(path),
                    }
                )
            index_path = snapshots / "index.json"
            index_path.write_text(
                json.dumps(
                    {
                        "schema": report.INDEX_SCHEMA,
                        "schema_version": 1,
                        "family": "bto-bfo",
                        "seed": seed,
                        "semantics": "fixture",
                        "scientific_strata": strata,
                        "snapshots": entries,
                    }
                ),
                encoding="utf-8",
            )
            summary = directory / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "family": "bto-bfo",
                        "seed": seed,
                        "configured_particles": 20,
                        "log_evidence": -10.0,
                    }
                ),
                encoding="utf-8",
            )
            sources.append(
                {
                    "seed": seed,
                    "snapshot_index": str(index_path.relative_to(root)),
                    "summary": str(summary.relative_to(root)),
                }
            )

        spec = root / "spec.json"
        spec.write_text(
            json.dumps(
                {
                    "schema_id": report.SPEC_SCHEMA,
                    "schema_version": report.SPEC_VERSION,
                    "title": "Fixture broad-flight report",
                    "flight_label": "CONTROL",
                    "posterior_semantics": "filtering",
                    "probability_interpretation": "conditional_on_declared_model_not_calibrated_true_probability",
                    "declared_control_history_model": {
                        "repeated_events": True,
                        "initial_lateral_modes": modes,
                        "maneuver_rate_families": [f"mean-{rate:g}s" for rate in rates],
                        "probability_status": "declared_not_empirically_calibrated",
                    },
                    "map_bounds": {
                        "latitude_min_deg": -35.0,
                        "latitude_max_deg": -28.0,
                        "longitude_min_deg": 92.0,
                        "longitude_max_deg": 99.0,
                        "cell_size_deg": 0.25,
                        "smoothing_sigma_cells": 1.0,
                    },
                    "families": [
                        {
                            "id": "bto-bfo",
                            "label": "BTO + BFO",
                            "color": "#0072B2",
                            "sources": sources,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        truth = root / "truth.csv"
        with truth.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                [
                    "epoch_id",
                    "time_utc",
                    "seconds_from_t0",
                    "lat_deg",
                    "lon_deg",
                    "heading_true_deg",
                ]
            )
            writer.writerow(["arc-one", "2014-01-01T00:10:00Z", 600.0, -31.0, 95.0, 180.0])
            writer.writerow(["arc-two", "2014-01-01T00:20:00Z", 1200.0, -32.0, 96.0, 185.0])
        return spec, truth

    def test_truth_present_and_absent_paths_preserve_structural_separation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generator_copy = (
                root / "crates" / "reporting" / "scripts" / "broad_snapshot_report.py"
            )
            generator_copy.parent.mkdir(parents=True)
            shutil.copyfile(Path(report.__file__), generator_copy)
            original_module_path = report.__file__
            report.__file__ = str(generator_copy)
            self.addCleanup(setattr, report, "__file__", original_module_path)
            spec, truth = self.make_fixture(root)
            scored = root / "scored"
            self.assertEqual(
                report.main(
                    ["--spec", str(spec), "--truth", str(truth), "--output", str(scored)]
                ),
                0,
            )
            audit = json.loads((scored / "broad_snapshot_diagnostic.json").read_text())
            self.assertEqual(audit["family_pooling"], "none")
            self.assertEqual(audit["numerical_support"]["status"], "failed")
            support = audit["families"][0]["declared_structural_support"]
            self.assertEqual(len(support["initial_lateral_mode_prior_mass"]), 5)
            self.assertEqual(len(support["maneuver_rate_family_prior_mass"]), 4)
            epoch = audit["families"][0]["epochs"][0]
            self.assertEqual(epoch["epoch_id"], "arc-one")
            self.assertEqual(epoch["observation_kind"], "checkpoint")
            self.assertEqual(epoch["enabled_evidence_components"], [])
            self.assertIn("accuracy", epoch["equal_seed_pooled_metrics"])
            self.assertEqual(
                len(
                    epoch["equal_seed_pooled_metrics"][
                        "initial_lateral_mode_spatial_summaries"
                    ]
                ),
                5,
            )
            self.assertEqual(
                len(
                    epoch["equal_seed_pooled_metrics"][
                        "maneuver_rate_family_spatial_summaries"
                    ]
                ),
                4,
            )
            self.assertGreater(
                epoch["equal_seed_pooled_metrics"]["mass_with_two_or_more_lateral_events"],
                0.99,
            )
            fuel_epoch = audit["families"][0]["epochs"][1]
            self.assertEqual(fuel_epoch["epoch_id"], "fuel-anchor")
            self.assertEqual(fuel_epoch["observation_kind"], "fuel_anchor")
            self.assertEqual(fuel_epoch["enabled_evidence_components"], [])
            self.assertIsNone(fuel_epoch["truth"])
            self.assertNotIn("accuracy", fuel_epoch["equal_seed_pooled_metrics"])
            self.assertEqual(
                report.observation_condition_label(
                    report.pooled_snapshot(
                        report.load_families(spec, report.parse_spec(spec))[0],
                        "fuel-anchor",
                    )
                ),
                "fuel-state anchor/reset; no positional likelihood",
            )

            unscored = root / "unscored"
            self.assertEqual(
                report.main(["--spec", str(spec), "--output", str(unscored)]), 0
            )
            audit = json.loads((unscored / "broad_snapshot_diagnostic.json").read_text())
            self.assertEqual(audit["truth_role"], "absent; no accuracy claims")
            self.assertNotIn(
                "accuracy",
                audit["families"][0]["epochs"][0]["equal_seed_pooled_metrics"],
            )

            scored_audit_path = scored / "broad_snapshot_diagnostic.json"
            scored_audit = json.loads(scored_audit_path.read_text())

            def path_records(value: dict) -> list[dict]:
                records = [value["specification"], value["generator"], value["truth_input"]]
                records.extend(value["outputs"].values())
                for family in value["families"]:
                    for source in family["sources"]:
                        records.extend((source["snapshot_index"], source["summary"]))
                        records.extend(source["snapshots"])
                return records

            for record in path_records(scored_audit):
                self.assertFalse(Path(record["path"]).is_absolute())
                resolved = (scored_audit_path.parent / record["path"]).resolve()
                self.assertTrue(resolved.is_file())
                self.assertEqual(digest(resolved), record["sha256"])

            with tempfile.TemporaryDirectory() as relocation_temporary:
                relocated = Path(relocation_temporary) / "capsule"
                shutil.copytree(root, relocated)
                relocated_audit_path = (
                    relocated / "scored" / "broad_snapshot_diagnostic.json"
                )
                relocated_audit = json.loads(relocated_audit_path.read_text())
                for record in path_records(relocated_audit):
                    resolved = (
                        relocated_audit_path.parent / record["path"]
                    ).resolve()
                    self.assertTrue(resolved.is_file())
                    self.assertEqual(digest(resolved), record["sha256"])


if __name__ == "__main__":
    unittest.main()
