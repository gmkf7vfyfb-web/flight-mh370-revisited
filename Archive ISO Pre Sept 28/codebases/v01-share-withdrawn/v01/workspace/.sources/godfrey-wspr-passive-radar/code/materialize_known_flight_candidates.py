#!/usr/bin/env python3
"""Freeze the six previously reported known-flight WSPR candidate tables.

This is a source-recreation adapter, not product code.  It invokes the retained
trajectory-blind public-core analysis, extracts its complete pre-clustering pair
locations, and writes a deterministic compact spot table for PHaRLAP.  Aircraft
truth is never passed to the WSPR pair calculation.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import os
import platform
import sys
import tempfile
from pathlib import Path
from types import ModuleType


SCHEMA = "mh370.wspr.known-flight-candidates.v1"
DEFAULT_LEGACY_ROOT = Path(
    "/jackbox/home/.iso/thread-storage/MH370-legacy-pre-refactor-20260824"
)
EXPECTED_PAIR_COUNTS = {
    "mh371_0404": 93,
    "mh371_0611": 168,
    "mh371_0648": 269,
    "mh370_1642": 357,
    "mh370_1656": 386,
    "mh370_1707": 450,
}
CONDITION_ORDER = {
    "minus_60_min": 0,
    "actual_time": 1,
    "plus_60_min": 2,
}
SPOT_FIELDS = (
    "id",
    "time",
    "frequency",
    "tx_sign",
    "rx_sign",
    "tx_loc",
    "rx_loc",
    "tx_lat",
    "tx_lon",
    "rx_lat",
    "rx_lon",
)


class MaterializationError(RuntimeError):
    """The retained source recreation did not match its frozen contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def deterministic_gzip(payload: bytes) -> bytes:
    destination = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=destination, mtime=0
    ) as handle:
        handle.write(payload)
    return destination.getvalue()


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise MaterializationError(f"cannot import retained analysis: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def retained_analysis_path(legacy_root: Path) -> Path:
    return (
        legacy_root
        / "analyses"
        / "D-0033-known-flight-wspr-controls"
        / "src"
        / "run_analysis.py"
    )


def loaded_source_hashes(legacy_root: Path) -> dict[str, str]:
    sources: dict[str, str] = {}
    root = legacy_root.resolve()
    for module in tuple(sys.modules.values()):
        raw_path = getattr(module, "__file__", None)
        if not raw_path:
            continue
        path = Path(raw_path)
        if path.suffix == ".pyc":
            source = path.with_suffix(".py")
            if source.exists():
                path = source
        try:
            relative = path.resolve().relative_to(root)
        except (FileNotFoundError, ValueError):
            continue
        if path.is_file():
            sources[relative.as_posix()] = sha256_file(path)
    return dict(sorted(sources.items()))


def dataframe_csv_bytes(frame: object) -> bytes:
    return frame.to_csv(
        None, index=False, lineterminator="\n", float_format="%.15g"
    ).encode("utf-8")


def materialize(
    legacy_root: Path,
) -> tuple[bytes, bytes, bytes, bytes, bytes, dict[str, object]]:
    analysis_path = retained_analysis_path(legacy_root)
    if not analysis_path.is_file():
        raise MaterializationError(f"retained analysis not found: {analysis_path}")
    analysis = load_module("retained_known_flight_wspr", analysis_path)
    analysis.configure_domain()
    arcs, _references, arc_audit = analysis.build_arcs_and_references()

    analysis.d0010.WSPR_FILE = analysis.WSPR_FILE
    analysis.d0010.PROVENANCE_FILE = analysis.WSPR_PROVENANCE
    spots, wspr_provenance = analysis.d0010.load_spots()
    spots, geometry_audit = analysis.d0030.d0029.apply_six_character_geometry(spots)

    pair_frames = []
    actual_counts: dict[str, int] = {}
    physical_slots_by_epoch: dict[str, tuple[object, ...]] = {}
    for epoch, expected_count in EXPECTED_PAIR_COUNTS.items():
        result = analysis.d0031.analyze_epoch(spots, arcs[epoch], epoch)
        physical_slots_by_epoch[epoch] = tuple(result["physical_slots"])
        frame = result["pairs"].copy()
        actual_count = len(frame)
        actual_counts[epoch] = actual_count
        if actual_count != expected_count:
            raise MaterializationError(
                f"{epoch}: expected {expected_count} pairs, got {actual_count}"
            )
        pair_frames.append(frame)

    pandas = __import__("pandas")
    pairs = pandas.concat(pair_frames, ignore_index=True)
    if len(pairs) != sum(EXPECTED_PAIR_COUNTS.values()):
        raise MaterializationError("known-flight total pair count changed")
    if not set(pairs["condition"]).issubset(CONDITION_ORDER):
        raise MaterializationError("candidate table contains an unknown condition")
    pairs["_epoch_order"] = pairs["epoch"].map(
        {name: index for index, name in enumerate(EXPECTED_PAIR_COUNTS)}
    )
    pairs["_condition_order"] = pairs["condition"].map(CONDITION_ORDER)
    pairs.sort_values(
        [
            "_epoch_order",
            "_condition_order",
            "physical_slot",
            "radio_time",
            "spot_id_1",
            "spot_id_2",
            "lat_deg",
            "lon_deg_E",
        ],
        kind="mergesort",
        inplace=True,
    )
    pairs.drop(columns=["_epoch_order", "_condition_order"], inplace=True)
    pairs.reset_index(drop=True, inplace=True)

    mh371_states = analysis.read_mh371_states()
    primary_truth_rows: list[dict[str, object]] = []
    for epoch in EXPECTED_PAIR_COUNTS:
        audit_index = arc_audit.index[arc_audit["epoch"] == epoch]
        if len(audit_index) != 1:
            raise MaterializationError(f"{epoch}: expected one arc audit row")
        row_index = audit_index[0]
        representative_time = pandas.Timestamp(
            arc_audit.loc[row_index, "representative_time_utc"]
        )
        slots = physical_slots_by_epoch[epoch]
        if not slots:
            raise MaterializationError(f"{epoch}: no physical WSPR slots")
        ordered_slots = tuple(sorted(pandas.Timestamp(value) for value in slots))
        slot = min(
            (pandas.Timestamp(value) for value in slots),
            key=lambda value: abs(
                (
                    value
                    + pandas.Timedelta(seconds=56.242)
                    - representative_time
                ).total_seconds()
            ),
        )
        midpoint = slot + pandas.Timedelta(seconds=56.242)
        case = analysis.CASES[epoch]
        truth = (
            analysis.interpolate_mh371(mh371_states, midpoint)
            if case["flight"] == "MH371"
            else analysis.read_mh370_reference(midpoint)
        )
        values = {
            "physical_wspr_slots": ";".join(str(value) for value in ordered_slots),
            "physical_wspr_slot_count": len(ordered_slots),
            "primary_truth_physical_slot": str(slot),
            "primary_truth_slot_midpoint_utc": str(midpoint),
            "primary_truth_slot_offset_from_bto_seconds": float(
                (midpoint - representative_time).total_seconds()
            ),
            "primary_truth_lat_deg": truth["lat_deg"],
            "primary_truth_lon_deg_E": truth["lon_deg_E"],
            "primary_truth_altitude_ft": truth["altitude_ft"],
            "primary_truth_altitude_km": truth["altitude_ft"] * 0.0003048,
            "primary_truth_reference_type": truth["reference_type"],
            "primary_truth_source_rows": ";".join(
                map(str, truth["source_rows"])
            ),
            "primary_truth_source_time_offset_seconds": truth[
                "time_offset_seconds"
            ],
            "primary_truth_role": (
                "withheld nearest-slot truth used only after blind PHaRLAP "
                "selection; same target applied symmetrically to all three panels"
            ),
        }
        for condition, offset_minutes in (
            ("minus_60_min", -60),
            ("actual_time", 0),
            ("plus_60_min", 60),
        ):
            values[f"{condition}_radio_window_start"] = str(
                ordered_slots[0] + pandas.Timedelta(minutes=offset_minutes)
            )
            values[f"{condition}_radio_window_end"] = str(
                ordered_slots[-1] + pandas.Timedelta(minutes=offset_minutes)
            )
        for field, value in values.items():
            arc_audit.loc[row_index, field] = value
        primary_truth_rows.append({"epoch": epoch, **values})

    arc_rows: list[dict[str, object]] = []
    truth_rows: list[dict[str, object]] = []
    west, east, south, north = analysis.MAP_EXTENT
    for epoch, expected in EXPECTED_PAIR_COUNTS.items():
        del expected
        case = analysis.CASES[epoch]
        audit_row = arc_audit.loc[arc_audit["epoch"] == epoch].iloc[0]
        arc = arcs[epoch]
        point_index = 0
        for latitude, longitude in zip(arc.curve_lat, arc.curve_lon):
            if south <= float(latitude) <= north and west <= float(longitude) <= east:
                arc_rows.append({
                    "epoch_id": epoch,
                    "sequence": case["sequence"],
                    "flight": case["flight"],
                    "arc_time_utc": audit_row["representative_time_utc"],
                    "arc_point_index": point_index,
                    "latitude_deg": float(latitude),
                    "longitude_deg_e": float(longitude),
                })
                point_index += 1
        if point_index < 2:
            raise MaterializationError(f"{epoch}: insufficient in-domain arc points")
        source_label = (
            "MH371 retained ACARS workbook"
            if case["flight"] == "MH371"
            else "MH370 retained SITA workbook"
        )
        truth_rows.extend((
            {
                "epoch_id": epoch,
                "truth_id": f"{epoch}-arc-epoch",
                "reference_role": "arc_epoch",
                "physical_slot": "",
                "is_nearest_arc_slot": False,
                "position_time_utc": audit_row["representative_time_utc"],
                "latitude_deg": audit_row["reference_lat_deg"],
                "longitude_deg_e": audit_row["reference_lon_deg_E"],
                "altitude_km": audit_row["reference_altitude_ft"] * 0.0003048,
                "position_source": source_label,
                "position_method": audit_row["reference_type"],
                "time_offset_seconds": audit_row["reference_time_offset_seconds"],
            },
            {
                "epoch_id": epoch,
                "truth_id": f"{epoch}-nearest-wspr-slot",
                "reference_role": "physical_slot",
                "physical_slot": audit_row["primary_truth_physical_slot"],
                "is_nearest_arc_slot": True,
                "position_time_utc": audit_row["primary_truth_slot_midpoint_utc"],
                "latitude_deg": audit_row["primary_truth_lat_deg"],
                "longitude_deg_e": audit_row["primary_truth_lon_deg_E"],
                "altitude_km": audit_row["primary_truth_altitude_km"],
                "position_source": source_label,
                "position_method": audit_row["primary_truth_reference_type"],
                "time_offset_seconds": audit_row[
                    "primary_truth_source_time_offset_seconds"
                ],
            },
        ))

    used_ids = set(map(int, pairs["spot_id_1"])) | set(
        map(int, pairs["spot_id_2"])
    )
    compact_spots = spots.loc[spots["id"].isin(used_ids), SPOT_FIELDS].copy()
    compact_spots.sort_values("id", kind="mergesort", inplace=True)
    compact_spots.reset_index(drop=True, inplace=True)
    found_ids = set(map(int, compact_spots["id"]))
    if found_ids != used_ids:
        raise MaterializationError(
            f"compact spot table omitted {len(used_ids - found_ids)} referenced reports"
        )
    if compact_spots["id"].duplicated().any():
        raise MaterializationError("compact spot table contains duplicate ids")
    if not all(
        len(str(locator).strip()) == 6
        for field in ("tx_loc", "rx_loc")
        for locator in compact_spots[field]
    ):
        raise MaterializationError("compact spot table contains a non-six-character locator")

    pair_payload = deterministic_gzip(dataframe_csv_bytes(pairs))
    spot_payload = deterministic_gzip(dataframe_csv_bytes(compact_spots))
    arc_audit_payload = dataframe_csv_bytes(arc_audit)
    arc_payload = dataframe_csv_bytes(pandas.DataFrame(arc_rows))
    truth_payload = dataframe_csv_bytes(pandas.DataFrame(truth_rows))
    source_inputs = {
        "wspr_extract": analysis.WSPR_FILE,
        "wspr_provenance": analysis.WSPR_PROVENANCE,
        "sita_workbook": analysis.SITA,
        "mh371_acars_workbook": analysis.MH371_ACARS,
        "satellite_ephemeris": analysis.d0011.EPHEMERIS,
    }
    manifest: dict[str, object] = {
        "schema": SCHEMA,
        "method": (
            "Complete pre-clustering same-slot great-circle pair locations from "
            "the retained six-epoch trajectory-blind known-flight analysis; "
            "aircraft reference positions were not supplied to pair generation."
        ),
        "epochs": list(EXPECTED_PAIR_COUNTS),
        "expected_pair_counts": EXPECTED_PAIR_COUNTS,
        "actual_pair_counts": actual_counts,
        "total_pairs": len(pairs),
        "compact_spot_records": len(compact_spots),
        "pair_columns": list(pairs.columns),
        "spot_columns": list(compact_spots.columns),
        "inputs": {
            name: {
                "path_relative_to_legacy_root": path.resolve()
                .relative_to(legacy_root.resolve())
                .as_posix(),
                "sha256": sha256_file(path),
            }
            for name, path in source_inputs.items()
        },
        "loaded_retained_sources_sha256": loaded_source_hashes(legacy_root),
        "wspr_provenance_identity": wspr_provenance,
        "six_character_geometry_audit": geometry_audit,
        "arc_audit": arc_audit.to_dict(orient="records"),
        "primary_truth_scoring": {
            "rule": (
                "For each epoch choose the physical WSPR transmission midpoint "
                "nearest the representative BTO time; evaluate aircraft truth at "
                "that time without extrapolating beyond retained MH370 truth; score "
                "that slot only and apply the same target to all control panels."
            ),
            "wspr_midpoint_offset_seconds": 56.242,
            "rows": primary_truth_rows,
        },
        "outputs": {
            "known_flight_pair_locations.csv.gz": {
                "sha256": hashlib.sha256(pair_payload).hexdigest(),
                "rows": len(pairs),
            },
            "known_flight_spot_records.csv.gz": {
                "sha256": hashlib.sha256(spot_payload).hexdigest(),
                "rows": len(compact_spots),
            },
            "known_flight_arc_truth_audit.csv": {
                "sha256": hashlib.sha256(arc_audit_payload).hexdigest(),
                "rows": len(arc_audit),
                "role": "withheld truth and BTO-arc audit; never a pair-selection input",
            },
            "known_flight_arcs.csv": {
                "sha256": hashlib.sha256(arc_payload).hexdigest(),
                "rows": len(arc_rows),
            },
            "known_flight_truth_references.csv": {
                "sha256": hashlib.sha256(truth_payload).hexdigest(),
                "rows": len(truth_rows),
                "role": "post-selection overlays and nearest-slot recovery only",
            },
        },
        "runtime": {
            "python": platform.python_version(),
            "pandas": pandas.__version__,
        },
    }
    return (
        pair_payload,
        spot_payload,
        arc_audit_payload,
        arc_payload,
        truth_payload,
        manifest,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-root", type=Path, default=DEFAULT_LEGACY_ROOT)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "known-flight",
    )
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    (
        pair_payload,
        spot_payload,
        arc_audit_payload,
        arc_payload,
        truth_payload,
        manifest,
    ) = materialize(arguments.legacy_root)
    output = arguments.output_directory
    pair_path = output / "known_flight_pair_locations.csv.gz"
    spot_path = output / "known_flight_spot_records.csv.gz"
    arc_audit_path = output / "known_flight_arc_truth_audit.csv"
    arcs_path = output / "known_flight_arcs.csv"
    truth_path = output / "known_flight_truth_references.csv"
    manifest_path = output / "known_flight_candidate_manifest.json"
    atomic_write(pair_path, pair_payload)
    atomic_write(spot_path, spot_payload)
    atomic_write(arc_audit_path, arc_audit_payload)
    atomic_write(arcs_path, arc_payload)
    atomic_write(truth_path, truth_payload)
    atomic_write(manifest_path, canonical_json(manifest))
    print(
        json.dumps(
            {
                "pair_path": str(pair_path),
                "spot_path": str(spot_path),
                "arc_audit_path": str(arc_audit_path),
                "arcs_path": str(arcs_path),
                "truth_path": str(truth_path),
                "manifest_path": str(manifest_path),
                "pair_count": manifest["total_pairs"],
                "spot_count": manifest["compact_spot_records"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
