from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/broad_flight_figures.py"
MODULE_SPEC = importlib.util.spec_from_file_location("broad_flight_figures", SCRIPT)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
reporter = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = reporter
MODULE_SPEC.loader.exec_module(reporter)


def write_csv(path: Path, seed: int, count: int, concentrated: bool = False) -> None:
    fields = [
        "particle",
        "root",
        "stratum",
        "weight",
        "latitude_deg",
        "longitude_deg",
        "fuel_flow_scale",
        "dual_engine_exhaustion_time_s",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for index in range(count):
            weight = 1.0 / count
            root = 0 if concentrated else index
            writer.writerow(
                {
                    "particle": index,
                    "root": root,
                    "stratum": 0,
                    "weight": f"{weight:.17g}",
                    "latitude_deg": f"{-35.0 + (index % 11 - 5) * 0.01:.8f}",
                    "longitude_deg": f"{92.0 + (index % 13 - 6) * 0.01:.8f}",
                    "fuel_flow_scale": "1.0",
                    "dual_engine_exhaustion_time_s": "22000" if index % 2 == 0 else "",
                }
            )


def write_summary(path: Path, family: str, seed: int) -> None:
    path.write_text(
        json.dumps(
            {
                "family": family,
                "seed": seed,
                "configured_particles": 1200,
                "log_evidence": -80.0,
                "mean_fuel_flow_scale": 1.0,
                "fuel_exhausted_by_checkpoint_mass": 0.5,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def base_spec(family_sources: list[dict], artifact_class: str = "diagnostic") -> dict:
    return {
        "schema_id": reporter.SCHEMA_ID,
        "schema_version": reporter.SCHEMA_VERSION,
        "title": "Deterministic broad-flight fixture",
        "artifact_class": artifact_class,
        "artifact_epoch_utc": "2014-03-08T00:10:59Z",
        "posterior_semantics": "filtering",
        "conditioning_statement": "Filtering fixture through M0011; no later evidence.",
        "numerical_standard": "milestone",
        "spatial_grid": {
            "projection_origin_deg": [-35.0, 92.0],
            "along_axis_bearing_deg": 180.0,
            "along_bounds_km": [-100.0, 100.0],
            "cross_bounds_km": [-100.0, 100.0],
            "cell_size_km": 10.0,
            "display_bandwidth_km": 30.0,
            "kernel_truncation_sigma": 4.0,
        },
        "marginals": {
            "latitude_bounds_deg": [-36.0, -34.0],
            "latitude_bin_width_deg": 0.1,
            "along_bounds_km": [-100.0, 100.0],
            "along_bin_width_km": 10.0,
        },
        "families": [
            {
                "id": "fixture-family",
                "label": "Fixture family",
                "color": "#0072B2",
                "sources": family_sources,
            }
        ],
    }


def write_parent_and_terminal_handoffs(root: Path) -> tuple[Path, Path]:
    model_family = "broad-fixture"
    seed = 370023
    checkpoint_id = "filtering-through-m0011"
    source_epoch_id = "radar"
    conditioning = {"filtering": {"through_epoch_id": "m0011"}}
    parent_particles = []
    for index, (weight, latitude, longitude) in enumerate(
        ((0.45, -35.0, 92.0), (0.55, -36.0, 93.0))
    ):
        identity = {
            "model_family": model_family,
            "seed": seed,
            "checkpoint_id": checkpoint_id,
            "particle": index,
        }
        prior_root = {
            "model_family": model_family,
            "seed": seed,
            "source_epoch_id": source_epoch_id,
            "stratum": index,
            "initial_particle": index,
        }
        parent_particles.append(
            {
                "identity": identity,
                "prior_root": prior_root,
                "stratum": index,
                "normalized_log_weight": float(np.log(weight)),
                "powered_flight": {
                    "aircraft": {
                        "position": {
                            "latitude": latitude,
                            "longitude": longitude,
                        }
                    }
                },
                "fuel": {"dual_engine_exhaustion_time": None},
                "fuel_flow_scale": 0.99 + 0.02 * index,
            }
        )
    input_sha256 = {"fixture": "c" * 64}
    parent = {
        "schema_version": 1,
        "run": {
            "model_family": model_family,
            "seed": seed,
            "run_identity_sha256": "a" * 64,
            "config_sha256": "b" * 64,
            "input_sha256": input_sha256,
            "time_origin_utc": "2014-03-07T18:01:49Z",
            "source_epoch_id": source_epoch_id,
            "configured_particles": 2,
        },
        "checkpoint": {
            "checkpoint_id": checkpoint_id,
            "state_epoch_id": "m0011",
            "state_time": 22150.0,
            "state_time_utc": "2014-03-08T00:10:59Z",
            "conditioning": conditioning,
        },
        "evidence": {"entries": []},
        "particles": parent_particles,
    }
    parent_path = root / "parent-handoff.json"
    parent_path.write_text(
        json.dumps(parent, sort_keys=True) + "\n", encoding="utf-8"
    )
    parent_digest = hashlib.sha256(parent_path.read_bytes()).hexdigest()

    terminal_particles = []
    definitions = (
        (0, 0, 0.10, "impact"),
        (0, 1, 0.20, "no_exhaustion_by_bound"),
        (1, 0, 0.30, "impact"),
        (1, 1, 0.40, "end_of_flight_non_impact"),
    )
    for parent_index, draw_id, weight, outcome in definitions:
        parent_particle = parent_particles[parent_index]
        terminal_particles.append(
            {
                "identity": {
                    "parent": parent_particle["identity"],
                    "prior_root": parent_particle["prior_root"],
                    "stratum": parent_particle["stratum"],
                    "terminal_draw": {
                        "terminal_seed": 17,
                        "terminal_family_id": "mirror-fixture",
                        "draw_id": draw_id,
                    },
                },
                "upstream_normalized_log_weight": parent_particle[
                    "normalized_log_weight"
                ],
                "posterior_normalized_log_weight": float(np.log(weight)),
                "outcome": {"outcome": outcome},
                "impact": (
                    {
                        "position_wgs84": {
                            "latitude": -40.0 - parent_index,
                            "longitude": 95.0 + parent_index,
                        }
                    }
                    if outcome == "impact"
                    else None
                ),
            }
        )
    impact = {
        "schema_id": reporter.BROAD_IMPACT_SCHEMA_ID,
        "schema_version": 1,
        "run": {"terminal_seed": 17},
        "parent": {
            "schema_version": 1,
            "handoff_sha256": parent_digest,
            "run_identity_sha256": "a" * 64,
            "config_sha256": "b" * 64,
            "input_sha256": input_sha256,
            "model_family": model_family,
            "seed": seed,
            "checkpoint_id": checkpoint_id,
            "source_epoch_id": source_epoch_id,
            "checkpoint_time_unix_s_utc": reporter.M0011_TIME_UNIX_S_UTC,
            "conditioning": conditioning,
            "configured_particle_count": 2,
            "retained_particle_count": 2,
        },
        "terminal_family": {"id": "mirror-fixture"},
        "r600_evidence": {
            "identity": {
                "observation_id": "m0019-r600",
                "component_id": "bto",
                "channel_id": "r600",
            }
        },
        "terminal_evidence_model": {"branch": "r600_bto_only"},
        "outcome_mass": {"impact": {"posterior_normalized_mass": 0.4}},
        "particles": terminal_particles,
    }
    impact_path = root / "impact-handoff.json"
    impact_path.write_text(
        json.dumps(impact, sort_keys=True) + "\n", encoding="utf-8"
    )
    return parent_path, impact_path


class BroadFlightFigureTests(unittest.TestCase):
    def test_fixed_bandwidth_and_outside_mass_do_not_follow_tail(self) -> None:
        grid = reporter.SpatialGrid(
            origin_latitude_deg=-35.0,
            origin_longitude_deg=92.0,
            along_axis_bearing_deg=180.0,
            along_min_km=-100.0,
            along_max_km=100.0,
            cross_min_km=-100.0,
            cross_max_km=100.0,
            cell_size_km=10.0,
            bandwidth_km=30.0,
            kernel_truncation_sigma=4.0,
        )
        rendered = reporter.surface(
            np.asarray([0.0, 1000.0]),
            np.asarray([0.0, 1000.0]),
            np.asarray([0.75, 0.25]),
            grid,
        )
        self.assertEqual(rendered["bandwidth_km"], 30.0)
        self.assertAlmostEqual(rendered["raw_mass_outside_plot"], 0.25)
        self.assertAlmostEqual(rendered["raw_mass_beyond_kernel_padding"], 0.25)
        self.assertIsNone(rendered["thresholds"]["0.95"])
        self.assertIsNone(rendered["thresholds"]["0.99"])

    def test_failed_diagnostic_is_refused_then_watermarked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            particles = root / "posterior.csv"
            summary = root / "summary.json"
            write_csv(particles, 370023, 4, concentrated=True)
            summary.write_text(
                json.dumps(
                    {
                        "family": "fixture-family",
                        "seed": 370023,
                        "configured_particles": 4,
                        "log_evidence": -80.0,
                        "mean_fuel_flow_scale": 1.0,
                        "fuel_exhausted_by_checkpoint_mass": 0.5,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            specification = root / "spec.json"
            specification.write_text(
                json.dumps(
                    base_spec(
                        [
                            {
                                "seed": 370023,
                                "path": particles.name,
                                "summary": summary.name,
                            }
                        ]
                    ),
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            refused_output = root / "refused"
            with self.assertRaises(reporter.PublicationRefused):
                reporter.render(specification, refused_output)
            self.assertFalse(refused_output.exists())
            diagnostic_output = root / "diagnostic"
            audit = reporter.render(
                specification, diagnostic_output, allow_failed_diagnostic=True
            )
            self.assertFalse(audit["publication_eligible"])
            self.assertEqual(audit["numerical_support"]["status"], "failed")
            svg = (diagnostic_output / "broad_flight_spatial_posterior.svg").read_text(
                encoding="utf-8"
            )
            self.assertIn("FAILED NUMERICAL SUPPORT", svg)
            self.assertIn("FILTERING POSTERIOR", svg)

    def test_passing_report_is_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sources = []
            for seed in (370023, 370024):
                particles = root / f"posterior-{seed}.csv"
                summary = root / f"summary-{seed}.json"
                write_csv(particles, seed, 1200)
                write_summary(summary, "fixture-family", seed)
                sources.append(
                    {"seed": seed, "path": particles.name, "summary": summary.name}
                )
            specification = root / "spec.json"
            value = base_spec(sources, artifact_class="publication")
            specification.write_text(
                json.dumps(value, sort_keys=True) + "\n", encoding="utf-8"
            )
            first = root / "first"
            second = root / "second"
            first_audit = reporter.render(specification, first)
            second_audit = reporter.render(specification, second)
            self.assertTrue(first_audit["publication_eligible"])
            self.assertTrue(second_audit["publication_eligible"])
            for path in sorted(first.iterdir()):
                self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
            svg = (first / "broad_flight_spatial_posterior.svg").read_text(
                encoding="utf-8"
            )
            self.assertIn('height="662.4pt"', svg)

    def test_broad_impact_json_keeps_unconditional_impact_mass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            particles = []
            definitions = [
                (0.2, "impact", {"position_wgs84": {"latitude": -35.0, "longitude": 92.0}}),
                (0.3, "impact", {"position_wgs84": {"latitude": -36.0, "longitude": 93.0}}),
                (0.5, "no_exhaustion_by_bound", None),
            ]
            for index, (weight, outcome, impact) in enumerate(definitions):
                particles.append(
                    {
                        "identity": {
                            "parent": {
                                "model_family": "broad",
                                "seed": 370023,
                                "checkpoint_id": "filtering-through-m0011",
                                "particle": index,
                            },
                            "prior_root": {
                                "model_family": "broad",
                                "seed": 370023,
                                "source_epoch_id": "radar",
                                "stratum": 0,
                                "initial_particle": index,
                            },
                            "stratum": 0,
                        },
                        "posterior_normalized_log_weight": float(np.log(weight)),
                        "outcome": outcome,
                        "impact": impact,
                    }
                )
            handoff = {
                "schema_id": reporter.BROAD_IMPACT_SCHEMA_ID,
                "schema_version": 1,
                "run": {"terminal_seed": 17},
                "parent": {
                    "seed": 370023,
                    "conditioning": {"filtering": {"through_epoch_id": "m0011"}},
                    "configured_particle_count": 3,
                },
                "outcome_mass": {"impact": {"posterior_normalized_mass": 0.5}},
                "particles": particles,
            }
            handoff_path = root / "impact.json"
            handoff_path.write_text(
                json.dumps(handoff, sort_keys=True) + "\n", encoding="utf-8"
            )
            specification = root / "spec.json"
            specification.write_text("{}\n", encoding="utf-8")
            loaded = reporter.load_impact_json_source(
                {"seed": 370023, "path": handoff_path.name},
                specification,
                "impact-family",
                "conditional_impact",
            )
            self.assertAlmostEqual(loaded.posterior_position_mass, 0.5)
            np.testing.assert_allclose(loaded.weights, [0.4, 0.6])
            self.assertEqual(len(loaded.root_ids), 2)

    def test_parent_checkpoint_aggregates_terminal_draws_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent_path, impact_path = write_parent_and_terminal_handoffs(root)
            specification = root / "spec.json"
            specification.write_text("{}\n", encoding="utf-8")
            source = {
                "seed": 370023,
                "path": impact_path.name,
                "format": "broad_impact_json",
                "spatial_target": "parent_checkpoint",
                "parent_handoff": parent_path.name,
                "parent_semantics": "filtering",
            }
            loaded = reporter.load_parent_checkpoint_json_source(
                source, specification, "parent-family", "smoothed"
            )
            self.assertEqual(len(loaded.weights), 2)
            self.assertEqual(len(set(loaded.particle_ids)), 2)
            np.testing.assert_allclose(loaded.weights, [0.3, 0.7])
            np.testing.assert_allclose(loaded.latitude_deg, [-35.0, -36.0])
            self.assertAlmostEqual(loaded.posterior_position_mass, 1.0)
            self.assertEqual(
                loaded.source_metadata["terminal_outcome_selection"], "all_outcomes"
            )
            self.assertEqual(
                loaded.source_metadata["positive_aggregated_parent_rows"], 2
            )
            self.assertIn("all terminal outcomes", loaded.source_metadata["rendered_conditioning"])

            impact_only = dict(source)
            impact_only["terminal_outcome_selection"] = "impact_only"
            conditioned = reporter.load_parent_checkpoint_json_source(
                impact_only, specification, "parent-family", "smoothed"
            )
            np.testing.assert_allclose(conditioned.weights, [0.25, 0.75])
            self.assertAlmostEqual(conditioned.posterior_position_mass, 0.4)
            self.assertAlmostEqual(
                conditioned.source_metadata["terminal_conditioning_mass"], 0.4
            )
            self.assertIn(
                "conditional on terminal impact",
                conditioned.source_metadata["rendered_conditioning"],
            )
            with self.assertRaisesRegex(
                reporter.ReportInputError, "requires smoothed report semantics"
            ):
                reporter.load_parent_checkpoint_json_source(
                    source, specification, "parent-family", "filtering"
                )

            report_spec = base_spec([source])
            report_spec["posterior_semantics"] = "smoothed"
            report_spec["conditioning_statement"] = (
                "00:11 state weighted by declared terminal evidence; all outcomes."
            )
            specification.write_text(
                json.dumps(report_spec, sort_keys=True) + "\n", encoding="utf-8"
            )
            output = root / "parent-report"
            audit = reporter.render(
                specification, output, allow_failed_diagnostic=True
            )
            audited_source = audit["families"][0]["sources"][0]
            self.assertEqual(
                audited_source["source_metadata"]["rendered_semantics"], "smoothed"
            )
            self.assertEqual(
                audited_source["input"]["parent_handoff"]["sha256"],
                hashlib.sha256(parent_path.read_bytes()).hexdigest(),
            )
            svg = (output / "broad_flight_spatial_posterior.svg").read_text(
                encoding="utf-8"
            )
            self.assertIn("SMOOTHED / LATER-EVIDENCE-CONDITIONAL POSTERIOR", svg)

    def test_parent_checkpoint_refuses_missing_or_hash_mismatched_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent_path, impact_path = write_parent_and_terminal_handoffs(root)
            specification = root / "spec.json"
            specification.write_text("{}\n", encoding="utf-8")
            source = {
                "seed": 370023,
                "path": impact_path.name,
                "format": "broad_impact_json",
                "spatial_target": "parent_checkpoint",
                "parent_handoff": "missing-parent.json",
            }
            with self.assertRaisesRegex(
                reporter.ReportInputError, "missing parent broad handoff"
            ):
                reporter.load_parent_checkpoint_json_source(
                    source, specification, "parent-family", "smoothed"
                )

            tampered_parent = root / "tampered-parent.json"
            tampered_parent.write_text(
                parent_path.read_text(encoding="utf-8") + " ", encoding="utf-8"
            )
            source["parent_handoff"] = tampered_parent.name
            with self.assertRaisesRegex(reporter.ReportInputError, "SHA-256 mismatch"):
                reporter.load_parent_checkpoint_json_source(
                    source, specification, "parent-family", "smoothed"
                )


if __name__ == "__main__":
    unittest.main()
