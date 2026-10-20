#!/usr/bin/env python3
"""Build a declination grid from any IGRF generation, in the runtime's own format.

`build.py` builds the IGRF-14 grid the estimate uses. This builds the same grid from a different
generation, so the choice of generation can be tested rather than assumed. It reuses build.py's
own synthesis, geodetic conversion, axes, seam handling and pole treatment — only the coefficient
file changes — and the official NOAA package ships `SHC_files/IGRF<1..14>.SHC`, so nothing is
downloaded.

Why this exists. Davey et al. cite their declination source as reference [31], "NOAA (2014) Grid
of magnetic field estimated values, ngdc.noaa.gov/geomag-web/#igrfgrid" — NOAA's *IGRF* grid
calculator, not the World Magnetic Model. In 2014 that calculator served IGRF-11, whose last
main-field epoch is 2010.0, so a March 2014 value was extrapolated 4.19 years on predicted
secular variation. IGRF-12 was only agreed in December 2014. IGRF-14 interpolates 2014 between
two definitive epochs and is the better model, but the difference had never been measured here,
and the magnetic autopilot modes are the ones that carry the published northern shoulder.

Measured at FL350 over 40S-8N, 85-105E on 2014-03-08: IGRF-11 minus IGRF-14 has mean -0.108 deg
and maximum 0.154 deg; restricted to the 30-37S corridor, mean -0.088 deg, maximum 0.113 deg.
IGRF-12 minus IGRF-14 is at most 0.010 deg. For scale the control-angle OU steady-state standard
deviation is 0.0826 deg, so the IGRF-11 offset is a spatially coherent bias of about one sigma of
the angle process, sustained over the whole flight, applied only to the magnetic modes.

Usage:  python .sources/igrf14-declination/build_generation.py 11 data/igrf11-declination.bin
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import struct
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as reference  # noqa: E402  (reuse its synthesis, axes and helpers unchanged)

# build.py's SOURCE/OUTPUT constants describe the pre-Sep-29 layout; resolve the package here.
PACKAGE_ZIP = HERE / "pyIGRF14.zip"


def load_generation(extract_root: Path, generation: int):
    """The official package's synthesis utilities and one generation's coefficient model."""
    with zipfile.ZipFile(PACKAGE_ZIP) as archive:
        archive.extractall(extract_root)
    package = extract_root / "pyIGRF14"
    sys.path.insert(0, str(package))
    try:
        utilities = importlib.import_module("igrf_utils")
    finally:
        sys.path.pop(0)
    coefficients = package / f"SHC_files/IGRF{generation}.SHC"
    if not coefficients.is_file():
        available = sorted(p.stem for p in (package / "SHC_files").glob("IGRF*.SHC"))
        raise SystemExit(f"no coefficients for generation {generation}; the package ships {available}")
    return utilities, utilities.load_shcfile(str(coefficients), None), coefficients


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("generation", type=int, help="IGRF generation, 1 to 14")
    parser.add_argument("output", type=Path, help="grid to write, e.g. data/igrf11-declination.bin")
    args = parser.parse_args()

    date = reference.decimal_year(reference.REFERENCE_TIME)
    latitudes, longitudes = np.meshgrid(
        reference.LATITUDE_DEG, reference.OPEN_LONGITUDE_DEG, indexing="ij")
    synthesis_latitudes = np.clip(latitudes.astype("float64"),
                                  -reference.POLE_LIMIT_FOR_SYNTHESIS_DEG,
                                  reference.POLE_LIMIT_FOR_SYNTHESIS_DEG)

    with tempfile.TemporaryDirectory(prefix=f"mh370-igrf{args.generation}-") as temporary:
        utilities, model, coefficient_path = load_generation(Path(temporary), args.generation)
        # A generation whose coefficients stop before the reference date would be extrapolated by
        # build.py's interpolator; refuse rather than do that silently.
        coefficients, epochs = reference.coefficients_at(model, date)
        open_fields = np.stack([
            reference.declination(utilities, model, coefficients, synthesis_latitudes, longitudes,
                                  float(altitude_ft) * 0.0003048).astype("float32")
            for altitude_ft in reference.PRESSURE_ALTITUDES_FT])
        if not np.all(np.isfinite(open_fields)):
            raise RuntimeError(f"IGRF-{args.generation} grid contains a non-finite declination")
        coefficient_sha256 = reference.sha256(coefficient_path)

    output_longitudes = np.concatenate(
        (reference.OPEN_LONGITUDE_DEG, np.asarray([180.0], dtype="float32")))
    fields = np.concatenate((open_fields, open_fields[:, :, :1]), axis=2)
    shape = (len(reference.PRESSURE_ALTITUDES_FT), len(reference.LATITUDE_DEG),
             len(output_longitudes))
    if fields.shape != shape or not np.array_equal(fields[:, :, 0], fields[:, :, -1]):
        raise RuntimeError("field shape or longitude seam is invalid")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = args.output.with_suffix(".bin.tmp")
    with temporary_output.open("wb") as stream:
        stream.write(reference.MAGIC)
        stream.write(struct.pack("<IIIqd", *shape,
                                 int(reference.REFERENCE_TIME.timestamp()), date))
        for axis in (reference.PRESSURE_ALTITUDES_FT, reference.LATITUDE_DEG, output_longitudes):
            stream.write(np.asarray(axis, dtype="<f4").tobytes(order="C"))
        stream.write(np.asarray(fields, dtype="<f4").tobytes(order="C"))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary_output, args.output)

    manifest = args.output.with_suffix(".manifest.json")
    manifest.write_text(json.dumps({
        "schema_version": "mh370-igrf-generation-grid-v1",
        "model": f"IGRF-{args.generation}",
        "why": "declination-generation sensitivity; Davey's reference [31] is NOAA's IGRF grid "
               "calculator, which served IGRF-11 in 2014",
        "reference_time_utc": reference.REFERENCE_TIME.isoformat(),
        "decimal_year": date,
        "coefficient_interpolation_epochs": list(epochs),
        "shc_sha256": coefficient_sha256,
        "noaa_package_sha256": reference.sha256(PACKAGE_ZIP),
        "builder_sha256": reference.sha256(Path(__file__)),
        "reference_builder_sha256": reference.sha256(HERE / "build.py"),
        "array_shape_pressure_altitude_lat_lon": list(shape),
        "output_sha256": reference.sha256(args.output),
        "output_bytes": args.output.stat().st_size,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: IGRF-{args.generation}, epochs {epochs}, "
          f"{args.output.stat().st_size:,} bytes")
    print(f"wrote {manifest}")


if __name__ == "__main__":
    main()
