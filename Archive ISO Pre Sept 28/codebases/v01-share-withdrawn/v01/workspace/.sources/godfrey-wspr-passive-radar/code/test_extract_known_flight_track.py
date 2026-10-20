#!/usr/bin/env python3
"""Regression checks for the post-selection known-flight track overlay."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import tempfile
import unittest
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


CODE = Path(__file__).resolve().parent
DATA = CODE.parent / "data" / "known-flight"
sys.path.insert(0, str(CODE))

import extract_known_flight_track as extractor


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def great_circle_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    first, second = math.radians(latitude_1), math.radians(latitude_2)
    delta_latitude = second - first
    delta_longitude = math.radians(longitude_2 - longitude_1)
    value = (
        math.sin(delta_latitude / 2.0) ** 2
        + math.cos(first) * math.cos(second)
        * math.sin(delta_longitude / 2.0) ** 2
    )
    return 2.0 * 6371.0088 * math.asin(math.sqrt(max(0.0, min(1.0, value))))


class KnownFlightTrackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.track_path = DATA / "known_flight_track_observations.csv"
        self.manifest_path = DATA / "known_flight_track_provenance.json"
        with self.track_path.open(newline="", encoding="utf-8") as handle:
            self.rows = list(csv.DictReader(handle))
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def test_frozen_track_and_source_identity(self) -> None:
        self.assertEqual(len(self.rows), 77)
        self.assertEqual(
            Counter(row["flight"] for row in self.rows),
            Counter(extractor.EXPECTED_COUNTS),
        )
        self.assertEqual(self.manifest["schema"], extractor.MANIFEST_SCHEMA)
        self.assertEqual(self.manifest["track_schema"], extractor.TRACK_SCHEMA)
        source = self.manifest["source"]
        self.assertEqual(source["file"], extractor.SOURCE_FILENAME)
        self.assertEqual(source["sha256"], extractor.SOURCE_SHA256)
        self.assertEqual(source["size_bytes"], extractor.SOURCE_SIZE_BYTES)
        self.assertEqual(source["license"], "CC-BY-4.0")
        identity = hashlib.sha256(self.track_path.read_bytes()).hexdigest()
        self.assertEqual(identity, self.manifest["output"]["sha256"])
        self.assertEqual(
            identity,
            "f16beefec5a504f76270fc0bc4ce01eed8fa2a647a48911065828f6cafde3c03",
        )
        self.assertIn("Post-selection", self.manifest["role"])
        self.assertIn("not continuously observed", self.manifest["role"])

    def test_rows_are_unique_chronological_observations(self) -> None:
        by_flight: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in self.rows:
            by_flight[row["flight"]].append(row)
            self.assertEqual(row["position_source"], extractor.SOURCE_FILENAME)
            self.assertEqual(row["source_sheet"], extractor.SOURCE_SHEET)
            self.assertEqual(
                row["position_method"], "reported ACARS position sample"
            )
        for flight, rows in by_flight.items():
            self.assertEqual(
                [int(row["track_point_index"]) for row in rows],
                list(range(len(rows))),
            )
            timestamps = [parse_utc(row["time_utc"]) for row in rows]
            self.assertEqual(timestamps, sorted(set(timestamps)))
        used_source_rows = {int(row["source_excel_row"]) for row in self.rows}
        self.assertTrue(used_source_rows.isdisjoint(extractor.DUPLICATE_ROW_MAP))
        self.assertEqual(by_flight["MH371"][0]["source_excel_row"], "14")
        self.assertEqual(by_flight["MH371"][-1]["source_excel_row"], "95")
        self.assertEqual(by_flight["MH370"][0]["source_excel_row"], "105")
        self.assertEqual(by_flight["MH370"][-1]["source_excel_row"], "110")

    def test_overlay_agrees_with_separate_scoring_truth_as_documented(self) -> None:
        truth_path = DATA / "known_flight_truth_references.csv"
        with truth_path.open(newline="", encoding="utf-8") as handle:
            truths = [
                row for row in csv.DictReader(handle)
                if row["reference_role"] == "arc_epoch"
            ]
        tracks: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in self.rows:
            tracks[row["flight"]].append(row)

        differences: dict[str, float] = {}
        for truth in truths:
            epoch = truth["epoch_id"]
            flight = truth["position_source"].split()[0]
            target_time = parse_utc(truth["position_time_utc"])
            rows = tracks[flight]
            before = [row for row in rows if parse_utc(row["time_utc"]) <= target_time]
            after = [row for row in rows if parse_utc(row["time_utc"]) >= target_time]
            if before and after:
                left, right = before[-1], after[0]
                left_time, right_time = (
                    parse_utc(left["time_utc"]), parse_utc(right["time_utc"])
                )
                fraction = (
                    (target_time - left_time).total_seconds()
                    / (right_time - left_time).total_seconds()
                    if right_time != left_time else 0.0
                )
                latitude = float(left["latitude_deg"]) + fraction * (
                    float(right["latitude_deg"]) - float(left["latitude_deg"])
                )
                longitude = float(left["longitude_deg_e"]) + fraction * (
                    float(right["longitude_deg_e"])
                    - float(left["longitude_deg_e"])
                )
            else:
                nearest = min(
                    rows,
                    key=lambda row: abs(
                        (parse_utc(row["time_utc"]) - target_time).total_seconds()
                    ),
                )
                latitude = float(nearest["latitude_deg"])
                longitude = float(nearest["longitude_deg_e"])
            differences[epoch] = great_circle_km(
                latitude,
                longitude,
                float(truth["latitude_deg"]),
                float(truth["longitude_deg_e"]),
            )

        self.assertLess(max(
            value for epoch, value in differences.items()
            if epoch.startswith("mh371_")
        ), 1e-6)
        # The MH370 scorer uses a separate retained SITA source.  Its first two
        # references differ by at most 1 km from this independent ACARS overlay.
        self.assertLessEqual(differences["mh370_1642"], 1.01)
        self.assertLessEqual(differences["mh370_1656"], 0.10)
        self.assertLess(differences["mh370_1707"], 1e-6)

    def test_wrong_workbook_is_refused_before_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / extractor.SOURCE_FILENAME
            path.write_bytes(b"not the audited workbook")
            with self.assertRaisesRegex(
                extractor.TrackExtractionError, "size is"
            ):
                extractor.verify_source(path)


if __name__ == "__main__":
    unittest.main()
