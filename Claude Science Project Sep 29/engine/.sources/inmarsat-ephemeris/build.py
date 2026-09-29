#!/usr/bin/env python3
"""Build data/satellite-ephemeris-inmarsat.csv from Inmarsat's published 3F1 states.

Source: Ashton et al. (2015), "The Search for MH370", J. Navigation 68(1), Table 4:
satellite ECEF position (km) and velocity (km/s) supplied by Inmarsat for the key times
of the flight. Davey et al. (2016) used Inmarsat's satellite states. States at each
SATCOM epoch are interpolated with a cubic Hermite spline in position and velocity
between the bracketing tabulated times (at most 90 minutes apart for this near-
geostationary orbit).

Usage: build.py EPOCH_TIMES.csv OUTPUT.csv  (EPOCH_TIMES.csv: data/satellite-ephemeris.csv,
used only for its epoch ids and times)
"""

import csv
import sys
from datetime import datetime, timezone

TABLE_4 = [  # time UTC, x, y, z (km), vx, vy, vz (km/s)
    ("2014-03-07T16:30:00", 18122.9, 38080.0, 828.5, 0.00216, -0.00107, 0.06390),
    ("2014-03-07T16:45:00", 18124.8, 38079.0, 884.2, 0.00212, -0.00114, 0.05980),
    ("2014-03-07T16:55:00", 18126.1, 38078.3, 919.2, 0.00209, -0.00118, 0.05693),
    ("2014-03-07T17:05:00", 18127.3, 38077.6, 952.5, 0.00206, -0.00120, 0.05395),
    ("2014-03-07T18:25:00", 18136.7, 38071.8, 1148.5, 0.00188, -0.00117, 0.02690),
    ("2014-03-07T19:40:00", 18145.1, 38067.0, 1206.3, 0.00189, -0.00092, -0.00148),
    ("2014-03-07T20:40:00", 18152.1, 38064.0, 1159.7, 0.00200, -0.00077, -0.02422),
    ("2014-03-07T21:40:00", 18159.5, 38061.3, 1033.8, 0.00212, -0.00076, -0.04531),
    ("2014-03-07T22:40:00", 18167.2, 38058.3, 837.2, 0.00211, -0.00096, -0.06331),
    ("2014-03-08T00:10:00", 18177.5, 38051.7, 440.0, 0.00160, -0.00151, -0.08188),
    ("2014-03-08T00:20:00", 18178.4, 38050.8, 390.5, 0.00150, -0.00158, -0.08321),
]


def unix(text):
    return datetime.fromisoformat(text.rstrip("Z")).replace(tzinfo=timezone.utc).timestamp()


def hermite(t, a, b):
    """Cubic Hermite position and velocity at t between tabulated states a and b."""
    (t0, p0, v0), (t1, p1, v1) = a, b
    h = t1 - t0
    s = (t - t0) / h
    h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
    d00, d10, d01, d11 = 6 * s**2 - 6 * s, 3 * s**2 - 4 * s + 1, -6 * s**2 + 6 * s, 3 * s**2 - 2 * s
    pos = [h00 * p0[i] + h10 * h * v0[i] + h01 * p1[i] + h11 * h * v1[i] for i in range(3)]
    vel = [(d00 * p0[i] + d10 * h * v0[i] + d01 * p1[i] + d11 * h * v1[i]) / h for i in range(3)]
    return pos, vel


def main():
    table = [(unix(r[0]), r[1:4], r[4:7]) for r in TABLE_4]
    epochs = list(csv.DictReader(open(sys.argv[1])))
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["epoch_id", "time_utc", "x_km", "y_km", "z_km", "vx_km_s", "vy_km_s", "vz_km_s"])
        for e in epochs:
            t = unix(e["time_utc"])
            k = max(i for i in range(len(table) - 1) if table[i][0] <= t)
            pos, vel = hermite(t, table[k], table[k + 1])
            w.writerow([e["epoch_id"], e["time_utc"], *(f"{v:.4f}" for v in pos), *(f"{v:.6f}" for v in vel)])


if __name__ == "__main__":
    main()
