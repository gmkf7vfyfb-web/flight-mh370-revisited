#!/usr/bin/env python3
"""Fast independent invariants for the Pléiades fuselage morphology bundle."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np
from PIL import Image

from morphology import radius_profile_from_polygon
from render_report import (
    grouped_pca_category_records,
    orient_pca_display_mask,
    split_wing_faces_at_waterline,
    wing_pose_surface_geometry,
)
from run_screen import (
    CANDIDATE_COUNT,
    FAMILY_ORDER,
    STRUCTURAL_INTERVALS,
    candidate_interval,
    x_from_body_station,
)
from wing_flooding import build_wing_template, solve_hydrostatic_pose


BUNDLE = Path(__file__).resolve().parent.parent
DATA = BUNDLE / "data"
OUTPUTS = BUNDLE / "outputs"
EXPECTED_SOURCE_HASHES = {
    "targets.json": "fa92cb080d33078dab1a12461f92ce969e6c2b2d3dccf5831f0ecea3181606cf",
    "size-interval-calibration.json": "23961ec3c38216acd9b292caa1d82183c48c003e092541ef318abb01169b57bb",
    "boeing-derived-fuselage-geometry.json": "708dc8fc0e56ebf83a615dd0f6393c9d763426d05ea60855449902acbb24ba1c",
    "previous-five-family-results.json": "ca7072ce1207029e652678fba07bc55f89fad443218e4a9deff64b4906a0e72e",
}
EXPECTED_DISPLAY_INPUT_HASHES = {
    "legacy-selected-pca-display-masks.json": "66c5fda8fb40c510a54bb8d369e1048b6f7759999ea2d8aa4ca292b544fbd9cf",
    "boeing-selected-component-context.json": "820061b135ed1e6fbcb176f1171c7147a9f4c641b87cc76de7dbc9e0676322be",
    "pca-only-selected-display-masks.json": "f90180806acfeaed7a2eca15edbddd66b0500fba1b993a04b1b9732cf540de3b",
}
EXPECTED_WING_FLOODING_INPUT_HASH = (
    "c5ccc0e12a2d8fc3d170e82b8663fa9cda90664c4f4ea9d69d350da34c5f68f3"
)
EXPECTED_REPORT_HASHES = {
    "aaib-british-airways-38-final-report.pdf": "2e95e1018fba4f95a3d563f6f1c5c47e29f2099e5337fb2e3ed25c6e88672868",
    "ntsb-asiana-214-final-report.pdf": "842b2947e957b64d948d6a9d38a4aac3203f11f22946906c8e807a94a9508e6f",
    "ntsb-asiana-structures-factual-report.pdf": "0da7ac8f4f6f1f88c050eb181226d17ed31da09f7b8e303516d168cd294b064e",
    "ntsb-us-airways-1549-final-report.pdf": "fe9e1733e8400f3ea9ce0832f36d934c829ac369e8a66765dc423d18973640ef",
    "malaysia-mh370-safety-investigation-report.pdf": "b39fa554b38c8e156fbb0f09567de0baf32bafaf012b0f2b80133745f3ed1f32",
    "ntsb-boeing-777-fuel-tank-addendum.pdf": "a775fff10a8606ef43ea50b5bb2d555209343677aede20bba51122f8573dbdae",
}

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FuselageMorphologyInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.targets = read_json(DATA / "targets.json")
        cls.calibration = read_json(DATA / "size-interval-calibration.json")
        cls.previous = read_json(DATA / "previous-five-family-results.json")
        cls.geometry = read_json(DATA / "boeing-derived-fuselage-geometry.json")
        cls.results = read_json(OUTPUTS / "fuselage-screen-results.json")
        cls.pca_masks = read_json(DATA / "pca-only-selected-display-masks.json")
        cls.component_context = read_json(
            DATA / "boeing-selected-component-context.json"
        )
        cls.flooding_input = read_json(
            DATA / "wing-flooding-sensitivity-input.json"
        )
        cls.flooding_results = read_json(
            OUTPUTS / "phr4-18-wing-flooding-retention-sensitivity.json"
        )
        cls.profile = radius_profile_from_polygon(
            cls.geometry["coordinates_m"]["full_fuselage_shell"]
        )
        cls.target_by_id = {
            record["object_id"]: record for record in cls.targets["objects"]
        }

    def test_pinned_inputs_and_primary_reports(self):
        for name, expected in EXPECTED_SOURCE_HASHES.items():
            self.assertEqual(sha256(DATA / name), expected, name)
        for name, expected in EXPECTED_DISPLAY_INPUT_HASHES.items():
            self.assertEqual(sha256(DATA / name), expected, name)
        for name, expected in EXPECTED_REPORT_HASHES.items():
            self.assertEqual(sha256(BUNDLE / "paper" / name), expected, name)
        self.assertEqual(
            sha256(DATA / "wing-flooding-sensitivity-input.json"),
            EXPECTED_WING_FLOODING_INPUT_HASH,
        )
        self.assertEqual(
            self.results["source_hashes_sha256"]["targets"],
            EXPECTED_SOURCE_HASHES["targets.json"],
        )
        self.assertEqual(
            self.results["source_hashes_sha256"]["size_interval_calibration"],
            EXPECTED_SOURCE_HASHES["size-interval-calibration.json"],
        )
        self.assertEqual(
            self.results["source_hashes_sha256"]["simulation_code"],
            sha256(BUNDLE / "code" / "run_screen.py"),
        )
        self.assertEqual(
            self.results["source_hashes_sha256"]["morphology_code"],
            sha256(BUNDLE / "code" / "morphology.py"),
        )
        self.assertIn("no Monte Carlo convergence claim", self.results["method"]["convergence"])
        self.assertEqual(
            self.flooding_results["source_hashes_sha256"]["sensitivity_input"],
            EXPECTED_WING_FLOODING_INPUT_HASH,
        )
        self.assertEqual(
            self.flooding_results["source_hashes_sha256"]["runner_code"],
            sha256(BUNDLE / "code" / "run_wing_flooding_sensitivity.py"),
        )
        self.assertEqual(
            self.flooding_results["source_hashes_sha256"]["hydrostatics_code"],
            sha256(BUNDLE / "code" / "wing_flooding.py"),
        )

    def test_five_retained_targets_and_source_view_areas(self):
        expected = {
            "phr-4-object-06": (888, 983),
            "phr-4-object-18": (581, 893),
            "phr-4-object-19": (612, 883),
            "phr-4-object-26": (904, 1150),
            "phr-4-object-27": (599, 921),
        }
        self.assertEqual(set(self.target_by_id), set(expected))
        for object_id, areas in expected.items():
            target = self.target_by_id[object_id]
            actual = (
                target["views"]["true_colour"]["baseline_component"]["area"],
                target["views"]["pca"]["baseline_component"]["area"],
            )
            self.assertEqual(actual, areas)

    def test_size_intervals_are_two_sided_and_correspondence_qualified(self):
        calibration_by_id = {
            record["object_id"]: record for record in self.calibration["objects"]
        }
        object_06 = calibration_by_id["phr-4-object-06"]
        self.assertEqual(object_06["summary"]["retained_trials"], 15)
        self.assertEqual(object_06["summary"]["rejected_trials"], 3)
        self.assertEqual(
            object_06["strict_intervals"],
            {
                "visible_area_m2": {"p10": 14.83, "p90": 31.68},
                "visible_length_m": {"p10": 6.38, "p90": 9.24},
                "visible_width_m": {"p10": 4.54, "p90": 6.32},
            },
        )
        retained = []
        rejected = []
        for record in self.calibration["objects"]:
            self.assertEqual(record["summary"]["total_trials"], 18)
            for trial in record["trials"]:
                destination = (
                    retained if trial["corresponds_to_baseline"] else rejected
                )
                destination.append(trial["baseline_component_iou"])
        self.assertEqual(len(rejected), 3)
        self.assertLessEqual(max(rejected), 0.003052)
        self.assertGreaterEqual(min(retained), 0.322608)
        for target in self.targets["objects"]:
            for interval in target["strict_intervals"].values():
                self.assertLess(interval["p10"], interval["p90"])

    def test_body_station_conversion_and_documented_intervals(self):
        self.assertAlmostEqual(x_from_body_station(92.5), 0.0, places=12)
        expected_lengths = {
            "section-41": 14.2875,
            "section-43": 9.6520,
            "sections-44-45": 10.1346,
            "section-46": 10.1092,
            "section-47": 8.0772,
            "section-48": 10.6680,
        }
        for index, (name, start_bs, end_bs) in enumerate(STRUCTURAL_INTERVALS):
            subtype, x0, x1 = candidate_interval(
                "documented_structural_sections", index, None, self.profile
            )
            self.assertEqual(subtype, name)
            self.assertAlmostEqual(x0, x_from_body_station(start_bs), places=10)
            self.assertAlmostEqual(x1, x_from_body_station(end_bs), places=10)
            self.assertAlmostEqual(x1 - x0, expected_lengths[name], places=4)

    def test_equal_candidate_budgets_and_inventory(self):
        with (OUTPUTS / "fuselage-candidate-inventory.csv").open(
            newline="", encoding="utf-8"
        ) as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), CANDIDATE_COUNT * len(FAMILY_ORDER))
        counts = {family: 0 for family in FAMILY_ORDER}
        subtype_counts = {}
        for row in rows:
            counts[row["family"]] += 1
            subtype_counts[row["source_subtype"]] = (
                subtype_counts.get(row["source_subtype"], 0) + 1
            )
        self.assertEqual(set(counts.values()), {CANDIDATE_COUNT})
        for name, _, _ in STRUCTURAL_INTERVALS:
            self.assertEqual(subtype_counts[name], CANDIDATE_COUNT // 6)

    def test_asiana_focused_family_is_not_in_the_reported_comparison(self):
        self.assertNotIn("asiana_aft_section_analogue", FAMILY_ORDER)
        self.assertNotIn(
            "asiana_aft_section_analogue",
            self.results["family_summary_with_previous_controls"],
        )
        self.assertEqual(len(FAMILY_ORDER), 3)

    def test_selected_pca_display_masks_are_tied_to_recorded_candidate_area(self):
        display = read_json(DATA / "legacy-selected-pca-display-masks.json")
        expected_candidates = {
            "phr-4-object-06": "fishing_net_or_rope__00292",
            "phr-4-object-18": "matched_random_geometry__00571",
            "phr-4-object-19": "matched_random_geometry__00032",
            "phr-4-object-26": "random_pose__02550",
        }
        for object_id, categories in display["objects"].items():
            for record in categories.values():
                pixel_count = int.from_bytes(
                    bytes.fromhex(record["mask_hex"]), "big"
                ).bit_count()
                self.assertEqual(
                    pixel_count, record["recovered_display_mask_pixel_count"]
                )
                self.assertEqual(pixel_count, round(record["visible_area_m2"] / 0.25))
            if object_id in expected_candidates:
                candidates = {record["candidate_id"] for record in categories.values()}
                self.assertIn(expected_candidates[object_id], candidates)
        section_47 = self.results["objects"]["phr-4-object-27"]["families"][
            "documented_structural_sections"
        ]["primary_lowest_strict_size_loss"]
        self.assertEqual(section_47["source_subtype"], "section-47")
        self.assertAlmostEqual(section_47["section_length_m"], 8.077, places=3)
    def test_pca_only_panel_uses_independently_selected_strict_minima(self):
        self.assertEqual(
            self.pca_masks["source"]["legacy_source_hashes_sha256"][
                "corrected_targets"
            ],
            EXPECTED_SOURCE_HASHES["targets.json"],
        )
        expected_candidates = {
            "phr-4-object-06": "cargo_or_plastic_cluster__00477",
            "phr-4-object-18": "random_pose__03122",
            "phr-4-object-19": "matched_random_geometry__01692",
        }
        expected_categories = {
            "phr-4-object-06": "ocean_object_controls",
            "phr-4-object-18": "wing",
            "phr-4-object-19": "matched_random_geometry",
            "phr-4-object-26": "fuselage_sections",
            "phr-4-object-27": "fuselage_sections",
        }
        dimension_keys = (
            "visible_area_m2",
            "visible_length_m",
            "visible_width_m",
        )
        for object_id in self.target_by_id:
            records = grouped_pca_category_records(
                self.results,
                self.pca_masks,
                object_id,
            )
            winner = min(
                (
                    record["pca_loss_lower_is_better"],
                    category,
                )
                for category, record in records.items()
                if record["strict_size_eligible"]
            )[1]
            self.assertEqual(winner, expected_categories[object_id])
            intervals = self.target_by_id[object_id]["strict_intervals"]
            for record in records.values():
                if not record["strict_size_eligible"]:
                    continue
                for key in dimension_keys:
                    self.assertGreaterEqual(
                        record[key], intervals[key]["p10"] - 0.001
                    )
                    self.assertLessEqual(
                        record[key], intervals[key]["p90"] + 0.001
                    )
            for record in self.pca_masks["objects"][object_id].values():
                pixel_count = int.from_bytes(
                    bytes.fromhex(record["mask_hex"]), "big"
                ).bit_count()
                self.assertEqual(
                    pixel_count, record["display_mask_pixel_count"]
                )
            if object_id in expected_candidates:
                selected = records[expected_categories[object_id]]
                self.assertEqual(
                    selected["candidate_id"],
                    expected_candidates[object_id],
                )
        object_18 = grouped_pca_category_records(
            self.results,
            self.pca_masks,
            "phr-4-object-18",
        )
        self.assertAlmostEqual(
            object_18["wing"]["pca_loss_lower_is_better"],
            0.2730,
            places=4,
        )
        self.assertLess(
            object_18["wing"]["pca_loss_lower_is_better"],
            object_18["matched_random_geometry"][
                "pca_loss_lower_is_better"
            ],
        )

    def test_phr4_18_wing_attitude_matches_record_and_marks_waterline(self):
        record = self.pca_masks["objects"]["phr-4-object-18"]["wing"]
        geometry = wing_pose_surface_geometry(
            self.component_context["components"][record["source_subtype"]],
            record["metadata"]["model_parameters"],
            record["metadata"]["pose"],
        )
        references = geometry["references"]
        self.assertEqual(geometry["plan_cell_count"], 176)
        self.assertAlmostEqual(
            references["tip"][2] - references["root"][2],
            record["metadata"]["pose"]["root_to_tip_height_difference_m"],
            places=3,
        )
        self.assertAlmostEqual(
            references["trailing"][2] - references["leading"][2],
            record["metadata"]["pose"][
                "leading_to_trailing_height_difference_m"
            ],
            places=3,
        )
        split = split_wing_faces_at_waterline(geometry["faces"])
        self.assertGreater(len(split["above"]), 0)
        self.assertGreater(len(split["below"]), 0)
        self.assertGreater(len(split["waterline"]), 20)
        self.assertLessEqual(
            max(
                abs(float(point[2]))
                for segment in split["waterline"]
                for point in segment
            ),
            1e-12,
        )

    def test_wing_flooding_hydrostatic_reference_fixture(self):
        component = {
            "id": "left-wing-complete",
            **self.component_context["components"]["left-wing-complete"],
        }
        template = build_wing_template(
            component,
            self.flooding_input["parameter_draws"][0],
            self.flooding_input,
            "absent",
        )
        self.assertEqual(len(template.plan_xy), 176)
        self.assertAlmostEqual(template.mass_kg, 13000.0, places=6)
        self.assertAlmostEqual(template.outer_volume_m3, 219.95531114, places=7)
        pose = solve_hydrostatic_pose(
            template,
            np.ones(9),
            self.flooding_input["water_density_kg_m3"],
        )
        self.assertTrue(pose["afloat"])
        self.assertEqual(pose["roll_degrees"], 0.0)
        self.assertEqual(pose["pitch_degrees"], 4.0)
        self.assertAlmostEqual(pose["heave_m"], 0.76904297, places=7)
        self.assertAlmostEqual(
            pose["root_to_tip_height_difference_m"],
            -0.8128567,
            places=6,
        )
        self.assertAlmostEqual(
            pose["leading_to_trailing_height_difference_m"],
            -0.4983082,
            places=6,
        )
        self.assertAlmostEqual(
            pose["reserve_buoyancy_kg"],
            212454.1939,
            places=3,
        )

    def test_multistart_flooding_sensitivity_requires_inboard_buoyancy(self):
        result = self.flooding_results
        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(
            result["counts"],
            {
                "original_states": 168,
                "binary_states": 3072,
                "refined_states": 24,
                "continuous_objective_evaluations": 3398,
            },
        )
        self.assertIs(
            result["target"]["independent_renderer_check"]["strict_size_eligible"],
            True,
        )
        self.assertAlmostEqual(
            result["target"]["independent_renderer_check"][
                "pca_loss_lower_is_better"
            ],
            0.27304348,
            places=8,
        )
        original = result["summaries"]["original_progressive_schedules"]
        binary = result["summaries"]["exhaustive_binary_retention"]
        refined = result["summaries"]["continuous_coordinate_refinement"]
        self.assertEqual(
            original["within_25_percent_each_slope_component_count"],
            0,
        )
        self.assertEqual(
            binary["within_25_percent_each_slope_component_count"],
            1,
        )
        self.assertEqual(
            binary["within_25_percent_and_root_above_tip_below_count"],
            0,
        )
        self.assertEqual(
            refined[
                "within_25_percent_root_above_tip_below_and_strict_size_count"
            ],
            10,
        )
        assumptions = refined["target_like_attitude_assumptions"]
        self.assertEqual(assumptions["engine_states"], ["absent"])
        self.assertEqual(assumptions["draw_indices"], [0, 1, 2])
        for span in ("midspan", "tip"):
            for chord in ("leading", "middle", "trailing"):
                self.assertEqual(
                    assumptions[
                        "retained_air_fraction_range_by_sensitivity_cell"
                    ][f"{span}-{chord}"],
                    {"minimum": 0.0, "maximum": 0.0},
                )
        self.assertEqual(
            assumptions["retained_air_fraction_range_by_sensitivity_cell"][
                "root-middle"
            ],
            {"minimum": 0.1796875, "maximum": 0.515625},
        )
        self.assertEqual(
            assumptions["modeled_retained_air_volume_m3_range"],
            [12.69320697, 71.86665793],
        )
        closest = result["selected_records"][
            "closest_refined_target_like_with_strict_size"
        ]
        self.assertEqual(closest["state_id"], "draw1__absent__start01__final")
        self.assertEqual(
            closest["retained_air_fraction"],
            [0.875, 0.25, 0.015625, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        )
        self.assertAlmostEqual(
            closest["attitude"]["reference_height_rmse_m"],
            0.79586964,
            places=8,
        )
        self.assertAlmostEqual(
            closest["image_screen"]["best_strict"]["pca_loss_lower_is_better"],
            0.34206219,
            places=8,
        )
        lowest_pca = refined["lowest_strict_pca_loss"]
        self.assertEqual(lowest_pca["state_id"], "draw2__absent__start02__final")
        self.assertAlmostEqual(
            lowest_pca["image_screen"]["best_strict"][
                "pca_loss_lower_is_better"
            ],
            0.31832797,
            places=8,
        )
        self.assertGreater(
            lowest_pca["image_screen"]["best_strict"][
                "pca_loss_lower_is_better"
            ],
            result["target"]["pinned_pca_loss"],
        )

    def test_every_reported_primary_candidate_passes_all_three_size_gates(self):
        keys = ("visible_area_m2", "visible_length_m", "visible_width_m")
        for object_id, object_result in self.results["objects"].items():
            intervals = self.target_by_id[object_id]["strict_intervals"]
            for family in FAMILY_ORDER:
                best = object_result["families"][family][
                    "primary_lowest_strict_size_loss"
                ]
                if best is None:
                    continue
                for key in keys:
                    self.assertGreaterEqual(best[key], intervals[key]["p10"] - 0.001)
                    self.assertLessEqual(best[key], intervals[key]["p90"] + 0.001)
                self.assertEqual(best["dimension_range_penalty"], 0.0)
                self.assertTrue(best["strict_size_eligible"])
            for family_result in self.previous["objects"][object_id]["families"].values():
                best = family_result["primary_best_strict_size"]
                if best is None:
                    continue
                for key in keys:
                    self.assertGreaterEqual(best[key], intervals[key]["p10"] - 0.001)
                    self.assertLessEqual(best[key], intervals[key]["p90"] + 0.001)
                self.assertTrue(best["dimensions_in_p10_p90_range"])

    def test_extended_object_level_minima(self):
        expected = {
            "phr-4-object-06": "ocean_object_combined",
            "phr-4-object-18": "matched_random_geometry",
            "phr-4-object-19": "matched_random_geometry",
            "phr-4-object-26": "wing_random_pose",
            "phr-4-object-27": "documented_structural_sections",
        }
        actual = {
            object_id: rows[0]["family"]
            for object_id, rows in self.results[
                "extended_strict_size_rankings"
            ].items()
        }
        self.assertEqual(actual, expected)
        summary = self.results["family_summary_with_previous_controls"]
        self.assertEqual(summary["whole_fuselage_shell"]["objects_at_lowest_loss"], 0)
        self.assertEqual(
            summary["documented_structural_sections"]["objects_at_lowest_loss"], 1
        )
        self.assertEqual(
            summary["matched_random_geometry"]["objects_at_lowest_loss"], 2
        )
        self.assertEqual(
            summary["ocean_object_combined"]["objects_at_lowest_loss"], 1
        )
        self.assertEqual(summary["nonwing_777_parts"]["objects_at_lowest_loss"], 0)

    def test_published_pca_reference_scales_recover_reported_area(self):
        for target in self.targets["objects"]:
            pca_view = target["views"]["pca"]
            reconstructed_area = (
                len(pca_view["relative_component_pixels"])
                * pca_view["scale_m_per_report_pixel"] ** 2
            )
            self.assertAlmostEqual(
                reconstructed_area,
                target["ga_area_m2_reported"],
                delta=0.01,
                msg=target["object_id"],
            )

    def test_visibility_sensitivity_prevents_whole_shell_overinterpretation(self):
        whole = []
        for object_result in self.results["objects"].values():
            best = object_result["families"]["whole_fuselage_shell"][
                "primary_lowest_strict_size_loss"
            ]
            if best is not None:
                whole.append(best)
        self.assertEqual(len(whole), 4)
        self.assertTrue(all(item["view_axis_cosine"] >= 0.88 for item in whole))
        self.assertTrue(all(item["achieved_visible_fraction"] <= 0.68 for item in whole))
        object_27 = self.results["objects"]["phr-4-object-27"]["families"][
            "documented_structural_sections"
        ]
        self.assertAlmostEqual(
            object_27["primary_lowest_strict_size_loss"]["loss_lower_is_better"],
            0.305757,
            places=6,
        )
        self.assertAlmostEqual(
            object_27["visibility_sensitivity"]["lowest_loss_fully_visible"][
                "loss_lower_is_better"
            ],
            0.355555,
            places=6,
        )
        random_control = next(
            row
            for row in self.results["extended_strict_size_rankings"][
                "phr-4-object-27"
            ]
            if row["family"] == "matched_random_geometry"
        )
        self.assertLess(
            random_control["primary_loss_lower_is_better"],
            object_27["visibility_sensitivity"]["lowest_loss_fully_visible"][
                "loss_lower_is_better"
            ],
        )

    def test_phr4_18_display_rotations_are_180_degrees_and_area_preserving(self):
        probe = np.zeros((7, 7), dtype=bool)
        probe[1:3, 2] = True
        expected = np.rot90(probe, 2)
        for category in ("wing", "ocean_object_controls"):
            rotated = orient_pca_display_mask(
                probe,
                "phr-4-object-18",
                category,
            )
            self.assertTrue(np.array_equal(rotated, expected))
            self.assertEqual(int(rotated.sum()), int(probe.sum()))
        for category in (
            "wing",
            "matched_random_geometry",
            "ocean_object_controls",
        ):
            unchanged = orient_pca_display_mask(
                probe,
                "phr-4-object-06",
                category,
            )
            self.assertTrue(np.array_equal(unchanged, probe))

    def test_publication_figures_are_vector_first_and_high_resolution(self):
        for stem in (
            "fuselage-common-scale-mask-panel",
            "extended-family-loss-comparison",
            "published-pca-category-minima-panel",
            "selected-777-full-and-matched-sketches",
            "phr4-18-pca-wing-attitude-waterline",
            "phr4-18-wing-flooding-sensitivity",
        ):
            pdf = (OUTPUTS / f"{stem}.pdf").read_bytes()
            svg = (OUTPUTS / f"{stem}.svg").read_text(encoding="utf-8")
            with Image.open(OUTPUTS / f"{stem}.png") as image:
                self.assertGreaterEqual(image.width, 3000)
                self.assertGreaterEqual(image.height, 1200)
            self.assertTrue(pdf.startswith(b"%PDF-1.4"))
            self.assertIn(b"/Subtype /Type0", pdf)
            self.assertIn("font-family", svg)
            self.assertIn("<text", svg)

        pca_svg = (
            OUTPUTS / "published-pca-category-minima-panel.svg"
        ).read_text(encoding="utf-8")
        self.assertNotIn("Lowest Loss", pca_svg)
        self.assertNotIn("Full Component", pca_svg)
        self.assertIn("Lowest PCA-Loss", pca_svg)
        self.assertIn("PCA Loss", pca_svg)
        self.assertNotIn("all losses use the two binary masks", pca_svg)
        self.assertIn("#b68522", pca_svg)
        sketch_svg = (
            OUTPUTS / "selected-777-full-and-matched-sketches.svg"
        ).read_text(encoding="utf-8")
        self.assertIn("Full Component Outline", sketch_svg)
        self.assertIn("Matched Visible Pose", sketch_svg)
        attitude_svg = (
            OUTPUTS / "phr4-18-pca-wing-attitude-waterline.svg"
        ).read_text(encoding="utf-8")
        self.assertIn("Complete Wing Attitude", attitude_svg)
        self.assertIn("Waterline on wing", attitude_svg)
        self.assertIn("not a hydrostatic-equilibrium prediction", attitude_svg)
        flooding_svg = (
            OUTPUTS / "phr4-18-wing-flooding-sensitivity.svg"
        ).read_text(encoding="utf-8")
        self.assertIn("First-Order Complete-Wing Flooding Sensitivity", flooding_svg)
        self.assertIn("all six midspan/tip cells fully flooded", flooding_svg)
        self.assertIn("not documented Boeing tank bays", flooding_svg)
        self.assertIn("Modeled Retained-Air Fraction", flooding_svg)


if __name__ == "__main__":
    unittest.main()
