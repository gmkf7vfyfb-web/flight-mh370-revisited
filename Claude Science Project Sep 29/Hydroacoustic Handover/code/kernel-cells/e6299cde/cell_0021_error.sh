cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
cat > geometry.py <<'EOF'
"""Geometry products for the run J searches (work order 2026-10-21 blocks 4-5). MODEL COMPUTATION ONLY: nothing here
reads a hydrophone sample. It builds a weighted impact sample from run J and derives (1) the two-site lag
distributions used by the pre-registered coincidence rule, (2) the back-azimuth distribution at H01W used by the
Kadri Table 1 bearing test, (3) impact energy and tau summaries used by the 'coupling needed' column, and (4)
arrival-quantile checks against the windows track's windows.csv.

Sample: run-j-waypoints seeds 1-4, every 16th row (waypoints carries 0.998 of the stratum mixture, windows note
G-W4: the other strata are DECLARED omitted here), plus the northern supplement (reduced/impacts-ruleB.npz,
technique >= 1, every 8th row) at the windows track's share s_D (D0 0.125, D2 0.111, D3 0.105, D4 0.105).
Weights per option (D0', D2, D3, D4) at p = 0.5 follow run_j_windows.ln_weights / p_factor exactly (the same
re-implementation of end of flight's two-factor table); supplement rows keep lnw:comb/D* (native, p = 0.5 only).
Usage: python geometry.py <out_dir>
Outputs: sample.npz (lat, lon, t_unix, E_j, tau90_s, source, w_D0..w_D4), lags.csv, arrival_check.csv,
bearing_h01w.csv, energy.json, run.json.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run_j_windows as W

EOF_ROOT = Path("/Users/pete/Downloads/mh370-exchange/end-of-flight")
SEEDS = [1, 2, 3, 4]
STRIDE = 16
SUPP_STRIDE = 8
SUPP_SHARE = {"D0": 0.125, "D2": 0.111, "D3": 0.105, "D4": 0.105}
OPTS = ["D0", "D2", "D3", "D4"]
RX = ["H01W", "H08S", "H08N", "3315", "3376", "3274", "3275", "3250"]
PAIRS = [("H01W", "H08S"), ("3376", "3274"), ("3315", "3274"), ("3376", "3275"), ("3315", "3275"), ("3376", "3250"),
         ("3315", "3250"), ("3274", "3250"), ("3275", "3250"), ("H01W", "3376"), ("H01W", "3315"), ("H01W", "3274"),
         ("H01W", "3275"), ("H01W", "3250"), ("H08S", "3376"), ("H08S", "3315"), ("H08S", "3274"), ("H08S", "3250")]


def wq(x, w, qs):
    o = np.argsort(x); x, w = x[o], w[o]
    c = np.cumsum(w); c /= c[-1]
    return np.interp(qs, c, x)


def back_azimuth(rlat, rlon, lat, lon):
    """Initial bearing from the receiver towards the source, degrees clockwise from north (spherical)."""
    p1, p2 = np.radians(rlat), np.radians(lat); dl = np.radians(lon - rlon)
    y = np.sin(dl) * np.cos(p2); x = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    rx = W.receivers()
    lat, lon, t, E, tau, lw = [], [], [], [], [], {o: [] for o in OPTS}
    for s in SEEDS:
        sd = EOF_ROOT / "run-j" / "run-j-waypoints" / f"seed-{s}"
        g, meta, n = W.load_seed(sd)
        idx = np.arange(0, n, STRIDE)
        gs = lambda k: g(k)[idx]
        logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
        pf = np.log(W.p_factor(gs, 0.5))
        for o in OPTS:
            lw[o].append(W.ln_weights(gs, logon, o) + pf)
        lat.append(gs("latitude_deg")); lon.append(gs("longitude_deg")); t.append(gs("unix_s"))
        E.append(gs("latent:impact_energy_transferred_j")); tau.append(gs("latent:energy_transfer_tau90_s"))
        print("seed", s, n, round(time.time() - t0), flush=True)
    lat, lon, t, E, tau = map(np.concatenate, (lat, lon, t, E, tau))
    w = {}
    for o in OPTS:
        l = np.concatenate(lw[o]); l = l - np.nanmax(l[np.isfinite(l)]); x = np.exp(np.where(np.isfinite(l), l, -np.inf)); w[o] = x / x.sum()
    z = np.load(EOF_ROOT / "run-j-supplement" / "reduced" / "impacts-ruleB.npz")
    m = z["technique"] >= 1; ii = np.where(m)[0][::SUPP_STRIDE]
    slat, slon, st = z["latitude_deg"][ii].astype(float), z["longitude_deg"][ii].astype(float), z["t_impact_s"][ii].astype(float) + W.T0
    sE = z["latent:impact_energy_transferred_j"][ii].astype(float); stau = np.full(len(ii), np.nan)
    sw = {}
    for o in OPTS:
        l = z[f"lnw:comb/{o}"][ii].astype(float); l = l - np.nanmax(l[np.isfinite(l)]); x = np.exp(np.where(np.isfinite(l), l, -np.inf)); sw[o] = x / x.sum()
    LAT = np.concatenate([lat, slat]); LON = np.concatenate([lon, slon]); T = np.concatenate([t, st]); EE = np.concatenate([E, sE]); TAU = np.concatenate([tau, stau])
    WW = {o: np.concatenate([(1 - SUPP_SHARE[o]) * w[o], SUPP_SHARE[o] * sw[o]]) for o in OPTS}
    src = np.concatenate([np.zeros(len(lat), np.int8), np.ones(len(slat), np.int8)])
    np.savez_compressed(out / "sample.npz", lat=LAT, lon=LON, t_unix=T, E_j=EE, tau90_s=TAU, source=src, **{f"w_{o}": WW[o] for o in OPTS})
    d = {r: W.geodesic_km(LAT, LON, rx[r][0], rx[r][1]) for r in RX}
    rows = []
    qs = [0.005, 0.025, 0.05, 0.5, 0.95, 0.975, 0.995]
    for a, b in PAIRS:
        for o in OPTS:
            lag = (d[b] - d[a]) / 1.482
            q = wq(lag, WW[o], qs)
            rows.append(dict(rx_a=a, rx_b=b, option=o, **{f"q{x*100:g}": float(v) for x, v in zip(qs, q)}, ess=float(WW[o].sum() ** 2 / np.sum(WW[o] ** 2))))
    pd.DataFrame(rows).to_csv(out / "lags.csv", index=False)
    arr = []
    for r in RX:
        for o in OPTS:
            q = wq(T + d[r] / 1.482, WW[o], [0.005, 0.05, 0.5, 0.95, 0.995])
            arr.append(dict(receiver=r, option=o, **{k: W.hms(v) for k, v in zip(["q0.5", "q5", "q50", "q95", "q99.5"], q)}))
    pd.DataFrame(arr).to_csv(out / "arrival_check.csv", index=False)
    baz = back_azimuth(rx["H01W"][0], rx["H01W"][1], LAT, LON)
    edges = np.arange(180.0, 360.01, 0.5)
    hb = {o: np.histogram(baz, bins=edges, weights=WW[o])[0] for o in OPTS}
    pd.DataFrame({"baz_lo": edges[:-1], "baz_hi": edges[1:], **{f"mass_{o}": hb[o] for o in OPTS}}).to_csv(out / "bearing_h01w.csv", index=False)
    en = {}
    for o in OPTS:
        mt = np.isfinite(TAU)
        en[o] = dict(E_j_q=dict(zip(["q5", "q25", "q50", "q75", "q95"], map(float, wq(EE, WW[o], [0.05, 0.25, 0.5, 0.75, 0.95])))),
                     lat_q=dict(zip(["q0.5", "q5", "q50", "q95", "q99.5"], map(float, wq(LAT, WW[o], [0.005, 0.05, 0.5, 0.95, 0.995])))),
                     t_impact_q=dict(zip(["q0.5", "q5", "q25", "q50", "q75", "q95", "q99.5"], [W.hms(v) for v in wq(T, WW[o], [0.005, 0.05, 0.25, 0.5, 0.75, 0.95, 0.995])])),
                     t_impact_unix_q=dict(zip(["q0.5", "q5", "q25", "q50", "q75", "q95", "q99.5"], map(float, wq(T, WW[o], [0.005, 0.05, 0.25, 0.5, 0.75, 0.95, 0.995])))),
                     tau90_s_q=dict(zip(["q5", "q50", "q95"], map(float, wq(TAU[mt], WW[o][mt] / WW[o][mt].sum(), [0.05, 0.5, 0.95])))),
                     ess=float(WW[o].sum() ** 2 / np.sum(WW[o] ** 2)))
    (out / "energy.json").write_text(json.dumps(en, indent=1))
    (out / "run.json").write_text(json.dumps(dict(seeds=SEEDS, stride=STRIDE, supp_stride=SUPP_STRIDE, n_strata_rows=int(len(lat)), n_supp_rows=int(len(slat)),
                                                  supp_share=SUPP_SHARE, receivers=rx, c_km_s=1.482, wall_s=round(time.time() - t0, 1),
                                                  note="waypoints stratum only (0.998 of mixture; G-W4); supplement native weights at p=0.5"), indent=1, default=str))
    print("done", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python geometry.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry 2>&1 | tail -8
cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry && cat arrival_check.csv | head -9 && head -5 lags.csv && python -c "import json;e=json.load(open('energy.json'));print({o:(e[o]['E_j_q']['q50'],e[o]['tau90_s_q'],e[o]['t_impact_q']['q50'],e[o]['lat_q'],round(e[o]['ess'])) for o in e})"