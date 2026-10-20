"""Forward model shared by the early-flight analyses (sequence_1825.py, early_path_fit.py).

The same BTO/BFO equations as crates/satcom (checked against the core's fixture to 1e-6),
Inmarsat satellite states (Ashton et al. 2015, Table 4, Hermite-interpolated), spherical
great-circle geodesy for route geometry, and ERA5 wind/temperature lookups (nearest grid
point in space, linear in time) for converting Mach to ground speed.
"""

import csv
import math
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".sources/inmarsat-ephemeris"))
from build import TABLE_4, hermite, unix  # noqa: E402

C = 299792.458
UP = 1646652500.0
DOWN = 3615152500.0
GES = np.array([-2368.8, 4881.1, -3342.0])
OFFSET = 499962.0 - 4283.0
A = 6378.137
F = 1 / 298.257223563
E2 = F * (2 - F)
KM_FT = 0.0003048
KMS_KT = 1.852 / 3600
R_NM = 3440.065
BIAS = 150.0

# Historical Malaysia AIP (MEKAR, NILAM, IGOGU, SANOB); AirNav Indonesia (BEDAX); AAI India (SAMAK).
WP = {
    "MEKAR": (6.503888888888889, 96.49111111111111),
    "NILAM": (6.756388888888889, 95.97638888888889),
    "IGOGU": (7.516944444444444, 94.41666666666667),
    "SAMAK": (7.9783333333333335, 94.41666666666667),
    "SANOB": (6.586111111111111, 95.66916666666667),
    "BEDAX": (5.364327777777778, 93.787575),
}
FIR_MERIDIAN = 94.41666666666667  # Kuala Lumpur FIR western boundary between 6 N and 8.1 N
T0 = unix("2014-03-07T18:22:12")  # last radar return


def ecef(lat, lon, h):
    la, lo = math.radians(lat), math.radians(lon)
    n = A / math.sqrt(1 - E2 * math.sin(la) ** 2)
    return np.array([(n + h) * math.cos(la) * math.cos(lo), (n + h) * math.cos(la) * math.sin(lo), (n * (1 - E2) + h) * math.sin(la)])


def basis(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return (np.array([-math.sin(la) * math.cos(lo), -math.sin(la) * math.sin(lo), math.cos(la)]),
            np.array([-math.sin(lo), math.cos(lo), 0.0]))


def bto(sat, lat, lon, alt):
    a = ecef(lat, lon, alt * KM_FT)
    return 2 * (np.linalg.norm(sat - a) + np.linalg.norm(sat - GES)) / C * 1e6 - OFFSET


def bfo_nobias(sat, satv, afc_hz, lat, lon, alt, vn, ve, vs_fpm=0.0):
    n, e = basis(lat, lon)
    hv = n * vn * KMS_KT + e * ve * KMS_KT
    a = ecef(lat, lon, alt * KM_FT)
    up = ecef(lat, lon, alt * KM_FT + 1.0) - a
    v = hv + up / np.linalg.norm(up) * vs_fpm * KM_FT / 60
    u = (sat - a) / np.linalg.norm(sat - a)
    uplink = -UP / C * np.dot(satv - v, u)
    g = (sat - GES) / np.linalg.norm(sat - GES)
    down = -DOWN / C * np.dot(satv, g)
    nom = ecef(0, 64.5, 36210.12)
    s = ecef(lat, lon, 0)
    cu = (s - nom) / np.linalg.norm(s - nom)
    comp = UP / C * np.dot(hv, cu)
    return uplink + down + comp + afc_hz


def bearing(p, q):
    (a, b), (c, d) = [(math.radians(x), math.radians(y)) for x, y in (p, q)]
    return math.atan2(math.sin(d - b) * math.cos(c), math.cos(a) * math.sin(c) - math.sin(a) * math.cos(c) * math.cos(d - b))


def dist_nm(p, q):
    (a, b), (c, d) = [(math.radians(x), math.radians(y)) for x, y in (p, q)]
    return 2 * R_NM * math.asin(math.sqrt(math.sin((c - a) / 2) ** 2 + math.cos(a) * math.cos(c) * math.sin((d - b) / 2) ** 2))


def dest(p, brg, d):
    a, b = map(math.radians, p)
    dr = d / R_NM
    la = math.asin(math.sin(a) * math.cos(dr) + math.cos(a) * math.sin(dr) * math.cos(brg))
    lo = b + math.atan2(math.sin(brg) * math.sin(dr) * math.cos(a), math.cos(dr) - math.sin(a) * math.sin(la))
    return (math.degrees(la), math.degrees(lo))


_TAB = [(unix(r[0]), r[1:4], r[4:7]) for r in TABLE_4]


def satstate(t):
    k = max(i for i in range(len(_TAB) - 1) if _TAB[i][0] <= t)
    p, v = hermite(t, _TAB[k], _TAB[k + 1])
    return np.array(p), np.array(v)


_AFC = [(unix(r["time_utc"]), float(r["satellite_afc_hz"])) for r in csv.DictReader(open(ROOT / "data/satcom-observations.csv"))]


def afc(t):
    """Satellite + EAFC term: linear between tabulated epochs, extrapolated from the first two before 18:25:34."""
    if t <= _AFC[0][0]:
        (t1, a1), (t2, a2) = _AFC[0], _AFC[1]
        return a1 + (a2 - a1) * (t - t1) / (t2 - t1)
    return float(np.interp(t, [x for x, _ in _AFC], [y for _, y in _AFC]))


def _era5():
    b = open(ROOT / "data/era5-wind-temperature.bin", "rb").read()
    nt, na, ny, nx = struct.unpack("<4I", b[8:24])
    o = 24
    t = np.frombuffer(b, "<i8", nt, o); o += 8 * nt
    al = np.frombuffer(b, "<f4", na, o); o += 4 * na
    y = np.frombuffer(b, "<f4", ny, o); o += 4 * ny
    x = np.frombuffer(b, "<f4", nx, o); o += 4 * nx
    n = nt * na * ny * nx
    return t, al, y, x, [np.frombuffer(b, "<f4", n, o + 4 * n * k).reshape(nt, na, ny, nx) for k in range(3)]


_W = None


def weather(t, alt, lat, lon):
    """Temperature (K) and wind east/north (kt); nearest grid point, linear in time."""
    global _W
    if _W is None:
        _W = _era5()
    T, ALT, LAT, LON, (TEMP, U, V) = _W
    it = int(np.searchsorted(T, t)) - 1
    ft = (t - T[it]) / (T[it + 1] - T[it])
    ia = int(np.argmin(np.abs(ALT - alt)))
    iy = int(round((LAT[0] - lat) / 0.5)) if LAT[0] > LAT[-1] else int(round((lat - LAT[0]) / 0.5))
    ix = int(round((lon - LON[0]) / 0.5))
    g = lambda Fld: (1 - ft) * Fld[it, ia, iy, ix] + ft * Fld[it + 1, ia, iy, ix]  # noqa: E731
    return float(g(TEMP)), float(g(U)) / 0.514444, float(g(V)) / 0.514444


def ground_speed(mach, track, t, alt, lat, lon):
    """Ground speed (kt) on a given true track (radians) for a Mach number, with the ERA5 wind (track mode, Eq. 6.18)."""
    temp, ue, vn = weather(t, alt, lat, lon)
    air = mach * math.sqrt(1.4 * 287.05287 * temp) / 0.514444
    along = ue * math.sin(track) + vn * math.cos(track)
    cross = -vn * math.sin(track) + ue * math.cos(track)
    return along + math.sqrt(max(air * air - cross * cross, 0.0))


def mach_of(gs, track, t, alt, lat, lon):
    temp, ue, vn = weather(t, alt, lat, lon)
    a_kt = math.sqrt(1.4 * 287.05287 * temp) / 0.514444
    return math.hypot(gs * math.cos(track) - vn, gs * math.sin(track) - ue) / a_kt


# Independent check against the core's fixture (crates/satcom tests).
_sat = np.array([18161.90697, 38060.47336, 1029.903202])
_sv = np.array([0.002195, -0.000728, -0.045877])
assert abs(bto(_sat, -10, 85, 25000) - 9151.491113446828) < 1e-6
assert abs(bfo_nobias(_sat, _sv, -18.075833333333, -10, 85, 25000, -450, 50) - 13.952695799684) < 1e-6
