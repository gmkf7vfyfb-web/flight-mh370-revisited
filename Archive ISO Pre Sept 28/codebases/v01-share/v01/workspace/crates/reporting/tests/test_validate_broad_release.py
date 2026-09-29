from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_broad_release.py"
MODULE_SPEC = importlib.util.spec_from_file_location("validate_broad_release", SCRIPT)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
validator = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = validator
MODULE_SPEC.loader.exec_module(validator)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class ReleaseFixture:
    family = "bto-bfo"
    seeds = [370023, 370024]

    def __init__(self, root: Path) -> None:
        self.root = root
        self.snapshot_mode = False
        self.config_dir = root / "config"
        self.input_dir = root / "inputs"
        self.run_dir = root / "run"
        self.report_dir = root / "report"
        for directory in (self.config_dir, self.input_dir, self.run_dir, self.report_dir):
            directory.mkdir(parents=True)
        self.binary = root / "mh370"
        self.binary.write_bytes(b"fixture broad runner\n")
        self.input_paths = {
            "satcom_observations": self.input_dir / "observations.csv",
            "satellite_ephemeris": self.input_dir / "ephemeris.csv",
            "era5": self.input_dir / "era5.bin",
            "igrf": self.input_dir / "igrf.bin",
        }
        for name, path in self.input_paths.items():
            path.write_bytes(f"{name} fixture\n".encode())
        self.config = self.config_dir / "broad-release.toml"
        self.config.write_text(self.config_text(), encoding="utf-8")
        self.summary = self.run_dir / "summary.json"
        self.manifest = self.run_dir / "run-manifest.json"
        self.report_spec = self.report_dir / "report-spec.json"
        self.report_spec.write_text('{"fixture":"broad report"}\n', encoding="utf-8")
        self.generator = self.report_dir / "generator.py"
        self.generator.write_text("# deterministic fixture generator\n", encoding="utf-8")
        self.report_audit = self.report_dir / "broad_flight_spatial_report.json"
        self.seed_summaries: dict[int, dict] = {}
        self.create_run_outputs()
        self.create_report()
        self.rebuild_manifest()

    def config_text(self, *, name: str = "MH370 repeated-manoeuvre release", seeds: list[int] | None = None) -> str:
        seeds = self.seeds if seeds is None else seeds
        return f'''schema_version = 1
name = "{name}"
seeds = {json.dumps(seeds)}

[[families]]
id = "{self.family}"
use_bfo = true

[inputs]
observations = "../inputs/observations.csv"
satellite_ephemeris = "../inputs/ephemeris.csv"
era5 = "../inputs/era5.bin"
igrf = "../inputs/igrf.bin"

[model.integration]
maximum_events_per_transition = 16

[[model.initial_modes]]
name = "heading"
mode = "constant_true_heading"
scientific_probability = 0.5

[[model.initial_modes]]
name = "track"
mode = "constant_true_track"
scientific_probability = 0.5

[[model.maneuver_families]]
name = "short-dwell"
scientific_probability = 0.5

[model.maneuver_families.process.lateral_clock]
mean_interval_s = 900.0
minimum_interval_s = 60.0
gamma_shape = 1.0

[model.maneuver_families.process.lateral_mode_weights]
constant_true_heading = 0.5
constant_true_track = 0.5

[[model.maneuver_families]]
name = "long-dwell"
scientific_probability = 0.5

[model.maneuver_families.process.lateral_clock]
mean_interval_s = 3600.0
minimum_interval_s = 60.0
gamma_shape = 1.0

[model.maneuver_families.process.lateral_mode_weights]
constant_true_heading = 0.5
constant_true_track = 0.5
'''

    @property
    def manifest_inputs(self) -> dict[str, str]:
        return {name: digest(path) for name, path in self.input_paths.items()}

    def seed_summary(self, seed: int) -> dict:
        return {
            "configured_particles": 2000,
            "effective_sample_size": 1200.0,
            "family": self.family,
            "log_evidence": -80.0,
            "mean_fuel_flow_scale": 1.0,
            "fuel_exhausted_by_checkpoint_mass": 0.4,
            "seed": seed,
        }

    def create_run_outputs(self) -> None:
        family_dir = self.run_dir / self.family
        family_dir.mkdir()
        for name in ("report.pdf", "posterior.svg", "posterior.png"):
            (family_dir / name).write_bytes(f"broad {name}\n".encode())
        for seed in self.seeds:
            seed_dir = family_dir / f"seed-{seed}"
            seed_dir.mkdir()
            summary = self.seed_summary(seed)
            self.seed_summaries[seed] = summary
            write_json(seed_dir / "summary.json", summary)
            write_json(seed_dir / "checkpoints.json", [{"observation_id": "m0011"}])
            (seed_dir / "posterior.csv").write_text(
                "particle,weight,latitude_deg,longitude_deg\n0,1,-35,92\n",
                encoding="utf-8",
            )
        suite = {
            "schema_version": 1,
            "name": "MH370 repeated-manoeuvre release",
            "status": validator.EXPECTED_RUN_STATUS,
            "model_family": validator.EXPECTED_MODEL_FAMILY,
            "families": [
                {
                    "id": self.family,
                    "independent_seed_pooling": {"pooling_semantics": "evidence_weighted_independent_posterior_mixture"},
                    "seeds": [self.seed_summaries[seed] for seed in self.seeds],
                }
            ],
        }
        write_json(self.summary, suite)
        self.rewrite_handoffs()

    def rewrite_handoffs(self) -> None:
        if self.snapshot_mode:
            return
        config_hash = digest(self.config)
        inputs = self.manifest_inputs
        for seed in self.seeds:
            run_identity = validator.expected_run_identity(config_hash, self.family, seed, inputs)
            handoff = {
                "schema_version": 2,
                "run": {
                    "model_family": validator.EXPECTED_MODEL_FAMILY,
                    "seed": seed,
                    "run_identity_sha256": run_identity,
                    "config_sha256": config_hash,
                    "input_sha256": inputs,
                },
                "checkpoint": {"checkpoint_id": "filtering-through-m0011"},
                "particles": [],
            }
            write_json(self.run_dir / self.family / f"seed-{seed}" / "posterior-handoff.json", handoff)

    def create_report(self) -> None:
        sources = []
        for seed in self.seeds:
            posterior = self.run_dir / self.family / f"seed-{seed}" / "posterior.csv"
            seed_summary = self.run_dir / self.family / f"seed-{seed}" / "summary.json"
            sources.append(
                {
                    "seed": seed,
                    "source_format": "csv",
                    "input": {
                        "logical_path": os.path.relpath(posterior, self.report_spec.parent),
                        "sha256": digest(posterior),
                        "summary": {
                            "logical_path": os.path.relpath(seed_summary, self.report_spec.parent),
                            "sha256": digest(seed_summary),
                        },
                    },
                }
            )
        for name in ("broad_flight_spatial_posterior.pdf", "broad_flight_spatial_posterior.svg"):
            (self.report_dir / name).write_bytes(f"diagnostic {name}\n".encode())
        report_outputs = {
            name: digest(self.report_dir / name)
            for name in ("broad_flight_spatial_posterior.pdf", "broad_flight_spatial_posterior.svg")
        }
        report = {
            "schema_id": validator.REPORT_SCHEMA_ID,
            "schema_version": 1,
            "title": "MH370 repeated-manoeuvre diagnostic",
            "artifact_class": "diagnostic",
            "publication_eligible": False,
            "family_pooling": "none",
            "families": [
                {
                    "id": self.family,
                    "seed_pooling": "equal numerical-replicate weight within this family",
                    "sources": sources,
                }
            ],
            "numerical_support": {
                "status": "failed",
                "publication_eligible": False,
                "failed_criteria": 1,
                "unassessed_criteria": 0,
                "criteria": [{"scope": "fixture", "criterion": "root ESS", "status": "failed"}],
            },
            "generator": str(self.generator),
            "generator_sha256": digest(self.generator),
            "specification_logical_path": str(self.report_spec),
            "specification_sha256": digest(self.report_spec),
            "outputs": report_outputs,
        }
        write_json(self.report_audit, report)

    def replace_with_snapshot_report(self) -> None:
        self.snapshot_mode = True
        self.report_spec = self.config_dir / "snapshot-report-spec.json"
        self.report_spec.write_text('{"fixture":"snapshot report"}\n', encoding="utf-8")
        self.config.write_text(
            self.config_text()
            + """
[outputs]
write_builtin_report_artifacts = false
write_posterior_csv = false
write_posterior_handoff = false
write_observation_snapshot_csvs = true
""",
            encoding="utf-8",
        )
        family_dir = self.run_dir / self.family
        for name in ("report.pdf", "posterior.svg", "posterior.png"):
            (family_dir / name).unlink(missing_ok=True)
        sources = []
        for seed in self.seeds:
            seed_dir = self.run_dir / self.family / f"seed-{seed}"
            (seed_dir / "posterior.csv").unlink(missing_ok=True)
            (seed_dir / "posterior-handoff.json").unlink(missing_ok=True)
            snapshot_dir = seed_dir / "observation-snapshots"
            snapshot_dir.mkdir(exist_ok=True)
            initial = snapshot_dir / "initial.csv"
            checkpoint = snapshot_dir / "observation-0000.csv"
            fuel_anchor = snapshot_dir / "observation-0001.csv"
            satcom = snapshot_dir / "observation-0002.csv"
            initial.write_text("fixture initialized population\n", encoding="utf-8")
            checkpoint.write_text("fixture propagation-only population\n", encoding="utf-8")
            fuel_anchor.write_text("fixture fuel-anchor population\n", encoding="utf-8")
            satcom.write_text("fixture SATCOM population\n", encoding="utf-8")
            index = {
                "schema": "mh370-broad-observation-snapshot-index",
                "schema_version": 1,
                "family": self.family,
                "seed": seed,
                "snapshots": [
                    {
                        "observation_id": "radar",
                        "observation_kind": "initial",
                        "enabled_evidence_components": [],
                        "path": initial.name,
                        "sha256": digest(initial),
                    },
                    {
                        "observation_id": "held-out-m1839",
                        "observation_kind": "checkpoint",
                        "enabled_evidence_components": [],
                        "path": checkpoint.name,
                        "sha256": digest(checkpoint),
                    },
                    {
                        "observation_id": "fuel-anchor",
                        "observation_kind": "fuel_anchor",
                        "enabled_evidence_components": [],
                        "path": fuel_anchor.name,
                        "sha256": digest(fuel_anchor),
                    },
                    {
                        "observation_id": "m0011",
                        "observation_kind": "satcom",
                        "enabled_evidence_components": ["bto", "bfo"],
                        "path": satcom.name,
                        "sha256": digest(satcom),
                    },
                ],
            }
            index_path = snapshot_dir / "index.json"
            write_json(index_path, index)
            summary_path = seed_dir / "summary.json"
            sources.append(
                {
                    "seed": seed,
                    "snapshot_index": {
                        "path": os.path.relpath(index_path, self.report_audit.parent),
                        "sha256": digest(index_path),
                    },
                    "summary": {
                        "path": os.path.relpath(summary_path, self.report_audit.parent),
                        "sha256": digest(summary_path),
                    },
                    "snapshots": [
                        {
                            "epoch_id": "m1839",
                            "observation_kind": "checkpoint",
                            "enabled_evidence_components": [],
                            "path": os.path.relpath(
                                checkpoint, self.report_audit.parent
                            ),
                            "sha256": digest(checkpoint),
                        },
                        {
                            "epoch_id": "fuel-anchor",
                            "observation_kind": "fuel_anchor",
                            "enabled_evidence_components": [],
                            "path": os.path.relpath(
                                fuel_anchor, self.report_audit.parent
                            ),
                            "sha256": digest(fuel_anchor),
                        },
                        {
                            "epoch_id": "m0011",
                            "observation_kind": "satcom",
                            "enabled_evidence_components": ["bto", "bfo"],
                            "path": os.path.relpath(satcom, self.report_audit.parent),
                            "sha256": digest(satcom),
                        },
                    ],
                }
            )
        pdf = self.report_dir / "broad_snapshot_diagnostic.pdf"
        png = self.report_dir / "broad_snapshot_diagnostic.png"
        pdf.write_bytes(b"snapshot diagnostic pdf\n")
        png.write_bytes(b"snapshot diagnostic png\n")
        report = {
            "schema_id": validator.SNAPSHOT_REPORT_SCHEMA_ID,
            "schema_version": 1,
            "title": "MH370 all-epoch repeated-manoeuvre diagnostic",
            "artifact_class": "diagnostic",
            "posterior_semantics": "filtering",
            "probability_interpretation": validator.CONDITIONAL_PROBABILITY_INTERPRETATION,
            "truth_role": "absent; no accuracy claims",
            "truth_input": None,
            "family_pooling": "none",
            "families": [
                {
                    "id": self.family,
                    "seed_pooling": "equal numerical-replicate weight within this family",
                    "scientific_family_pooling": "none",
                    "sources": sources,
                }
            ],
            "numerical_support": {
                "status": "failed",
                "publication_eligible": False,
                "watermark": "FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY",
                "criteria": [{"scope": "fixture", "criterion": "root ESS", "status": "failed"}],
            },
            "specification": {
                "path": os.path.relpath(self.report_spec, self.report_audit.parent),
                "sha256": digest(self.report_spec),
            },
            "generator": {
                "path": os.path.relpath(self.generator, self.report_audit.parent),
                "sha256": digest(self.generator),
            },
            "outputs": {
                "pdf": {"path": pdf.name, "sha256": digest(pdf)},
                "png": {"path": png.name, "sha256": digest(png)},
            },
        }
        write_json(self.report_audit, report)
        self.rebuild_manifest()

    def rebuild_manifest(self) -> None:
        self.rewrite_handoffs()
        outputs = {}
        for path in sorted(self.run_dir.rglob("*")):
            if path.is_file() and path != self.manifest:
                outputs[path.relative_to(self.run_dir).as_posix()] = digest(path)
        manifest = {
            "schema_version": 1,
            "command": validator.EXPECTED_COMMAND,
            "status": validator.EXPECTED_RUN_STATUS,
            "executable_sha256": digest(self.binary),
            "config_path": "config/broad-release.toml",
            "config_sha256": digest(self.config),
            "input_sha256": self.manifest_inputs,
            "independent_seed_pooling_by_family": {self.family: {"pooling_semantics": "fixture"}},
            "output_configuration": {
                "write_builtin_report_artifacts": not self.snapshot_mode,
                "write_posterior_csv": not self.snapshot_mode,
                "write_posterior_handoff": not self.snapshot_mode,
                "write_observation_snapshot_csvs": self.snapshot_mode,
            },
            "outputs": outputs,
        }
        write_json(self.manifest, manifest)

    def audit(self) -> dict:
        return validator.validate_release(
            self.manifest,
            self.summary,
            self.config,
            self.binary,
            self.report_audit,
        )


class BroadReleaseValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.fixture = ReleaseFixture(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def check_status(self, audit: dict, check_id: str) -> str:
        return next(item["status"] for item in audit["checks"] if item["id"] == check_id)

    def test_valid_failed_numerical_report_is_diagnostic_release_and_deterministic(self) -> None:
        first = self.fixture.audit()
        second = self.fixture.audit()
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "passed")
        self.assertTrue(first["release_eligible"])
        self.assertFalse(json.loads(self.fixture.report_audit.read_text())["publication_eligible"])

        first_path = self.fixture.root / "first-audit.json"
        second_path = self.fixture.root / "second-audit.json"
        arguments = [
            "--manifest", str(self.fixture.manifest),
            "--summary", str(self.fixture.summary),
            "--config", str(self.fixture.config),
            "--binary", str(self.fixture.binary),
            "--report-audit", str(self.fixture.report_audit),
        ]
        self.assertEqual(validator.main(arguments + ["--output", str(first_path)]), 0)
        self.assertEqual(validator.main(arguments + ["--output", str(second_path)]), 0)
        self.assertEqual(first_path.read_bytes(), second_path.read_bytes())

    def test_single_seed_is_refused(self) -> None:
        self.fixture.config.write_text(self.fixture.config_text(seeds=[370023]), encoding="utf-8")
        self.fixture.rebuild_manifest()
        audit = self.fixture.audit()
        self.assertFalse(audit["release_eligible"])
        self.assertEqual(self.check_status(audit, "config.independent_seeds"), "failed")

    def test_one_turn_and_fixed_track_release_identities_are_refused(self) -> None:
        for name in ("MH371 one-turn release", "MH370 fixed-track release"):
            with self.subTest(name=name):
                self.fixture.config.write_text(self.fixture.config_text(name=name), encoding="utf-8")
                suite = json.loads(self.fixture.summary.read_text())
                suite["name"] = name
                write_json(self.fixture.summary, suite)
                self.fixture.rebuild_manifest()
                audit = self.fixture.audit()
                self.assertEqual(
                    self.check_status(audit, "release.no_legacy_fixed_trajectory_artifacts"),
                    "failed",
                )

    def test_binary_input_and_output_hash_changes_are_refused(self) -> None:
        cases = (
            ("binary", self.fixture.binary, "manifest.executable_hash"),
            ("input", self.fixture.input_paths["era5"], "manifest.input_hash_closure"),
            (
                "output",
                self.fixture.run_dir / self.fixture.family / f"seed-{self.fixture.seeds[0]}" / "posterior.csv",
                "manifest.output_hash_closure",
            ),
        )
        for label, path, check_id in cases:
            with self.subTest(label=label):
                original = path.read_bytes()
                path.write_bytes(original + b"changed\n")
                audit = self.fixture.audit()
                self.assertEqual(self.check_status(audit, check_id), "failed")
                path.write_bytes(original)

    def test_cross_seed_report_source_is_refused(self) -> None:
        report = json.loads(self.fixture.report_audit.read_text())
        wrong = self.fixture.run_dir / self.fixture.family / f"seed-{self.fixture.seeds[1]}" / "posterior.csv"
        source = report["families"][0]["sources"][0]["input"]
        source["logical_path"] = os.path.relpath(wrong, self.fixture.report_spec.parent)
        source["sha256"] = digest(wrong)
        write_json(self.fixture.report_audit, report)
        audit = self.fixture.audit()
        self.assertEqual(
            self.check_status(audit, "report.complete_same_run_family_seed_set"),
            "failed",
        )

    def test_failed_numerical_report_cannot_claim_publication(self) -> None:
        report = json.loads(self.fixture.report_audit.read_text())
        report["artifact_class"] = "publication"
        report["publication_eligible"] = True
        report["numerical_support"]["publication_eligible"] = True
        write_json(self.fixture.report_audit, report)
        audit = self.fixture.audit()
        self.assertEqual(self.check_status(audit, "report.numerical_gate"), "failed")

    def test_all_epoch_snapshot_diagnostic_is_bound_to_manifest_outputs(self) -> None:
        self.fixture.replace_with_snapshot_report()
        audit = self.fixture.audit()
        self.assertTrue(audit["release_eligible"])
        self.assertEqual(self.check_status(audit, "report.conditional_probability_interpretation"), "passed")
        self.assertEqual(self.check_status(audit, "report.complete_same_run_family_seed_set"), "passed")

        report = json.loads(self.fixture.report_audit.read_text())
        source = report["families"][0]["sources"][0]
        source["snapshots"][0] = report["families"][0]["sources"][1]["snapshots"][0]
        write_json(self.fixture.report_audit, report)
        audit = self.fixture.audit()
        self.assertEqual(self.check_status(audit, "report.complete_same_run_family_seed_set"), "failed")

    def test_snapshot_diagnostic_requires_reported_propagation_checkpoint(self) -> None:
        self.fixture.replace_with_snapshot_report()
        report = json.loads(self.fixture.report_audit.read_text())
        del report["families"][0]["sources"][0]["snapshots"][0]
        write_json(self.fixture.report_audit, report)
        audit = self.fixture.audit()
        self.assertEqual(
            self.check_status(audit, "report.complete_same_run_family_seed_set"),
            "failed",
        )

    def test_snapshot_diagnostic_refuses_artifact_suppressed_by_config(self) -> None:
        self.fixture.replace_with_snapshot_report()
        posterior = (
            self.fixture.run_dir
            / self.fixture.family
            / f"seed-{self.fixture.seeds[0]}"
            / "posterior.csv"
        )
        posterior.write_text("unexpected suppressed output\n", encoding="utf-8")
        manifest = json.loads(self.fixture.manifest.read_text())
        logical = posterior.relative_to(self.fixture.run_dir).as_posix()
        manifest["outputs"][logical] = digest(posterior)
        write_json(self.fixture.manifest, manifest)
        audit = self.fixture.audit()
        self.assertEqual(
            self.check_status(audit, "manifest.complete_family_seed_artifacts"),
            "failed",
        )

    def test_snapshot_diagnostic_binds_manifest_output_configuration(self) -> None:
        self.fixture.replace_with_snapshot_report()
        manifest = json.loads(self.fixture.manifest.read_text())
        manifest["output_configuration"]["write_posterior_csv"] = True
        write_json(self.fixture.manifest, manifest)
        audit = self.fixture.audit()
        self.assertEqual(
            self.check_status(audit, "manifest.complete_family_seed_artifacts"),
            "failed",
        )

    def test_snapshot_diagnostic_binds_held_back_truth(self) -> None:
        self.fixture.replace_with_snapshot_report()
        truth = self.fixture.input_dir / "held-back-truth.csv"
        truth.write_text("epoch_id,lat_deg,lon_deg\nm0011,-35,92\n", encoding="utf-8")
        specification = json.loads(self.fixture.report_spec.read_text())
        specification["expected_truth_sha256"] = digest(truth)
        write_json(self.fixture.report_spec, specification)
        report = json.loads(self.fixture.report_audit.read_text())
        report["specification"]["sha256"] = digest(self.fixture.report_spec)
        report["truth_role"] = (
            "held back from inference and loaded only by reporter/scorer"
        )
        report["truth_input"] = {
            "path": os.path.relpath(truth, self.fixture.report_audit.parent),
            "sha256": digest(truth),
        }
        write_json(self.fixture.report_audit, report)
        audit = self.fixture.audit()
        self.assertEqual(self.check_status(audit, "report.truth_provenance"), "passed")

        truth.write_text("epoch_id,lat_deg,lon_deg\nm0011,-10,110\n", encoding="utf-8")
        audit = self.fixture.audit()
        self.assertEqual(self.check_status(audit, "report.truth_provenance"), "failed")

    def test_snapshot_diagnostic_semantics_and_watermark_are_fail_closed(self) -> None:
        mutations = (
            ("probability_interpretation", lambda value: value.__setitem__("probability_interpretation", "true_probability"), "report.conditional_probability_interpretation"),
            ("publication", lambda value: value["numerical_support"].__setitem__("publication_eligible", True), "report.numerical_gate"),
            ("watermark", lambda value: value["numerical_support"].__setitem__("watermark", "READY"), "report.numerical_gate"),
        )
        for label, mutate, check_id in mutations:
            with self.subTest(label=label):
                self.fixture.replace_with_snapshot_report()
                report = json.loads(self.fixture.report_audit.read_text())
                mutate(report)
                write_json(self.fixture.report_audit, report)
                audit = self.fixture.audit()
                self.assertEqual(self.check_status(audit, check_id), "failed")

    def test_unassessed_snapshot_uses_unassessed_diagnostic_watermark(self) -> None:
        self.fixture.replace_with_snapshot_report()
        report = json.loads(self.fixture.report_audit.read_text())
        report["numerical_support"]["criteria"][0]["status"] = "unassessed"
        report["numerical_support"]["status"] = "unassessed"
        report["numerical_support"]["watermark"] = (
            "UNASSESSED NUMERICAL SUPPORT — DIAGNOSTIC ONLY"
        )
        write_json(self.fixture.report_audit, report)
        audit = self.fixture.audit()
        self.assertTrue(audit["release_eligible"])
        self.assertEqual(self.check_status(audit, "report.numerical_gate"), "passed")

    def test_handoff_from_another_family_seed_run_is_refused(self) -> None:
        handoff_path = (
            self.fixture.run_dir
            / self.fixture.family
            / f"seed-{self.fixture.seeds[0]}"
            / "posterior-handoff.json"
        )
        handoff = json.loads(handoff_path.read_text())
        handoff["run"]["run_identity_sha256"] = "0" * 64
        write_json(handoff_path, handoff)
        self.fixture.rebuild_manifest()
        # rebuild_manifest rewrites handoffs; make the mismatch after hash closure.
        handoff = json.loads(handoff_path.read_text())
        handoff["run"]["run_identity_sha256"] = "0" * 64
        write_json(handoff_path, handoff)
        manifest = json.loads(self.fixture.manifest.read_text())
        logical = handoff_path.relative_to(self.fixture.run_dir).as_posix()
        manifest["outputs"][logical] = digest(handoff_path)
        write_json(self.fixture.manifest, manifest)
        audit = self.fixture.audit()
        self.assertEqual(self.check_status(audit, "outputs.handoff_run_identity"), "failed")


if __name__ == "__main__":
    unittest.main()
