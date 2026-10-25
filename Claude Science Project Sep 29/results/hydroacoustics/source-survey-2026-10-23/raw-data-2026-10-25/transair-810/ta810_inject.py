"""Measured detection probability (pre-registration v986504a4 s6). F-35A raw-record waveform (same triad, 5-40 Hz,
100 Hz, [pk-35, pk+15] s) scaled to a triad-mean 1-s RMS peak L, injected into all three elements with plane-wave
delays for the Transair back-azimuth at 1.482 km/s, energy peak uniform inside a 90 s background window (14 adjacent
days only). Statistics recomputed on [w-65 s, w+110 s]; score = max in the window; p against the section-4 null.
Extra levels: Kadri's reading (signal instantaneous peak 0.40-0.45 Pa, midpoint 0.425 Pa) for the LR."""
import sys, json, pathlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd
from obspy import read_inventory, UTCDateTime
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import ta810_common as T
WS = T.WS; rng = np.random.default_rng(20261025)
inv = read_inventory(str(WS / "data/transair_H11_resp.xml")); GEO = T.element_geometry(inv)
TP = np.load(WS / "out/f35a_templates.npz"); META = json.load(open(WS / "out/f35a_templates.json"))["meta"]
null = pd.read_csv(WS / "out/null_window_scores.csv"); null = null[null.gapfrac <= 0.01]
NULLS = {(tri, k): np.sort(null[null.triad == tri][k].dropna().values) for tri in T.TRIADS for k in ("D1", "M1b", "C3")}
def pval(tri, k, s):
    a = NULLS[(tri, k)]; return (len(a) - np.searchsorted(a, s, side="left") + 1) / (len(a) + 1)
bg = null[(null.day != "2021-07-02")].copy()
tod = pd.to_datetime(bg.w_start).dt.strftime("%H:%M:%S")
bg = bg[(tod >= "11:31:10") & (tod <= "13:28:00")]   # room for the 65 s lead-in and 20 s tail (declared)
PROC = {}
def proc(day, tri):
    if (day, tri) not in PROC:
        z = np.load(WS / f"data/proc/{day}_{tri}.npz"); PROC[(day, tri)] = (UTCDateTime(str(z["t0"])), {e: z[e].astype(float) for e in T.TRIADS[tri]})
    return PROC[(day, tri)]
LEV = list(np.logspace(np.log10(0.003), np.log10(0.3), 16))
KAD = {tri: 0.425 / (META[tri]["wave_inst_peak"] / META[tri]["wave_rms_peak"]) for tri in T.TRIADS}
N = 150
jobs = []
for tri in T.TRIADS:
    rows = bg[bg.triad == tri].reset_index(drop=True)
    for li, L in enumerate(LEV + [KAD[tri], 0.0]):
        for n in range(N):
            r = rows.iloc[int(rng.integers(len(rows)))]
            jobs.append(dict(tri=tri, level=float(L), kind=("kadri" if li == len(LEV) else ("zero" if li == len(LEV) + 1 else "grid")),
                             day=r.day, w_start=r.w_start, pk_off=float(rng.uniform(0, T.WIN))))
for tri in T.TRIADS:
    for d in sorted(bg.day.unique()):
        proc(d, tri)
def one(j):
    tri = j["tri"]; t0, X = proc(j["day"], tri); w = UTCDateTime(j["w_start"]) - t0
    a = int((w - 65) * T.FS); b = int((w + T.WIN + 20) * T.FS)
    wave = TP[f"wave_{tri}"].astype(float) * (j["level"] / META[tri]["wave_rms_peak"])
    dl = T.plane_wave_delays(GEO[tri]["xy"], GEO[tri]["baz"])
    Y = {}
    for e in T.TRIADS[tri]:
        y = X[e][a:b].copy()
        s0 = int(round((65 + j["pk_off"] - 35 + dl[e]) * T.FS))
        y[s0: s0 + len(wave)] += wave[: max(0, min(len(wave), len(y) - s0))]
        Y[e] = y.astype(np.float32)
    t1, d1 = T.d1_triad(Y); t2, m1 = T.m1b_triad(Y, [TP[f"env_{tri}"]]); t3, c3, lag = T.c3_triad(Y, GEO[tri]["xy"])
    out = dict(j)
    for k, (ts, s) in (("D1", (t1, d1)), ("M1b", (t2, m1)), ("C3", (t3, c3))):
        sc, tm = T.window_score(ts, s, 65, 65 + T.WIN); out[k] = sc; out["p_" + k] = pval(tri, k, sc); out[k + "_dt"] = tm - (65 + j["pk_off"])
    jj = int(np.argmin(np.abs(t3 - (out["C3_dt"] + 65 + j["pk_off"]))))
    baz, v = T.plane_fit(lag[:, jj], GEO[tri]["xy"]); out["baz"] = baz; out["v"] = v
    out["bearing_ok"] = bool(abs((baz - GEO[tri]["baz"] + 180) % 360 - 180) <= 10 and 1.35 <= v <= 1.65)
    return out
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, jobs))
R = pd.DataFrame(res); R.to_csv(WS / "out/injection_results.csv", index=False)
json.dump(dict(levels=LEV, kadri_level_rms_pa=KAD, n_per_level=N), open(WS / "out/injection_meta.json", "w"), indent=1)
g = R.groupby(["tri", "kind", "level"]).agg(pd_report=("p_M1b", lambda p: float((p < 0.05).mean())), pd_mark=("p_M1b", lambda p: float((p < 0.1).mean())),
                                            pd_screen=("p_M1b", lambda p: float((p < 0.3).mean())), pd_D1_report=("p_D1", lambda p: float((p < 0.05).mean())),
                                            pd_C3_report_bearing=("p_C3", lambda p: 0.0), n=("p_M1b", "size")).reset_index()
g["pd_C3_report_bearing"] = R.groupby(["tri", "kind", "level"]).apply(lambda d: float(((d.p_C3 < 0.05) & d.bearing_ok).mean())).values
print(g.round(3).to_string())
