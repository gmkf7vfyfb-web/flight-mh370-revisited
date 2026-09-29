#!/usr/bin/env python3
"""Build truth-separated MH371 cruise-control inputs from frozen workbooks.

Only the initial position and true heading are exposed. Later ACARS positions,
altitudes, Mach, and trajectory-derived velocities are written to the scorer-
only CSV. Channel selection is deterministic pseudo-random SHA-256 ranking.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from xml.etree import ElementTree as ET
from zipfile import ZipFile


OOXML = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RELATIONSHIPS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
AIRCRAFT_ID = 35_200_217
START_SECONDS = 1 * 3600 + 48 * 60
END_SECONDS = 7 * 3600 + 4 * 60
SELECTION_SEED = "mh371-cruise-hourly-v1"
BASE_DATE = datetime(2014, 3, 7, tzinfo=timezone.utc)
PERTH_GES_ECEF_KM = (-2368.841, 4881.080, -3342.092)
BTO_SPEED_OF_LIGHT_KM_S = 299_792.458
BTO_NOMINAL_DELAY_US = 499_962.0
BTO_R1200_CHANNEL_TERM_US = 4_283.0
SELECTION_WINDOWS = (
    ("mh371_0200", 2 * 3600, 1 * 3600 + 54 * 60, 1 * 3600 + 57 * 60),
    ("mh371_0300", 3 * 3600, 3 * 3600 + 20 * 60, 3 * 3600 + 22 * 60),
    ("mh371_0400", 4 * 3600, 3 * 3600 + 59 * 60, 4 * 3600 + 5 * 60),
    ("mh371_0500", 5 * 3600, 5 * 3600 + 10 * 60, 5 * 3600 + 12 * 60),
    ("mh371_0600", 6 * 3600, 6 * 3600 + 9 * 60, 6 * 3600 + 12 * 60),
    ("mh371_0648", 6 * 3600 + 48 * 60, 6 * 3600 + 47 * 60, 6 * 3600 + 49 * 60),
)
CORRECTION_SHEETS = (
    "0011 Updated",
    "0138 Accel and Climb",
    "0404 Updated",
    "0611 Updated 12dB Fixed",
    "0648 Updated 12dB",
    "1642 Accel and Climb",
    "1655 Cruise Climb",
    "1707 Updated 12dB",
    "1828 Updated 12dB",
    "Telephony 1 1838",
    "1941 Updated",
    "2041 Updated",
    "2141 Updated",
    "2241 Updated",
    "Telephony 2 2314",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def column_index(reference: str) -> int:
    value = 0
    for character in re.match(r"[A-Z]+", reference).group(0):
        value = value * 26 + ord(character) - ord("A") + 1
    return value - 1


class Workbook:
    def __init__(self, path: Path):
        self.path = path
        self.archive = ZipFile(path)
        self.shared_strings = []
        if "xl/sharedStrings.xml" in self.archive.namelist():
            root = ET.fromstring(self.archive.read("xl/sharedStrings.xml"))
            self.shared_strings = [
                "".join(node.text or "" for node in item.iter(OOXML + "t"))
                for item in root.findall(OOXML + "si")
            ]
        workbook = ET.fromstring(self.archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(
            self.archive.read("xl/_rels/workbook.xml.rels")
        )
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
        self.sheets = {
            item.attrib["name"]: "xl/" + targets[item.attrib[RELATIONSHIPS + "id"]]
            for item in workbook.find(OOXML + "sheets")
        }

    def close(self):
        self.archive.close()

    def _value(self, cell):
        value = cell.find(OOXML + "v")
        if value is None:
            return None
        text = value.text
        if cell.attrib.get("t") == "s":
            return self.shared_strings[int(text)]
        if cell.attrib.get("t") == "b":
            return text == "1"
        try:
            return float(text)
        except (TypeError, ValueError):
            return text

    def rows(self, sheet_name: str):
        with self.archive.open(self.sheets[sheet_name]) as stream:
            for _, row in ET.iterparse(stream, events=("end",)):
                if row.tag != OOXML + "row":
                    continue
                values = {
                    column_index(cell.attrib["r"]): self._value(cell)
                    for cell in row.findall(OOXML + "c")
                }
                source_row = int(row.attrib["r"])
                row.clear()
                yield source_row, values


def seconds_of_day(value: float) -> float:
    return (value % 1.0) * 86_400.0


def iso_time(seconds: float) -> str:
    value = BASE_DATE + timedelta(seconds=seconds)
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def circular_interpolate(first: float, second: float, fraction: float) -> float:
    difference = (second - first + 180.0) % 360.0 - 180.0
    return (first + fraction * difference) % 360.0


def read_acars(path: Path):
    workbook = Workbook(path)
    sheet = next(iter(workbook.sheets))
    output = []
    try:
        for source_row, values in workbook.rows(sheet):
            if source_row == 1 or values.get(0) is None:
                continue
            required = (0, 1, 3, 5, 6, 7, 10, 11, 12)
            if any(values.get(index) is None for index in required):
                continue
            output.append(
                {
                    "source_row": source_row,
                    "time_s": seconds_of_day(float(values[0])),
                    "altitude_ft": float(values[1]),
                    "cas_reported": float(values[2]),
                    "mach": float(values[3]),
                    "sat_c": float(values[5]),
                    "latitude_deg": float(values[6]),
                    "longitude_deg": float(values[7]),
                    "wind_from_deg": float(values[10]) % 360.0,
                    "wind_speed_kt": float(values[11]),
                    "heading_true_deg": float(values[12]) % 360.0,
                }
            )
    finally:
        workbook.close()
    if len(output) != 71:
        raise RuntimeError(f"expected 71 usable ACARS records, found {len(output)}")
    return output


def interpolate_state(states, time_s: float):
    right = next(
        (index for index, state in enumerate(states) if state["time_s"] > time_s), None
    )
    if right is None or right == 0:
        raise RuntimeError(f"time {time_s} is outside ACARS coverage")
    left = right - 1
    fraction = (time_s - states[left]["time_s"]) / (
        states[right]["time_s"] - states[left]["time_s"]
    )
    output = {}
    for name in (
        "altitude_ft",
        "cas_reported",
        "mach",
        "sat_c",
        "latitude_deg",
        "longitude_deg",
        "wind_speed_kt",
    ):
        output[name] = states[left][name] + fraction * (
            states[right][name] - states[left][name]
        )
    for name in ("wind_from_deg", "heading_true_deg"):
        output[name] = circular_interpolate(
            states[left][name], states[right][name], fraction
        )
    output["source_row_left"] = states[left]["source_row"]
    output["source_row_right"] = states[right]["source_row"]
    output["interpolation_fraction"] = fraction
    return output


def haversine_and_bearing(first, second):
    radius_nm = 3440.065
    lat1, lat2 = map(math.radians, (first[0], second[0]))
    dlat = lat2 - lat1
    dlon = math.radians(second[1] - first[1])
    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(
        dlon / 2.0
    ) ** 2
    distance = 2.0 * radius_nm * math.asin(min(1.0, math.sqrt(a)))
    east = math.sin(dlon) * math.cos(lat2)
    north = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
        lat2
    ) * math.cos(dlon)
    return distance, math.degrees(math.atan2(east, north)) % 360.0


def trajectory_velocity(states, time_s: float):
    before = interpolate_state(states, time_s - 60.0)
    after = interpolate_state(states, time_s + 60.0)
    distance, track = haversine_and_bearing(
        (before["latitude_deg"], before["longitude_deg"]),
        (after["latitude_deg"], after["longitude_deg"]),
    )
    return distance * 30.0, track


def read_sita(path: Path):
    workbook = Workbook(path)
    sheet = "All Data with Event Markers"
    rows = iter(workbook.rows(sheet))
    _, header = next(rows)
    names = {str(value): index for index, value in header.items() if value is not None}
    required = (
        "Time",
        "AES ID",
        "Channel Name",
        "SU Type",
        "C/No",
        "Frequency Offset (Hz)",
        "Burst Timing Offset (microseconds)",
    )
    if any(name not in names for name in required):
        raise RuntimeError("SITA workbook lacks required fields")
    output = []
    try:
        for source_row, values in rows:
            raw_time = values.get(names["Time"])
            channel = str(values.get(names["Channel Name"]) or "")
            su_type = str(values.get(names["SU Type"]) or "")
            if not isinstance(raw_time, float):
                continue
            if int(values.get(names["AES ID"]) or -1) != AIRCRAFT_ID:
                continue
            if not channel.startswith("IOR-R1200-"):
                continue
            if any(term in su_type for term in ("Log-on", "Log-off", "Log Control")):
                continue
            bto = values.get(names["Burst Timing Offset (microseconds)"])
            bfo = values.get(names["Frequency Offset (Hz)"])
            cno = values.get(names["C/No"])
            if bto is None or bfo is None or cno is None or float(cno) < 35.0:
                continue
            output.append(
                {
                    "source_row": source_row,
                    "time_s": seconds_of_day(raw_time),
                    "channel": channel,
                    "su_type": su_type,
                    "cno_db_hz": float(cno),
                    "bto_us": float(bto),
                    "bfo_hz": float(bfo),
                }
            )
    finally:
        workbook.close()
    return output


def select_observations(rows):
    selected = []
    audit = []
    for epoch_id, target_s, start_s, end_s in SELECTION_WINDOWS:
        candidates = [row for row in rows if start_s <= row["time_s"] <= end_s]
        if not candidates:
            raise RuntimeError(f"{epoch_id} has no eligible candidate rows")
        ranked = []
        for row in candidates:
            key = (
                f"{SELECTION_SEED}|{epoch_id}|{row['source_row']}|{row['channel']}"
            ).encode("utf-8")
            ranked.append((hashlib.sha256(key).hexdigest(), row))
        rank, chosen = min(ranked, key=lambda item: item[0])
        selected.append((epoch_id, target_s, chosen, candidates, rank))
        for candidate_rank, candidate in sorted(ranked):
            audit.append(
                {
                    "epoch_id": epoch_id,
                    "target_time_utc": iso_time(target_s),
                    "candidate_source_row": candidate["source_row"],
                    "candidate_time_utc": iso_time(candidate["time_s"]),
                    "channel": candidate["channel"],
                    "bto_us": candidate["bto_us"],
                    "bfo_hz": candidate["bfo_hz"],
                    "cno_db_hz": candidate["cno_db_hz"],
                    "sha256_rank": candidate_rank,
                    "selected": candidate is chosen,
                }
            )
    return selected, audit


def read_ephemeris(path: Path, query_times):
    workbook = Workbook(path)
    sheet = next(iter(workbook.sheets))
    needed = {
        value
        for query in query_times
        for value in (math.floor(query), math.ceil(query))
    }
    found = {}
    try:
        for _, values in workbook.rows(sheet):
            second = values.get(1)
            if not isinstance(second, float) or int(second) not in needed:
                continue
            found[int(second)] = tuple(float(values[index]) for index in range(2, 8))
            if found.keys() >= needed:
                break
    finally:
        workbook.close()
    if found.keys() < needed:
        raise RuntimeError(f"ephemeris lacks seconds {sorted(needed - found.keys())}")

    def interpolate(time_s):
        left, right = math.floor(time_s), math.ceil(time_s)
        if left == right:
            return found[left]
        fraction = time_s - left
        return tuple(
            found[left][index] + fraction * (found[right][index] - found[left][index])
            for index in range(6)
        )

    return {time_s: interpolate(time_s) for time_s in query_times}


def correction_knots(path: Path):
    workbook = Workbook(path)
    knots = {}
    try:
        for sheet in CORRECTION_SHEETS:
            if sheet not in workbook.sheets:
                raise RuntimeError(f"correction workbook lacks sheet {sheet}")
            found = None
            for _, values in workbook.rows(sheet):
                seconds = values.get(column_index("AD"))
                sat = values.get(column_index("FA"))
                afc = values.get(column_index("FB"))
                if all(isinstance(value, float) for value in (seconds, sat, afc)):
                    found = (seconds % 86_400.0, sat, afc)
                    break
            if found is None:
                raise RuntimeError(f"correction sheet {sheet} has no cached correction row")
            seconds, sat, afc = found
            knots.setdefault(round(seconds, 6), (sat, afc, sheet))
    finally:
        workbook.close()
    return [
        {"time_s": time_s, "sat_curve_hz": values[0], "afc_hz": values[1], "sheet": values[2]}
        for time_s, values in sorted(knots.items())
    ]


def interpolate_correction(knots, time_s):
    extended = [dict(item) for item in knots]
    extended += [dict(item, time_s=item["time_s"] + 86_400.0) for item in knots]
    query = time_s
    if query < extended[0]["time_s"]:
        query += 86_400.0
    right = next(index for index, item in enumerate(extended) if item["time_s"] >= query)
    if right == 0:
        raise RuntimeError("correction interpolation cannot bracket time")
    left = right - 1
    fraction = (query - extended[left]["time_s"]) / (
        extended[right]["time_s"] - extended[left]["time_s"]
    )
    sat_curve = extended[left]["sat_curve_hz"] + fraction * (
        extended[right]["sat_curve_hz"] - extended[left]["sat_curve_hz"]
    )
    afc = extended[left]["afc_hz"] + fraction * (
        extended[right]["afc_hz"] - extended[left]["afc_hz"]
    )
    return {
        "satellite_oscillator_hz": -sat_curve,
        "perth_ges_afc_hz": afc,
        "combined_satellite_ges_hz": afc - sat_curve,
        "left_knot_time_s": extended[left]["time_s"] % 86_400.0,
        "right_knot_time_s": extended[right]["time_s"] % 86_400.0,
        "interpolation_fraction": fraction,
    }


def lla_to_ecef(latitude_deg, longitude_deg, altitude_km):
    semimajor = 6378.137
    eccentricity_squared = 6.69437999014e-3
    latitude = math.radians(latitude_deg)
    longitude = math.radians(longitude_deg)
    prime_vertical = semimajor / math.sqrt(
        1.0 - eccentricity_squared * math.sin(latitude) ** 2
    )
    return (
        (prime_vertical + altitude_km) * math.cos(latitude) * math.cos(longitude),
        (prime_vertical + altitude_km) * math.cos(latitude) * math.sin(longitude),
        (prime_vertical * (1.0 - eccentricity_squared) + altitude_km)
        * math.sin(latitude),
    )


def norm(vector):
    return math.sqrt(sum(value * value for value in vector))


def bto_prediction(state, satellite):
    aircraft = lla_to_ecef(
        state["latitude_deg"], state["longitude_deg"], state["altitude_ft"] * 0.0003048
    )
    aircraft_range = norm(tuple(satellite[index] - aircraft[index] for index in range(3)))
    ground_range = norm(
        tuple(satellite[index] - PERTH_GES_ECEF_KM[index] for index in range(3))
    )
    propagation_us = (
        2.0
        * (aircraft_range + ground_range)
        / BTO_SPEED_OF_LIGHT_KM_S
        * 1.0e6
    )
    return propagation_us - BTO_NOMINAL_DELAY_US + BTO_R1200_CHANNEL_TERM_US


def write_outputs(args):
    states = read_acars(args.acars)
    sita_rows = read_sita(args.sita)
    selected, selection_audit = select_observations(sita_rows)
    times = [item[2]["time_s"] for item in selected]
    ephemeris = read_ephemeris(args.ephemeris, times)
    knots = correction_knots(args.corrections)
    initial = interpolate_state(states, START_SECONDS)

    observations = []
    truth_rows = []
    initial_speed, initial_track = trajectory_velocity(states, START_SECONDS)
    truth_rows.append(
        {
            "checkpoint_index": 0,
            "epoch_id": "t0_exposed",
            "time_utc": iso_time(START_SECONDS),
            "seconds_from_t0": 0.0,
            "observed_bto_us": "",
            "truth_predicted_bto_us": "",
            "truth_state_bto_residual_us": "",
            "observed_bfo_hz": "",
            "altitude_ft": initial["altitude_ft"],
            "mach": initial["mach"],
            "lat_deg": initial["latitude_deg"],
            "lon_deg": initial["longitude_deg"],
            "heading_true_deg": initial["heading_true_deg"],
            "ground_speed_kt": initial_speed,
            "ground_track_deg": initial_track,
            "acars_source_row_left": initial["source_row_left"],
            "acars_source_row_right": initial["source_row_right"],
            "interpolation_fraction": initial["interpolation_fraction"],
        }
    )

    for checkpoint, (epoch_id, target_s, chosen, candidates, rank) in enumerate(
        selected, start=1
    ):
        time_s = chosen["time_s"]
        state = interpolate_state(states, time_s)
        speed, track = trajectory_velocity(states, time_s)
        satellite = ephemeris[time_s]
        correction = interpolate_correction(knots, time_s)
        prediction = bto_prediction(state, satellite[:3])
        observations.append(
            {
                "epoch_id": epoch_id,
                "target_time_utc": iso_time(target_s),
                "time_utc": iso_time(time_s),
                "seconds_from_t0": time_s - START_SECONDS,
                "bto_us": chosen["bto_us"],
                "bto_sd_us": 29.0,
                "bfo_hz": chosen["bfo_hz"],
                **correction,
                "sat_position": list(satellite[:3]),
                "sat_velocity": list(satellite[3:]),
                "channel": chosen["channel"],
                "sita_source_row": chosen["source_row"],
                "selection_candidate_count": len(candidates),
                "selection_sha256_rank": rank,
                "cno_db_hz": chosen["cno_db_hz"],
            }
        )
        truth_rows.append(
            {
                "checkpoint_index": checkpoint,
                "epoch_id": epoch_id,
                "time_utc": iso_time(time_s),
                "seconds_from_t0": time_s - START_SECONDS,
                "observed_bto_us": chosen["bto_us"],
                "truth_predicted_bto_us": prediction,
                "truth_state_bto_residual_us": chosen["bto_us"] - prediction,
                "observed_bfo_hz": chosen["bfo_hz"],
                "altitude_ft": state["altitude_ft"],
                "mach": state["mach"],
                "lat_deg": state["latitude_deg"],
                "lon_deg": state["longitude_deg"],
                "heading_true_deg": state["heading_true_deg"],
                "ground_speed_kt": speed,
                "ground_track_deg": track,
                "acars_source_row_left": state["source_row_left"],
                "acars_source_row_right": state["source_row_right"],
                "interpolation_fraction": state["interpolation_fraction"],
            }
        )

    source_hashes = {
        "sita_sha256": sha256(args.sita),
        "acars_sha256": sha256(args.acars),
        "ephemeris_sha256": sha256(args.ephemeris),
        "correction_workbook_sha256": sha256(args.corrections),
    }
    package = {
        "schema_version": "mh371-known-flight-package-v2",
        "source_id": "mh371-cruise-control",
        "status": "truth_separated_cruise_bto_bfo_control",
        "time_origin_utc": iso_time(START_SECONDS),
        "time_origin_unix_s": int(BASE_DATE.timestamp()) + START_SECONDS,
        "cruise_boundary": {
            "start_utc": iso_time(START_SECONDS),
            "end_utc": iso_time(END_SECONDS),
            "start_definition": "first stable level-off",
            "end_definition": "last ACARS cruise sample before descent",
        },
        "initial_state": {
            "lat_deg": initial["latitude_deg"],
            "lon_deg": initial["longitude_deg"],
            "heading_true_deg": initial["heading_true_deg"],
        },
        "initial_position_prior": {
            "north_sd_nm": 0.5,
            "east_sd_nm": 0.5,
            "heading_sd_deg": 1.0,
            "source": "Davey et al. 2016, Chapter 4, pp. 34-35",
        },
        "observations": observations,
        "channel_selection": {
            "method": "minimum SHA-256 rank over predeclared eligible rows",
            "seed": SELECTION_SEED,
            "aircraft_id": AIRCRAFT_ID,
            "eligible_channel_prefix": "IOR-R1200-",
            "minimum_cno_db_hz": 35.0,
            "excluded_su_types": ["log-on", "log-off", "log control"],
        },
        "bfo_correction": {
            "sign_convention": "combined_satellite_ges_hz = perth_ges_afc_hz + satellite_oscillator_hz; satellite_oscillator_hz is negative of workbook FA",
            "latent_aircraft_bias_excluded": True,
            "workbook_columns": {"FA": "satellite curve", "FB": "Perth GES AFC"},
        },
        "speed_unit_audit": {
            "consumed_ground_speed_field": False,
            "acars_field_present": "CAS",
            "trajectory_velocity_source": "geodesic derivative of held-back ACARS positions",
            "reason": "the input workbook has no labelled ground-speed field, so no knot versus km/h assumption enters inference",
        },
        "source_hashes": source_hashes,
    }

    args.inference.parent.mkdir(parents=True, exist_ok=True)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.inference.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    truth_fields = list(truth_rows[0])
    with args.truth.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=truth_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(truth_rows)
    with args.audit.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(selection_audit[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(selection_audit)
    args.knots.write_text(json.dumps(knots, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "inference": str(args.inference),
                "inference_sha256": sha256(args.inference),
                "truth": str(args.truth),
                "truth_sha256": sha256(args.truth),
                "selection_audit": str(args.audit),
                "correction_knots": str(args.knots),
                "selected": [
                    {
                        "epoch_id": item["epoch_id"],
                        "time_utc": item["time_utc"],
                        "channel": item["channel"],
                        "source_row": item["sita_source_row"],
                        "bto_us": item["bto_us"],
                        "bfo_hz": item["bfo_hz"],
                        "satellite_oscillator_hz": item["satellite_oscillator_hz"],
                        "perth_ges_afc_hz": item["perth_ges_afc_hz"],
                    }
                    for item in observations
                ],
                "source_hashes": source_hashes,
            },
            indent=2,
        )
    )


def parse_args():
    repository = Path(__file__).resolve().parents[3]
    archive = Path(
        "/jackbox/home/.iso/thread-storage/MH370-legacy-pre-refactor-20260824"
    )
    imported = archive / (
        "corpus/repositories/flight-mh370-revisited-"
        "e0115e817975d073bdf2b09a428fbce62aeda35c/library_full_audit/MH370"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sita", type=Path, default=imported / "SITA data with CNo BTO BFO rx dBm 1 Oxford.xlsx"
    )
    parser.add_argument("--acars", type=Path, default=imported / "mh371-acars.xlsx")
    parser.add_argument(
        "--ephemeris", type=Path, default=imported / "Inmarsat3F1_23839 Fixed Position Velocity.xlsx"
    )
    parser.add_argument(
        "--corrections",
        type=Path,
        default=archive
        / "corpus/datasets/mh370-dissertation-spreadsheets/12dB FIXED VERSION Mar 2 Reduced Template With MH371 added Feb 18 Sensitivity Analysis BFO and dBm(AutoRecovered).xlsx",
    )
    parser.add_argument(
        "--inference", type=Path, default=repository / "inputs/controls/mh371-inference.json"
    )
    parser.add_argument(
        "--truth", type=Path, default=repository / "inputs/controls/mh371-truth.csv"
    )
    parser.add_argument(
        "--audit",
        type=Path,
        default=repository / ".sources/mh371-known-flight-data/outputs/channel-selection.csv",
    )
    parser.add_argument(
        "--knots",
        type=Path,
        default=repository / ".sources/mh371-known-flight-data/data/bfo-correction-knots.json",
    )
    return parser.parse_args()


if __name__ == "__main__":
    write_outputs(parse_args())
