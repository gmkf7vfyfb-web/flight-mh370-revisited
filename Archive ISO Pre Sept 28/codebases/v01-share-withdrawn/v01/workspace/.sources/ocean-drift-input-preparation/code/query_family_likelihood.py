#!/usr/bin/env python3
"""Query one family from the ocean-drift likelihood handoff."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


EARTH_RADIUS_NM = 3_440.065


def great_circle_nm(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    radians = math.pi / 180.0
    first_latitude = latitude_a * radians
    second_latitude = latitude_b * radians
    delta_latitude = (latitude_b - latitude_a) * radians
    delta_longitude = (longitude_b - longitude_a) * radians
    haversine = math.sin(delta_latitude / 2.0) ** 2 + math.cos(
        first_latitude
    ) * math.cos(second_latitude) * math.sin(delta_longitude / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_NM * math.asin(math.sqrt(min(1.0, haversine)))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument(
        "--require-admissible",
        action="store_true",
        help="exit nonzero if the selected family is diagnostic only",
    )
    arguments = parser.parse_args()
    if not (
        math.isfinite(arguments.latitude)
        and -90.0 <= arguments.latitude <= 90.0
        and math.isfinite(arguments.longitude)
        and -360.0 <= arguments.longitude <= 360.0
    ):
        parser.error("query coordinates are not finite geographic degrees")

    handoff = json.loads(arguments.handoff.read_text(encoding="utf-8"))
    matches = [
        family for family in handoff["families"] if family["id"] == arguments.family
    ]
    if len(matches) != 1:
        parser.error(f"family is absent or ambiguous: {arguments.family}")
    family = matches[0]
    nearest = min(
        family["cells"],
        key=lambda cell: great_circle_nm(
            arguments.latitude,
            arguments.longitude,
            cell["latitude_deg"],
            cell["longitude_deg"],
        ),
    )
    distance = great_circle_nm(
        arguments.latitude,
        arguments.longitude,
        nearest["latitude_deg"],
        nearest["longitude_deg"],
    )
    maximum = handoff["query_contract"]["maximum_nearest_cell_distance_nm"]
    if distance > maximum:
        result = {
            "status": "out_of_support",
            "family_id": family["id"],
            "decision": family["decision"],
            "may_apply_to_estimator": False,
            "nearest_cell_id": nearest["id"],
            "nearest_cell_distance_nm": distance,
            "maximum_distance_nm": maximum,
            "evidence_log_likelihood": None,
            "relative_log_likelihood": None,
            "relative_likelihood": None,
        }
    else:
        result = {
            "status": "ok",
            "family_id": family["id"],
            "decision": family["decision"],
            "may_apply_to_estimator": bool(family["admitted"]),
            "nearest_cell_id": nearest["id"],
            "nearest_cell_distance_nm": distance,
            "evidence_log_likelihood": nearest["evidence_log_likelihood"],
            "relative_log_likelihood": nearest["relative_log_likelihood"],
            "relative_likelihood": nearest["relative_likelihood"],
        }
    print(json.dumps(result, indent=2))
    if arguments.require_admissible and not family["admitted"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
