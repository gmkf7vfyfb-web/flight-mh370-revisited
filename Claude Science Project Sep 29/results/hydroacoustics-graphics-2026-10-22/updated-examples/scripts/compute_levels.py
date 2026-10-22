"""Corrected-IMOS levels for the updated example charts (graphics track, 22 Oct 2026).
Reruns the pre-registered run_j_levels.py chain (prereg 4277320, amendment 2: IMOS TL = imos_tl_ram_arc.csv) on the
existing 2 M-draw subsamples for D0/D2/D3/D4 at p = 0.5, all eight receivers. No rule changed; this only adds keys
D2-D4 to the amendment-2 rerun (which covered D0/p0.5, IMOS loggers) so that the maps and the per-band distributions
use the corrected IMOS table. Writes compact npz/csv for plotting."""
import sys, json, pathlib, numpy as np, pandas as pd
P = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(P))
import run_j_levels as RL
RL.IMOS_TL_FILE = "imos_tl_ram_arc.csv"
EX = pathlib.Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels")
EOF = "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j"
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
tau_grid, Sb = RL.chain_tables(); xs, tl = RL.tl_tables(); nz = RL.noise_medians()
teff = json.loads((RL.RD / "stageB/pd_samples_summary.json").read_text())["t_eff_s"]["T_C2"]
gain = {r: (RL.TRIAD_GAIN_DB if r in RL.IMS else 0.0) for r in RL.RECEIVERS}
EDGES = np.arange(-60.0, 200.0 + 1e-9, 0.25)
ETAS = [1e-2, 1e-3, 2.1e-4, 1e-4, 1e-5, 1e-6]
rows_det, rows_best, store = [], [], {}
for opt in ["D0", "D2", "D3", "D4"]:
    key = f"{opt}/p0.5"; D, w, info = RL.load_key(EX, key, EOF); n = len(w)
    tau_ac = np.clip(D["tau90"].astype(np.float64), RL.TAU_LO, RL.TAU_HI)
    S = np.full((n, len(RL.RECEIVERS)), -np.inf)
    for i, rec in enumerate(RL.RECEIVERS):
        Lb = RL.levels_eta1(D["lat"], D["E"], tau_ac, xs, tl[rec], tau_grid, Sb, teff)
        with np.errstate(divide="ignore"):
            L = 10 * np.log10(np.sum(10 ** (Lb / 10), axis=1))
        s = L + gain[rec] - nz[rec]; S[:, i] = s; fin = np.isfinite(s)
        if opt == "D0":
            for j, fc in enumerate(RL.BANDS):
                fb = np.isfinite(Lb[:, j])
                store[f"{rec}/band{fc:g}"] = np.histogram(np.clip(Lb[fb, j], EDGES[0], EDGES[-1]), bins=EDGES, weights=w[fb])[0]
                store[f"{rec}/band{fc:g}_blocked"] = np.array(float(w[~fb].sum()))
            store[f"{rec}/total"] = np.histogram(np.clip(L[fin], EDGES[0], EDGES[-1]), bins=EDGES, weights=w[fin])[0]
        for eta in ETAS:
            sh = 10 * np.log10(eta)
            r = dict(key=key, receiver=rec, eta=eta, blocked_mass=float(w[~fin].sum()), noise_median_db=nz[rec], gain_db=gain[rec],
                     frac_matched_filter=float(w[fin][(s[fin] + sh) >= 7].sum()), frac_baseline=float(w[fin][(s[fin] + sh) >= 15].sum()))
            if fin.any():
                q = RL.wquant(L[fin], w[fin], [0.1, 0.5, 0.9]); r.update(level_q10=q[0] + sh, level_q50=q[1] + sh, level_q90=q[2] + sh)
            rows_det.append(r)
    Sf = np.where(np.isfinite(S), S, -np.inf); best = np.argmax(Sf, axis=1); sb = Sf[np.arange(n), best]; fin = np.isfinite(sb)
    for eta in ETAS:
        sh = 10 * np.log10(eta)
        rows_best.append(dict(key=key, eta=eta, frac_matched_filter=float(w[fin][(sb[fin] + sh) >= 7].sum()), frac_baseline=float(w[fin][(sb[fin] + sh) >= 15].sum()),
                              **{f"share_best_{r}": float(w[best == i].sum()) for i, r in enumerate(RL.RECEIVERS)}, kish_ess=info["kish_ess"], n=n))
    rng = np.random.default_rng([20261022, 99, ["D0", "D2", "D3", "D4"].index(opt)])
    keep = rng.choice(n, 150_000, replace=False, p=w / w.sum())   # weight-proportional thinning: dots are draws from the posterior
    np.savez_compressed(OUT / f"map_{opt}.npz", lat=D["lat"][keep], lon=D["lon"][keep], snr_best_eta1=sb[keep].astype(np.float32), best=best[keep].astype(np.int8))
    print(key, n, round(info["kish_ess"]), flush=True)
np.savez_compressed(OUT / "band_hist_D0_p0.5.npz", edges=EDGES, **store)
pd.DataFrame(rows_det).to_csv(OUT / "detectable_corrected.csv", index=False)
pd.DataFrame(rows_best).to_csv(OUT / "best_receiver_corrected.csv", index=False)
