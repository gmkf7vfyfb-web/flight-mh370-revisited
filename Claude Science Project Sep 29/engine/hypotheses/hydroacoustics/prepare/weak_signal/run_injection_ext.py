"""AMENDMENT 1 (22 Oct 2026, after the pre-registered run; NOT pre-registered, disclosed): the same injection design as
run_injection.py on the SNR grid 15-30 dB (step 5), because the pre-registered grid (-15..+10 dB) ended before the
baseline detectors (M0a, M0b) and most trial methods reached P_D = 0.5, so their SNR_50 is unidentified on it (the
module's stage A met the same limit and extended likewise, imos_injection_ext.py). Same background, thresholds
(thresholds.json of the pre-registered run), templates, N_INJ; seed 20261023 (independent draws). The pre-registered
results stand as reported; logistic fits on the union are reported beside them.
Usage: python run_injection_ext.py <templates_raw.npz> <prereg_out_dir> <out_dir> [nproc]"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
from multiprocessing import Pool
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import preregistration as R, common as C, methods as M, bank as B, run_injection as RI

SNRS_EXT = (15, 20, 25, 30)
SEED_EXT = 20261023


def main(tpath, prereg_dir, out_dir, nproc=3):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    S0 = json.load(open(Path(prereg_dir) / "summary.json")); thresholds = json.load(open(Path(prereg_dir) / "thresholds.json"))
    T = np.load(tpath); ctx = B.build(T); ctx["sr_k"], ctx["sr_sigma"] = S0["sr"]["k"], S0["sr"]["sigma"]
    rng = np.random.default_rng(SEED_EXT)
    keys = [k for k in T.files if k.startswith("h2_")]
    rgrid = np.array(sorted(float(k[3:]) for k in keys)); rgrid = rgrid[(rgrid >= R.INJ_RANGE_KM[0]) & (rgrid <= R.INJ_RANGE_KM[1])]
    rows = []
    for cid in R.FILE_STRIDE:
        with Pool(nproc) as pool:
            xs = [x for x in pool.map(RI._load, C.bg_files(cid), chunksize=8) if x is not None]
        bmed = S0["bg_median_level_db"][str(cid)]
        jobs = []
        for tau in R.TAUS:
            for snr in SNRS_EXT:
                for _ in range(R.N_INJ[cid]):
                    r = float(rng.choice(rgrid)); p = B.pulse(T, f"h2_{r:.1f}", tau)
                    _, (lev,) = M.band_levels(np.concatenate([p, np.zeros(R.FS)]), R.FS, [R.BAND])
                    g = 10 ** ((snr - (float(np.max(lev)) - bmed)) / 20)
                    xi = int(rng.integers(len(xs))); on = float(rng.uniform(75.0, len(xs[xi]) / R.FS - 70.0))
                    jobs.append((xi, on, g, p, float(snr), float(tau), r))
        with Pool(nproc, initializer=RI._set_bg, initargs=(xs, tpath, ctx)) as pool:
            res = pool.map(RI.inj_one, jobs, chunksize=8)
        for rr in res:
            rr["logger"] = cid
        rows.extend(res); print("inj", cid, round(time.time() - t0), flush=True)
    df = pd.DataFrame(rows); df.to_csv(out / "injection_scores_ext.csv", index=False)
    df0 = pd.read_csv(Path(prereg_dir) / "injection_scores.csv")
    U = pd.concat([df0, df], ignore_index=True)
    def wilson(k, n, z=1.96):
        p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return c - h, c + h
    pdrows = []
    for cid, g0 in U.groupby("logger"):
        for name in M.METHODS:
            for a in R.ALPHAS:
                thr = thresholds[str(cid)][name][str(a)]
                for tau, g1 in g0.groupby("tau"):
                    for snr, g2 in g1.groupby("snr_db"):
                        k = int((g2[name] >= thr).sum()); n = int(g2[name].notna().sum()); lo, hi = wilson(k, max(n, 1))
                        pdrows.append(dict(logger=cid, method=name, alpha=a, tau=tau, snr_db=snr, k=k, n=n, pd=k / max(n, 1), ci_lo=lo, ci_hi=hi, threshold=thr, grid="prereg" if snr <= 10 else "extension"))
    PD = pd.DataFrame(pdrows); PD.to_csv(out / "pd_vs_snr_union.csv", index=False)
    from scipy.optimize import minimize
    fits = {}
    for (cid, name, a, tau), g in PD.groupby(["logger", "method", "alpha", "tau"]):
        def nll(th):
            p = 1 / (1 + np.exp(-(g.snr_db.values - th[0]) / max(th[1], 0.05))); p = np.clip(p, 1e-9, 1 - 1e-9)
            return -np.sum(g.k * np.log(p) + (g.n - g.k) * np.log(1 - p))
        th = minimize(nll, [10.0, 3.0], method="Nelder-Mead").x
        reached = bool((g.pd >= 0.5).any())
        fits[f"{cid}|{name}|{a}|{tau}"] = dict(snr50=float(th[0]) if reached else None, snr90=float(th[0] + np.log(9) * max(th[1], 0.05)) if reached else None, reached=reached, pd_max=float(g.pd.max()))
    json.dump(dict(amendment=__doc__, seed=SEED_EXT, snrs=SNRS_EXT, fits_union=fits, seconds=round(time.time() - t0)), open(out / "summary_ext.json", "w"), indent=1)
    print("done", round(time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 3)
