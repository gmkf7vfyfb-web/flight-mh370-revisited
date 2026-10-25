"""Pre-registered detection run (pre-registration v986504a4, sections 3-5). Processes every day file, saves the 100 Hz
5-40 Hz Pa series per triad (data/proc/), builds D1, M1b, C3 series, tiles the null windows, scores PW and KW,
computes p = (k+1)/(n+1) and the reported measurements. Threads only (4)."""
import sys, json, pathlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd
from obspy import read_inventory, UTCDateTime
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import ta810_common as T
WS = T.WS; (WS / "data/proc").mkdir(exist_ok=True)
inv = read_inventory(str(WS / "data/transair_H11_resp.xml")); GEO = T.element_geometry(inv)
TP = np.load(WS / "out/f35a_templates.npz")
BANK = {tri: [TP[f"env_{tri}"]] for tri in T.TRIADS}
days = sorted({p.name[:10] for p in (WS / "data/raw").glob("*.mseed")})

def series(X, tri):
    t1, d1 = T.d1_triad(X); t2, m1 = T.m1b_triad(X, BANK[tri]); t3, c3, lag = T.c3_triad(X, GEO[tri]["xy"])
    return dict(D1=(t1, d1), M1b=(t2, m1), C3=(t3, c3)), (t3, lag)

def one(args):
    day, tri = args
    t0, X, M = T.triad_block({e: str(WS / f"data/raw/{day}_{e}.mseed") for e in T.TRIADS[tri]}, inv)
    np.savez(WS / f"data/proc/{day}_{tri}.npz", t0=str(t0), mask=M, **X)
    S, (tl, lag) = series(X, tri)
    n_s = min(len(x) for x in X.values()) / T.FS
    # segments: background days whole record; event day split around 12:20-12:40
    if day == "2021-07-02":
        segs = [(0.0, UTCDateTime("2021-07-02T12:20:00") - t0), (UTCDateTime("2021-07-02T12:40:00") - t0, n_s)]
    else:
        segs = [(0.0, n_s)]
    rows = []
    for a, b in segs:
        w = a + 60.0
        while w + T.WIN <= b - 15.0:
            i0, i1 = int(w * T.FS), int((w + T.WIN) * T.FS); gapfrac = float(M[i0:i1].mean())
            r = dict(day=day, triad=tri, w_start=str(t0 + w), gapfrac=gapfrac)
            for k, (ts, s) in S.items():
                r[k], r[k + "_t"] = T.window_score(ts, s, w, w + T.WIN)
            rows.append(r); w += T.WIN
    obs = []
    if day == "2021-07-02":
        for wname, W in (("PW", T.PW), ("KW", T.KW)):
            w = W[tri] - t0; i0, i1 = int(w * T.FS), int((w + T.WIN) * T.FS)
            r = dict(triad=tri, window=wname, w_start=str(W[tri]), gapfrac=float(M[i0:i1].mean()))
            for k, (ts, s) in S.items():
                sc, tm = T.window_score(ts, s, w, w + T.WIN); r[k] = sc; r[k + "_utc"] = str(t0 + tm)
            # bearing at C3 max
            tc = r["C3_utc"]; j = int(np.argmin(np.abs(tl - (UTCDateTime(tc) - t0))))
            baz, v = T.plane_fit(lag[:, j], GEO[tri]["xy"]); r["baz_deg"] = baz; r["v_app_kms"] = v
            r["baz_expected"] = GEO[tri]["baz"]; r["dbaz"] = (baz - GEO[tri]["baz"] + 180) % 360 - 180
            # measurements (triad mean): SNR, 1-s RMS peak, instantaneous peak, exposure
            ms = np.mean([T.ms1(x) for x in X.values()], axis=0)
            s0 = int(w); s1 = int(w + T.WIN); pre = ms[max(0, s0 - 600): s0]
            k = s0 + int(np.argmax(ms[s0:s1])); r["snr_db"] = float(10 * np.log10(ms[k] / np.median(pre)))
            r["rms1s_peak_pa"] = float(np.sqrt(ms[k])); r["rms1s_peak_utc"] = str(t0 + k + 0.5)
            r["inst_peak_pa"] = float(np.mean([np.abs(x[i0:i1]).max() for x in X.values()]))
            a, b = int((k + 0.5 - 15) * T.FS), int((k + 0.5 + 15) * T.FS)
            r["exposure_5_40_pa2s"] = float(np.mean([np.sum(np.asarray(x[a:b], float) ** 2) / T.FS for x in X.values()]) - np.median(pre) * 30)
            r["noise_rms1s_median_pa"] = float(np.sqrt(np.median(pre)))
            obs.append(r)
        # keep the full event-day series for charts
        np.savez(WS / f"out/eventday_series_{tri}.npz", t0=str(t0), **{f"{k}_t": v[0] for k, v in S.items()}, **{f"{k}_s": v[1] for k, v in S.items()}, lag_t=tl, lag=lag)
    return rows, obs

jobs = [(d, tri) for d in days for tri in T.TRIADS]
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, jobs))
null = pd.DataFrame([r for rr, _ in res for r in rr]); obs = pd.DataFrame([o for _, oo in res for o in oo])
null.to_csv(WS / "out/null_window_scores.csv", index=False)
nullv = null[null.gapfrac <= 0.01]
for k in ("D1", "M1b", "C3"):
    obs[f"n_{k}"] = [int(nullv[nullv.triad == t][k].notna().sum()) for t in obs.triad]
    obs[f"p_{k}"] = [(int((nullv[nullv.triad == t][k] >= s).sum()) + 1) / (int(nullv[nullv.triad == t][k].notna().sum()) + 1) for t, s in zip(obs.triad, obs[k])]
    obs[f"rank_{k}"] = [int((nullv[nullv.triad == t][k] >= s).sum()) + 1 for t, s in zip(obs.triad, obs[k])]
    obs[f"label_{k}"] = [T.label(p) for p in obs[f"p_{k}"]]
obs["p_floor"] = 1.0 / (obs.n_M1b + 1)
obs.to_csv(WS / "out/observed_windows.csv", index=False)
print("null windows", len(null), "excluded for gaps", int((null.gapfrac > 0.01).sum()))
print(obs[["triad", "window", "D1", "p_D1", "M1b", "p_M1b", "C3", "p_C3", "baz_deg", "dbaz", "v_app_kms", "snr_db", "rms1s_peak_pa", "inst_peak_pa", "rms1s_peak_utc", "p_floor"]].round(4).to_string())
