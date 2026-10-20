"""Statistics of drifter-replay separations (`examples/drifter_replay.rs`): per lead, per component RMS
and mean, median and 90th percentile of |d|; drifter-block bootstrap 95% intervals at 2 and 15 days
(segments of one drifter overlap, so drifters are the resampling unit); an Ornstein-Uhlenbeck fit
<d_i^2>(t) = 2 s^2 T (t - T (1 - exp(-t/T))) per component, s the velocity-error SD and T its
decorrelation time; and the diffusivity-equivalent K(t) = <|d|^2> / (4 t).

python replay_stats.py <segments.json> <out.json> name=sep.f32 [name=sep.f32 ...]
"""
import json, sys
from datetime import datetime, timezone
import numpy as np
from scipy.optimize import least_squares

segs = json.load(open(sys.argv[1]))
S = segs["segments"]
L = segs["fixes"] - 1
dt_d = segs["step_s"] / 86400.0
lead_d = dt_d * np.arange(1, L + 1)
ids = np.array([s["id"] for s in S])
drog = np.array([s["drogued"] for s in S])
lon0 = np.array([s["lon"][0] for s in S]); lat0 = np.array([s["lat"][0] for s in S])
month = np.array([datetime.fromtimestamp(s["t0"], timezone.utc).month for s in S])
box = (lon0 >= 80) & (lon0 <= 110) & (lat0 >= -45) & (lat0 <= -20)
subsets = {"domain": np.ones(len(S), bool), "box80-110E_45-20S": box, "box_MAM": box & np.isin(month, [3, 4, 5])}
rng = np.random.default_rng(20140308)
REPORT = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 15]


def ou(t, s, T):
    return 2 * s * s * T * (t - T * (1 - np.exp(-t / T)))


def fit(ms):  # ms: mean-square separation per lead, km^2 -> s in m/s, T in days
    ok = np.isfinite(ms) & (ms > 0)
    t = lead_d[ok] * 86400.0
    y = ms[ok] * 1e6
    r = least_squares(lambda p: np.log(ou(t, np.exp(p[0]), np.exp(p[1]))) - np.log(y), x0=[np.log(0.1), np.log(2 * 86400)])
    return float(np.exp(r.x[0])), float(np.exp(r.x[1]) / 86400.0)


def boot_rms(d, sel, lead_index, B=400):
    u = np.unique(ids[sel])
    by = {k: np.where(sel & (ids == k))[0] for k in u}
    out = []
    for _ in range(B):
        k = np.concatenate([by[x] for x in rng.choice(u, len(u))])
        v = d[k, lead_index]
        v = v[np.isfinite(v).all(1)]
        out.append(np.sqrt((v ** 2).mean(0)) if len(v) else [np.nan, np.nan])
    return np.percentile(np.array(out), [2.5, 97.5], axis=0).round(2).tolist()


res = {"segments_file": sys.argv[1], "lead_days": REPORT, "configs": {}}
for arg in sys.argv[3:]:
    name, path = arg.split("=", 1)
    d = np.fromfile(path, "<f4").reshape(len(S), L, 2).astype(float)
    cfg = {}
    for dname, dsel in (("drogued", drog), ("undrogued", ~drog)):
        for sname, ssel in subsets.items():
            sel = dsel & ssel
            if sel.sum() < 20:
                continue
            x = d[sel]
            fin = np.isfinite(x).all(2)
            n = fin.sum(0)
            ms = np.where((n > 0)[:, None], np.nansum(np.where(fin[..., None], x, 0) ** 2, 0) / np.maximum(n, 1)[:, None], np.nan)
            mean = np.nansum(np.where(fin[..., None], x, 0), 0) / np.maximum(n, 1)[:, None]
            mag = np.where(fin, np.hypot(x[..., 0], x[..., 1]), np.nan)
            rows = []
            for ld in REPORT:
                i = int(round(ld / dt_d)) - 1
                rows.append(dict(lead_d=ld, n=int(n[i]), rms_e_km=round(float(np.sqrt(ms[i, 0])), 2), rms_n_km=round(float(np.sqrt(ms[i, 1])), 2),
                                 mean_e_km=round(float(mean[i, 0]), 2), mean_n_km=round(float(mean[i, 1]), 2),
                                 median_km=round(float(np.nanmedian(mag[:, i])), 2), p90_km=round(float(np.nanpercentile(mag[:, i], 90)), 2),
                                 K_equiv_m2_s=round(float((ms[i].sum() * 1e6) / (4 * ld * 86400)), 1)))
            fe, fn = fit(ms[:, 0]), fit(ms[:, 1])
            i2, i15 = int(round(2 / dt_d)) - 1, L - 1
            cfg[f"{dname}/{sname}"] = dict(
                segments=int(sel.sum()), drifters=int(len(np.unique(ids[sel]))), rows=rows,
                ou_fit=dict(east=dict(sigma_m_s=round(fe[0], 4), T_days=round(fe[1], 2)), north=dict(sigma_m_s=round(fn[0], 4), T_days=round(fn[1], 2))),
                boot95_rms_km_2d=boot_rms(d, sel, i2), boot95_rms_km_15d=boot_rms(d, sel, i15))
    res["configs"][name] = cfg
json.dump(res, open(sys.argv[2], "w"), indent=1)
for name, cfg in res["configs"].items():
    for k, v in cfg.items():
        r2 = [r for r in v["rows"] if r["lead_d"] == 2][0]; r15 = [r for r in v["rows"] if r["lead_d"] == 15][0]
        print(f"{name:28s} {k:28s} seg {v['segments']:5d} dr {v['drifters']:3d} | 2d rms e/n {r2['rms_e_km']:5.1f}/{r2['rms_n_km']:5.1f} med {r2['median_km']:5.1f} n {r2['n']:5d} | 15d rms {r15['rms_e_km']:5.1f}/{r15['rms_n_km']:5.1f} med {r15['median_km']:5.1f} n {r15['n']:5d} | OU e {v['ou_fit']['east']} n {v['ou_fit']['north']}")
