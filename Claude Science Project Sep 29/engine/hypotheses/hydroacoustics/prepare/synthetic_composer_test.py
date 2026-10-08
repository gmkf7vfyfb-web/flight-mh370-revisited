"""Synthetic composer test (brief section 7 step 2): how much would a hydroacoustic detection at one,
two or three IMS sites, with O-C inside its stated uncertainty, move the impact PDF?

PROVISIONAL BY CONSTRUCTION. Ruled 2026-10-08 (coordination/HYDROACOUSTICS.md, Q2): run first on a
parametric 7th-arc PDF, then rerun on end of flight's impact samples when they are published.

STAND-IN IMPACT PDF
  Arc geometry: a small circle fitted to the density ridge (density-weighted mean longitude per
  0.25 deg latitude row) of the full-scale core-only no-exhaustion-prior posterior at 00:19:37
  (results/no-exhaustion-prior-summary.json; 7M particles x 8 seeds, split-half 0.951).
  Along-arc position: latitude drawn from that run's latitude marginal (median -37.225).
  Cross-arc offset: N(0, sigma_x), sigma_x declared (baseline 20 NM), standing in for descent reach.
  Impact time: 00:19:37 + N(mu_t, sigma_t), independent of position (a known simplification; the
  real impact samples carry the correlation).

SYNTHETIC DETECTION MODEL
  Arrival: t_s = t_imp + d_s(x) / c, c = 1.482 km/s. Per-station timing sd = sqrt(pick^2 +
  (d_s sd_c / c^2)^2), sd_c = 0.006 km/s, independent across stations (conservative for differences).
  Impact time is shared across stations and marginalised exactly: the residual vector is
  multivariate normal with covariance diag(sd_s^2) + sigma_t^2 11^T.
  Bearing (optional): back-azimuth error Student-t, nu = 3, scaled to sd 3.3 deg - the DEMONSTRATED
  bearing error of brief section 5, not the claimed 0.4 deg.
  Truths: K samples drawn from the stand-in PDF; observations generated at each truth with noise
  drawn from the same error model, so O-C is inside the stated uncertainty by construction.

PRE-REGISTERED VERDICT (fixed before the first run; do not edit after looking)
  Per configuration, over the K truths, report the median of:
    I   information gain KL(posterior || prior) in bits;
    R   posterior along-arc sd / prior along-arc sd;
    D   |posterior mean - prior mean| along arc / posterior along-arc sd.
  "Moves the PDF materially":  median I >= 1.0 bit.
  "Negligible":                median I <  0.25 bit.
  Between: "modest". The brief's test - a marginal single-site detection moving the posterior by
  less than its own uncertainty - is D < 1; it is reported for every configuration.

Run: python prepare/synthetic_composer_test.py <summary.json> <out_dir>
"""

import itertools
import json
import pathlib
import sys

import numpy as np
from pyproj import Geod

GEOD = Geod(ellps="WGS84")
R_EARTH_KM = 6371.0088
NM_KM = 1.852
T0 = 0.0  # impact times are relative to 00:19:37 UTC

STATIONS = {  # FDSN triad centroids, data/stations.csv
    "H01W": (-34.890303, 114.142637),
    "H08S": (-7.639380, 72.483828),
    "H08N": (-6.337533, 71.002077),
}
C_KM_S, SD_C_KM_S = 1.482, 0.006
BEARING_SD_DEG, BEARING_NU = 3.3, 3.0

N_PRIOR = 200_000
K_TRUTHS = 300
SEED = 20261008

BASE = dict(sigma_x_nm=20.0, mu_t_s=300.0, sigma_t_s=180.0, pick_s=10.0)
SENSITIVITY = {
    "sigma_t_s": [0.0, 60.0, 180.0, 600.0],
    "pick_s": [2.0, 10.0, 30.0],
    "sigma_x_nm": [5.0, 20.0, 40.0],
}
STATION_SETS = [("H01W",), ("H08S",), ("H01W", "H08S"), ("H08S", "H08N"), ("H01W", "H08S", "H08N")]


def ridge_and_marginal(summary_path):
    s = json.load(open(summary_path))
    case = s["cases"][0]
    lat0, lon0 = s["map"]["lat"][0], s["map"]["lon"][0]
    step = s["map"]["step"]
    cells = np.array(case["map"], dtype=float)
    lat = lat0 + (cells[:, 0] + 0.5) * step
    lon = lon0 + (cells[:, 1] + 0.5) * step
    w = cells[:, 2]
    ridge = []
    for la in np.unique(lat):
        m = lat == la
        if w[m].sum() > 1e-4 * w.sum() / 40:
            ridge.append((la, np.average(lon[m], weights=w[m]), w[m].sum()))
    ridge = np.array(ridge)
    g = s["grid"]
    grid = np.linspace(g["min"], g["max"], g["points"])
    dens = np.array(case["density"], dtype=float)
    return ridge, grid, dens, case["stats"]


def unit(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def fit_small_circle(ridge):
    """Small circle (pole p, angular radius rho) minimising weighted squared angular residuals."""
    from scipy.optimize import least_squares
    v = unit(ridge[:, 0], ridge[:, 1])
    wt = np.sqrt(ridge[:, 2] / ridge[:, 2].sum())

    def res(q):
        p = unit(q[0], q[1])
        return wt * (np.arccos(np.clip(v @ p, -1, 1)) - q[2])

    q = least_squares(res, x0=[0.0, 64.5, np.radians(40.0)]).x
    r = np.degrees(np.arccos(np.clip(v @ unit(q[0], q[1]), -1, 1))) - np.degrees(q[2])
    rms_km = np.sqrt(np.average((r * np.pi / 180 * R_EARTH_KM) ** 2, weights=ridge[:, 2]))
    return q, rms_km


def arc_point(q, lat_target):
    """Point on the small circle at a given latitude, on the arc's southern-Indian-Ocean branch."""
    p = unit(q[0], q[1])
    e = np.cross([0, 0, 1.0], p); e /= np.linalg.norm(e)
    n = np.cross(p, e)
    th = np.linspace(-np.pi, np.pi, 20001)
    pts = (np.cos(q[2]) * p[None] + np.sin(q[2]) * (np.cos(th)[:, None] * e + np.sin(th)[:, None] * n))
    la = np.degrees(np.arcsin(pts[:, 2])); lo = np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))
    keep = (lo > 80) & (lo < 110) & (la < -10)
    la, lo, th = la[keep], lo[keep], th[keep]
    o = np.argsort(la)
    return np.interp(lat_target, la[o], lo[o]), np.interp(lat_target, la[o], th[o])


def draw_prior(rng, q, grid, dens, n, sigma_x_nm):
    cdf = np.cumsum(dens); cdf /= cdf[-1]
    lat = np.interp(rng.random(n), cdf, grid)
    lon, _ = arc_point(q, lat)
    # along-arc coordinate: geodesic distance from the arc point at the posterior median, signed
    ref_lon, _ = arc_point(q, np.array([-37.224711]))
    az_along, _, s_along = GEOD.inv(np.full(n, ref_lon[0]), np.full(n, -37.224711), lon, lat)
    s_along = np.where(lat >= -37.224711, 1, -1) * s_along / 1000.0
    # cross-arc offset perpendicular to the local arc direction (towards the pole = inside)
    d = 0.05
    lon2, _ = arc_point(q, lat + d)
    az_tan, _, _ = GEOD.inv(lon, lat, lon2, lat + d)
    x = rng.normal(0.0, sigma_x_nm * NM_KM, n)
    lon_i, lat_i, _ = GEOD.fwd(lon, lat, az_tan + 90.0, x * 1000.0)
    return np.column_stack([lat_i, lon_i, s_along, x])


def station_geometry(pts):
    out = {}
    for name, (sla, slo) in STATIONS.items():
        n = len(pts)
        az_bk, _, d = GEOD.inv(np.full(n, slo), np.full(n, sla), pts[:, 1], pts[:, 0])
        out[name] = (d / 1000.0, np.mod(az_bk, 360.0))
    return out


def log_t(x, scale, nu):
    z = x / scale
    return -0.5 * (nu + 1) * np.log1p(z * z / nu)


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


def evaluate(rng, prior, geom, stations, cfg, bearing):
    s_al = prior[:, 2]
    w0 = np.full(len(prior), 1.0 / len(prior))
    prior_sd = np.sqrt(np.cov(s_al))
    prior_mean = s_al.mean()
    bscale = BEARING_SD_DEG / np.sqrt(BEARING_NU / (BEARING_NU - 2))
    m = len(stations)
    res = []
    truths = rng.choice(len(prior), K_TRUTHS, replace=False)
    for ti in truths:
        sd = np.array([np.hypot(cfg["pick_s"], geom[s][0][ti] * SD_C_KM_S / C_KM_S**2) for s in stations])
        t_imp = cfg["mu_t_s"] + cfg["sigma_t_s"] * rng.normal()
        obs = np.array([t_imp + geom[s][0][ti] / C_KM_S + sd[j] * rng.normal() for j, s in enumerate(stations)])
        # residual for every prior sample, with mu_t removed; covariance diag(sd_s^2) + sigma_t^2 11^T
        # (per-sample sd differences from range are second order and are evaluated at the truth)
        r = obs[None, :] - cfg["mu_t_s"] - np.column_stack([geom[s][0] / C_KM_S for s in stations])
        cov = np.diag(sd**2) + cfg["sigma_t_s"] ** 2 * np.ones((m, m))
        ci = np.linalg.inv(cov)
        ll = -0.5 * np.einsum("ij,jk,ik->i", r, ci, r)
        if bearing:
            for s in stations:
                bt = geom[s][1][ti] + bscale * rng.standard_t(BEARING_NU)
                ll += log_t(wrap180(bt - geom[s][1]), bscale, BEARING_NU)
        ll -= ll.max()
        w = np.exp(ll); w /= w.sum()
        nz = w > 0
        info_bits = float(np.sum(w[nz] * np.log2(w[nz] / w0[nz])))
        ess = 1.0 / np.sum(w * w)
        mu = np.sum(w * s_al)
        post_sd = np.sqrt(np.sum(w * (s_al - mu) ** 2))
        res.append((info_bits, post_sd / prior_sd, abs(mu - prior_mean) / post_sd,
                    abs(mu - s_al[ti]), abs(prior_mean - s_al[ti]), ess))
    a = np.array(res)
    return {
        "info_bits_median": float(np.median(a[:, 0])), "info_bits_q10": float(np.quantile(a[:, 0], 0.1)),
        "info_bits_q90": float(np.quantile(a[:, 0], 0.9)),
        "sd_ratio_median": float(np.median(a[:, 1])), "shift_over_post_sd_median": float(np.median(a[:, 2])),
        "err_post_km_median": float(np.median(a[:, 3])), "err_prior_km_median": float(np.median(a[:, 4])),
        "ess_median": float(np.median(a[:, 5])), "prior_along_sd_km": float(prior_sd),
    }


def verdict(i):
    return "material" if i >= 1.0 else ("negligible" if i < 0.25 else "modest")


def main(summary_path, out_dir):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    ridge, grid, dens, stats = ridge_and_marginal(summary_path)
    q, rms_km = fit_small_circle(ridge)
    rows, priors = [], {}
    configs = [("base", BASE)]
    for k, vals in SENSITIVITY.items():
        for v in vals:
            if v != BASE[k]:
                c = dict(BASE); c[k] = v; configs.append((f"{k}={v:g}", c))
    for label, cfg in configs:
        key = cfg["sigma_x_nm"]
        if key not in priors:
            pr = draw_prior(rng, q, grid, dens, N_PRIOR, key)
            priors[key] = (pr, station_geometry(pr))
        pr, geom = priors[key]
        for stations in STATION_SETS:
            for bearing in (False, True):
                r = evaluate(rng, pr, geom, stations, cfg, bearing)
                rows.append({"config": label, **cfg, "stations": "+".join(stations), "n_sites": len(stations),
                             "bearing": bearing, **r, "verdict": verdict(r["info_bits_median"])})
                print(f"{label:16s} {'+'.join(stations):16s} bearing={int(bearing)} "
                      f"I={r['info_bits_median']:.2f} R={r['sd_ratio_median']:.2f} "
                      f"D={r['shift_over_post_sd_median']:.2f} -> {rows[-1]['verdict']}", flush=True)
    meta = {"arc_pole_lat": float(q[0]), "arc_pole_lon": float(q[1]), "arc_radius_deg": float(np.degrees(q[2])),
            "arc_fit_rms_km": float(rms_km), "ridge_rows": int(len(ridge)), "core_stats": stats,
            "n_prior": N_PRIOR, "k_truths": K_TRUTHS, "seed": SEED, "base": BASE,
            "c_km_s": C_KM_S, "sd_c_km_s": SD_C_KM_S, "bearing_sd_deg": BEARING_SD_DEG, "bearing_nu": BEARING_NU,
            "provisional": "parametric 7th-arc stand-in; rerun on end-of-flight impact samples when published"}
    json.dump({"meta": meta, "rows": rows}, open(out / "synthetic-composer-test.json", "w"), indent=1)
    np.save(out / "prior_base.npy", priors[BASE["sigma_x_nm"]][0][:20000])
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
