"""End-to-end calibration smoke (order E, 19 Oct 2026): shared helpers. Standard library + numpy only.
BFO/BTO forward model: a line-by-line port of engine/crates/satcom/src/lib.rs (bto_us, bfo_without_bias_hz) and
engine/crates/geo/src/lib.rs (lla_to_ecef, local_basis), using the SAME per-epoch satellite state (ephemeris CSV) and
satellite_afc_hz (observation CSV) that the engine reads."""
import csv, json, math, os, pathlib
import numpy as np

C = 299_792.458; UP = 1_646_652_500.0; DOWN = 3_615_152_500.0
GES = np.array([-2_368.8, 4_881.1, -3_342.0]); OFFSET = 499_962.0 - 4_283.0
A = 6_378.137; F = 1 / 298.257_223_563; E2 = F * (2 - F); KM_FT = 0.000_304_8; KMS_KT = 1.852 / 3600.0
NOM_LON = 64.5; NOM_H = 36_210.12


def ecef(lat, lon, h_km):
    la, lo = math.radians(lat), math.radians(lon); s, c = math.sin(la), math.cos(la)
    n = A / math.sqrt(1 - E2 * s * s)
    return np.array([(n + h_km) * c * math.cos(lo), (n + h_km) * c * math.sin(lo), (n * (1 - E2) + h_km) * s])


def basis(lat, lon):
    la, lo = math.radians(lat), math.radians(lon); sl, cl, so, co = math.sin(la), math.cos(la), math.sin(lo), math.cos(lo)
    return np.array([-sl * co, -sl * so, cl]), np.array([-so, co, 0.0]), np.array([cl * co, cl * so, sl])


def unit(v):
    return v / np.linalg.norm(v)


def bto_us(sat, lat, lon, alt_ft):
    a = ecef(lat, lon, alt_ft * KM_FT)
    return 2.0 * (np.linalg.norm(sat - a) + np.linalg.norm(sat - GES)) / C * 1e6 - OFFSET


def bfo_nobias(sat, satv, afc, lat, lon, alt_ft, vn_kt, ve_kt, vup_fpm):
    n, e, u = basis(lat, lon)
    hor = n * (vn_kt * KMS_KT) + e * (ve_kt * KMS_KT); vel = hor + u * (vup_fpm * KM_FT / 60.0)
    a = ecef(lat, lon, alt_ft * KM_FT)
    uplink = -UP / C * (satv - vel).dot(unit(sat - a))
    downlink = -DOWN / C * satv.dot(unit(sat - GES))
    comp = UP / C * hor.dot(unit(ecef(lat, lon, 0.0) - ecef(0.0, NOM_LON, NOM_H)))
    return uplink + downlink + comp + afc


def read_rows(p):
    with open(p, newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def write_rows(p, rows, header):
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\n"); w.writeheader(); [w.writerow(r) for r in rows]


def header_of(p):
    with open(p, newline="") as f:
        return [h.strip() for h in next(csv.reader(f))]


def sat_state(eph_rows, eid):
    r = next(x for x in eph_rows if x["epoch_id"] == eid)
    return np.array([float(r["x_km"]), float(r["y_km"]), float(r["z_km"])]), np.array([float(r["vx_km_s"]), float(r["vy_km_s"]), float(r["vz_km_s"])])


def utc_plus(t, ds):
    """'2014-03-07T18:28:05.000Z' + ds seconds (integer)."""
    import datetime as dt
    x = dt.datetime.strptime(t.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f") + dt.timedelta(seconds=ds)
    return x.strftime("%Y-%m-%dT%H:%M:%S.000Z")
