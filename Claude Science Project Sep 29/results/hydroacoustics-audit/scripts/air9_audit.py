"""Audit of the air9 TL comparison (criteria.md C1, C2; c3-source-models.md C3).

Inputs (module branch hypothesis/hydroacoustics @3412bc6, read-only):
  data/blackman/fig23_air9_digitised.csv           the module's digitised Fig. 23 air9 curves (+/-2 dB chart reading)
  results-data/shared_env/air9_tl_model.csv         the module's KRAKEN TL on the shared ocean transport (authoritative)
Observed band value: power mean of the digitised points inside f_c 2^(+/-1/6), >= 2 points.

Usage: python air9_audit.py <module_dir> <out_dir>
"""
import json
import sys

import numpy as np
import pandas as pd

BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
C = 1500.0


def obs_bands(obs, st):
    o = obs[obs.station == st]; out = {}
    for fc in BANDS:
        m = (o.f_hz >= fc * 2 ** (-1 / 6)) & (o.f_hz < fc * 2 ** (1 / 6))
        if m.sum() >= 2:
            out[fc] = 10 * np.log10(np.mean(10 ** (o.tl_db[m] / 10)))
    return out


def stats(fb, r):
    x = np.log2(np.array(fb, float)); r = np.array(r, float)
    A = np.vstack([np.ones_like(x), x - x.mean()]).T
    c, *_ = np.linalg.lstsq(A, r, rcond=None)
    det = r - A @ c; n = len(r)
    se = float(np.sqrt(det @ det / (n - 2) / np.sum((x - x.mean()) ** 2))) if n > 2 else float("nan")
    return dict(n=n, f_lo=float(min(fb)), f_hi=float(max(fb)), level_median=float(np.median(r)), mean=float(r.mean()),
                slope_db_per_oct=float(c[1]), slope_se=se, shape_rms=float(np.sqrt(np.mean(det ** 2))),
                rms=float(np.sqrt(np.mean(r ** 2))))


def grade(v, p, q):
    v = abs(v)
    return "PASS" if v <= p else ("PARTIAL" if v <= q else "FAIL")


def verdict(s, shape=(3.0, 5.0)):
    g = dict(level=grade(s["level_median"], 3, 6), slope=grade(s["slope_db_per_oct"], 1.5, 3), shape=grade(s["shape_rms"], *shape))
    v = "FAIL" if "FAIL" in g.values() else ("PASS" if all(x == "PASS" for x in g.values()) else "PARTIAL")
    return g, v


def ghost_db(fc, zs):
    k = 2 * np.pi * fc / C
    return 20 * np.log10(np.abs(2 * np.sin(k * zs)))


def directivity_db(fc, elev_deg, nx=5, ny=4, Lx=24.0, Ly=16.0):
    """Azimuth-mean, band-mean |AF|^2 / N^2 of an nx x ny uniform planar array, all guns in phase."""
    xs = np.linspace(-Lx / 2, Lx / 2, nx); ys = np.linspace(-Ly / 2, Ly / 2, ny)
    X, Y = [a.ravel() for a in np.meshgrid(xs, ys)]
    fs = np.linspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 9); phi = np.linspace(0, 2 * np.pi, 181)[:-1]
    ce = np.cos(np.radians(elev_deg)); vals = []
    for f in fs:
        k = 2 * np.pi * f / C
        ph = k * ce * (np.outer(np.cos(phi), X) + np.outer(np.sin(phi), Y))
        vals.append(np.mean(np.abs(np.exp(1j * ph).sum(1)) ** 2) / len(X) ** 2)
    return 10 * np.log10(np.mean(vals))


def main(mdir, out):
    obs = pd.read_csv(f"{mdir}/data/blackman/fig23_air9_digitised.csv", comment="#")
    mod = pd.read_csv(f"{mdir}/results-data/shared_env/air9_tl_model.csv")
    mod = mod[mod.bottom == "hard"]
    ob = {st: obs_bands(obs, st) for st in ("H01W", "H08S")}
    rows, summ = [], {}
    for zs in (9.0, 10.0, 12.0):
        for model in ("M1", "M2", "M3_e0", "M3_e10", "M4_e0", "M4_e10"):
            rr = {}
            for st in ("H01W", "H08S"):
                g = mod[(mod.station == st) & np.isclose(mod.src_depth_m, zs)].set_index("fc_hz").tl_db
                fb = [f for f in ob[st] if f in g.index]
                X = []
                for f in fb:
                    x = 0.0
                    if model in ("M2", "M4_e0", "M4_e10"):
                        x -= ghost_db(f, zs)
                    if model.startswith(("M3", "M4")):
                        x += directivity_db(f, float(model.split("_e")[1]))
                    X.append(x)
                r = [ob[st][f] - g[f] + x for f, x in zip(fb, X)]
                for f, rv, x in zip(fb, r, X):
                    rows.append(dict(src_depth_m=zs, model=model, station=st, fc_hz=f, obs_tl_db=ob[st][f], model_tl_db=float(g[f]),
                                     correction_db=x, residual_db=rv))
                rr[st] = (fb, r)
                for tag, sel in (("all", lambda f: True), ("ge12.5", lambda f: f >= 12.5), ("lt12.5", lambda f: f < 12.5)):
                    fb2 = [f for f in fb if sel(f)]; r2 = [rv for f, rv in zip(fb, r) if sel(f)]
                    if len(fb2) >= 3:
                        s = stats(fb2, r2); s["grades"], s["verdict"] = verdict(s)
                        summ[f"{model}|z{zs:g}|{st}|{tag}"] = s
            (fa, ra), (fb_, rb) = rr["H01W"], rr["H08S"]
            sh = [f for f in fa if f in fb_]
            d = [ra[fa.index(f)] - rb[fb_.index(f)] for f in sh]
            s = stats(sh, d); s["grades"], s["verdict"] = verdict(s, (3.5, 5.0)); s["d_b"] = dict(zip(map(str, sh), d))
            summ[f"{model}|z{zs:g}|C2"] = s
    pd.DataFrame(rows).to_csv(f"{out}/air9_residuals.csv", index=False)
    json.dump(summ, open(f"{out}/air9_audit_summary.json", "w"), indent=1)
    for k, v in summ.items():
        if "|z10|" in k and ("all" in k or "C2" in k or "ge12.5" in k):
            print(k, round(v["level_median"], 2), round(v["slope_db_per_oct"], 2), "+/-", round(v["slope_se"], 2), round(v["shape_rms"], 2), v["verdict"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
