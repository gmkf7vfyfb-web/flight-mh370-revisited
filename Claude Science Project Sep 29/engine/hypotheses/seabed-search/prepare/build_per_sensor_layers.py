#!/usr/bin/env python3
"""Write one coverage raster per Phase 2 sensor, so that repeat search can be modelled.

    python hypotheses/seabed-search/prepare/build_per_sensor_layers.py

`build_coverage.py` collapses the four Phase 2 mosaics into a per-cell maximum, `phase2.cov`.
That union is right for a single cumulative campaign and wrong for repeat-search dependence:
it hides the ground that was swept more than once. This script writes the same cells per
sensor, from the per-sensor caches `build_coverage.py` already produced, and prints the
double-coverage area the union conceals.

Outputs (same format, grid and resolution as `phase2.cov`):
  hypotheses/seabed-search/coverage/phase2-<sensor>.cov
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_coverage import CACHE, GRIDS, SENSORS, area_km2, coarse, write_cov  # noqa: E402

MODULE = Path(__file__).resolve().parent.parent


def main():
    grid = GRIDS["phase2"]
    out = MODULE / "coverage"
    fine = {}
    for name in SENSORS:
        path = CACHE / f"phase2-{name}.npz"
        if not path.is_file():
            raise SystemExit(f"missing {path}; run build_coverage.py first")
        fine[name] = np.load(path)["fraction"]

    for name, f in fine.items():
        raster = write_cov(out / f"phase2-{name}.cov", coarse(f), grid)
        print(f"phase2-{name}.cov  {area_km2(f, grid, 255):>10,.1f} km2 fine"
              f"  {area_km2(raster, grid):>10,.1f} km2 raster")

    union = np.maximum.reduce(list(fine.values()))
    total = np.sum([f.astype(np.uint16) for f in fine.values()], axis=0)
    excess = np.clip(total.astype(np.int32) - union.astype(np.int32), 0, None)
    twice = (np.sum([(f > 0).astype(np.uint8) for f in fine.values()], axis=0) >= 2).astype(np.uint8)
    print(f"union {area_km2(union, grid, 255):,.1f} km2; "
          f"sum of sensors {area_km2(total, grid, 255):,.1f} km2; "
          f"repeat coverage the union hides {area_km2(excess, grid, 255):,.1f} km2; "
          f"ground with data from two or more sensors {area_km2(twice, grid):,.1f} km2")


if __name__ == "__main__":
    main()
