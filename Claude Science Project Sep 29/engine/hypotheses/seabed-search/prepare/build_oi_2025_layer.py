#!/usr/bin/env python3
"""Build the INFERRED Ocean Infinity 2025-26 coverage raster, for the separately reported variant.

    python hypotheses/seabed-search/prepare/build_oi_2025_layer.py [--footprints PATH]

Ocean Infinity published no geometry for the renewed search. What exists is a community tracing of
the two bands in its March 2024 presentation, graded C by whoever made it:

  outboard/southeast band   9,767.8 km2   "community vessel tracking indicates the outboard band
                                           was traversed; exact AUV coverage remains unpublished"
  inboard/northwest band    6,072.0 km2   "most likely concentration of the official remaining
                                           area"; the official residual is 7,428.54 km2

The two together are about 15,840 km2 - the contract area. **The contract area is not searched
ground**, and the reported 7,571 km2 of survey is not spread over it. This script puts the reported
area on the OUTBOARD band alone, as a coverage fraction, and leaves the inboard band at zero, which
is what the community vessel tracks and the official residual both say.

By Pete's ruling of 9 Oct 2026 (~18:30 UTC) the raster is committed under
hypotheses/seabed-search/coverage/. The tracing itself is read from the frozen September snapshot,
which already holds it, so there is one copy with a stable checksum. Every use of this layer carries
the grade-C inferred-coverage footnote in coverage/PROVENANCE.md.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_coverage import CACHE, COARSE, FINE, area_km2, coarse, rasterise, rings_of, write_cov  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
# The traced bands, by path, never committed into this module.
FOOTPRINTS = ROOT.parent.parent / "Sept 27 2026 backup PL ChatGPT instance" / \
    "2026-09-28_codex_drift_and_search_update" / "combined_panel_versions" / "search_footprints.geojson"
OUTBOARD = "oi2024_proposed_outboard_southeast"
INBOARD = "oi2024_proposed_inboard_northwest"
# Ocean Infinity's reported survey in the 2025-26 season, as carried in the module brief.
REPORTED_KM2 = 7571.0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--footprints", type=Path, default=FOOTPRINTS)
    args = parser.parse_args()
    if not args.footprints.is_file():
        raise SystemExit(f"missing {args.footprints}: the traced bands are read by path, not from this module")
    doc = json.loads(args.footprints.read_text())
    bands = {f["properties"]["id"]: f for f in doc["features"] if f["properties"].get("id") in (OUTBOARD, INBOARD)}
    if OUTBOARD not in bands:
        raise SystemExit(f"{args.footprints}: no feature `{OUTBOARD}`")

    rings = rings_of(bands[OUTBOARD]["geometry"])
    xs = [x for r in rings for x, _ in r]
    ys = [y for r in rings for _, y in r]
    south = float(np.floor(min(ys) / COARSE) * COARSE)
    west = float(np.floor(min(xs) / COARSE) * COARSE)
    rows = int(np.ceil((max(ys) - south) / COARSE)) + 1
    cols = int(np.ceil((max(xs) - west) / COARSE)) + 1
    grid = (south, west, rows, cols)

    fine = rasterise(rings, grid).view(np.uint8) * np.uint8(255)
    outline_km2 = area_km2(fine, grid, 255)
    raster = write_cov(CACHE / "ocean-infinity-2025.cov", coarse(fine), grid)
    fraction = REPORTED_KM2 / outline_km2
    inboard_km2 = area_km2(rasterise(rings_of(bands[INBOARD]["geometry"]), grid).view(np.uint8) * np.uint8(255),
                           grid, 255) if INBOARD in bands else float("nan")
    print(f"outboard band outline {outline_km2:,.1f} km2 (raster {area_km2(raster, grid):,.1f} km2 at {COARSE} deg)")
    print(f"inboard band, NOT searched, inside this grid {inboard_km2:,.1f} km2")
    print(f"reported survey {REPORTED_KM2:,.0f} km2 -> coverage_fraction {fraction:.4f} on the outboard band")
    print(f"wrote {CACHE / 'ocean-infinity-2025.cov'}  grid {grid}, fine step {FINE} deg")


if __name__ == "__main__":
    main()
