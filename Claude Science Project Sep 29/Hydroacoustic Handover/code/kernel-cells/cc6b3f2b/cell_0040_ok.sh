cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
cat > run_injection.py <<'EOF'
"""Test set (a) of preregistration.py: null (false-alarm) distributions of every method on real IMOS background and
injection-recovery of synthetic impact pulses (KRAKEN channel x one-pole source) at SNR -15..+10 dB.
Usage: python run_injection.py <templates_raw.npz> <out_dir> [nproc]
Outputs: null_maxima_<logger>.npz, thresholds.json, pd_vs_snr.csv, m2_pairs.csv, sr_calibration.json, summary.json"""
from __future__ import annotations
import json, sys, time, os
from pathlib import Path
from multiprocessing import Pool
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import preregistration as R, common as C, methods as M, bank as B

CTX = {}
T = None
BG = {}


def _init(tpath, ctx):
    global T, CTX
    os.environ["OMP_NUM_THREADS"] = "1"
    T = np.load(tpath)
    CTX = ctx


def _load(f):
    return C.load_100(f)


def null_one(args):
    x, L, start = args
    out = {}
    end = len(x) / R.FS
    for name, fn in M.METHODS.items():
        t, s = fn(x, R.FS, CTX)
        out[name] = M.window_maxima(t, s, start, L, end)
    _, (lev, l1, l2) = M.band_levels(x, R.FS, [R.BAND, (5, 20), (10, 40)])[0], C.band_level_1s(x)
    out["_lev"] = lev
    return out


def z_series(lev):
    med, mad = M._roll_med_mad(lev, 60)
    return (lev - med) / mad


def inj_one(args):
    xi, on, g, p, snr, tau, r = args
    x = BG_X[xi].astype(float).copy()
    i0 = int(on * R.FS)
    x[i0: i0 + len(p)] += g * p
    a, b = on - 75.0, on + 60.0
    ia, ib = max(int(a * R.FS), 0), min(int(b * R.FS), len(x))
    seg = x[ia: ib]
    off = ia / R.FS
    row = dict(snr_db=snr, tau=tau, range_km=r, file=xi, onset_s=on)
    for name, fn in M.METHODS.items():
        t, s = fn(seg, R.FS, CTX)
        row[name] = M.window_max(t + off, s, on - R.INJ_WIN[0], on + R.INJ_WIN[1])
    return row


BG_X = None


def _set_bg(xs, tpath, ctx):
    global BG_X
    _init(tpath, ctx)
    BG_X = xs


def main(tpath, out_dir, nproc=3):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    T = np.load(tpath)
    ctx = B.build(T)
    rng = np.random.default_rng(R.SEED)
    summary = dict(prereg="preregistration.py", seed=R.SEED, loaded={}, unreadable={}, n_null_windows={}, bg_median_level_db={}, seconds={})
    rows, pairs = [], []
    thresholds = {}
    # ---- load backgrounds
    X = {}
    for cid in R.FILE_STRIDE:
        files = C.bg_files(cid)
        with Pool(nproc) as pool:
            xs = pool.map(_load, files, chunksize=8)
        bad = sum(x is None for x in xs)
        X[cid] = [x for x in xs if x is not None]
        summary["loaded"][cid], summary["unreadable"][cid] = len(X[cid]), bad
        print("loaded", cid, len(X[cid]), "bad", bad, round(time.time() - t0), flush=True)
    # ---- SR calibration on the first 20 files of 3376 (pre-registered): background switch rate ~ 1 per s
    cal = []
    for k in (0.3, 1.0, 3.0):
        for sig in (0.2, 0.35, 0.5, 0.7):
            rates = []
            for x in X[3376][:20]:
                ctx2 = dict(ctx, sr_k=k, sr_sigma=sig)
                xx = np.asarray(x, float)
                import pandas as pd
                rms = pd.Series(xx ** 2).rolling(60 * R.FS, min_periods=5 * R.FS).mean().shift(1).bfill().values ** 0.5
                s = xx / np.maximum(rms, 1e-12)
                rr = np.random.default_rng(1); dt = 1 / R.FS; u = 1.0; prev = 1.0; cnt = 0
                xi = rr.standard_normal(len(s)) * np.sqrt(dt) * sig
                for n in range(len(s)):
                    u = u + dt * (u - u ** 3 + k * s[n]) + xi[n]
                    sg = 1.0 if u >= 0 else -1.0
                    cnt += sg != prev; prev = sg
                rates.append(cnt / (len(s) / R.FS))
            cal.append(dict(k=k, sigma=sig, rate=float(np.median(rates))))
    cal = pd.DataFrame(cal); best = cal.iloc[(cal.rate - 1.0).abs().argmin()]
    ctx["sr_k"], ctx["sr_sigma"] = float(best.k), float(best.sigma)
    cal.to_csv(out / "sr_calibration.csv", index=False)
    summary["sr"] = dict(k=ctx["sr_k"], sigma=ctx["sr_sigma"], rate=float(best.rate))
    print("SR", summary["sr"], flush=True)
    # ---- null per target
    LEV = {}
    for cid in R.FILE_STRIDE:
        with Pool(nproc, initializer=_init, initargs=(tpath, ctx)) as pool:
            res = pool.map(null_one, [(x, R.WINDOW_S, R.WARMUP_S) for x in X[cid]], chunksize=4)
        nm = {name: np.concatenate([r[name] for r in res]) for name in M.METHODS}
        LEV[cid] = [r["_lev"] for r in res]
        np.savez(out / f"null_maxima_{cid}.npz", **nm)
        summary["n_null_windows"][cid] = int(len(nm["M0a_stalta"]))
        thresholds[cid] = {name: {str(a): float(np.nanquantile(v, 1 - a)) for a in R.ALPHAS} for name, v in nm.items()}
        summary["bg_median_level_db"][cid] = float(np.nanmedian(np.concatenate(LEV[cid])))
        summary["seconds"][f"null_{cid}"] = round(time.time() - t0)
        print("null", cid, summary["n_null_windows"][cid], round(time.time() - t0), flush=True)
    # ---- M2 null: random 3376 x 3274 window pairs, lag search +-30 s
    Z = {cid: [z_series(l) for l in LEV[cid]] for cid in (3376, 3274)}
    def m2_stat(z1, z2, a, lag0=0.0, half=30):
        best = -np.inf
        for t in range(int(a), int(a + R.WINDOW_S)):
            if t >= len(z1) or not np.isfinite(z1[t]):
                continue
            j0 = int(t + lag0)
            seg = z2[max(j0 - half, 0): j0 + half + 1]
            seg = seg[np.isfinite(seg)]
            if len(seg):
                best = max(best, z1[t] + seg.max())
        return best
    m2null = []
    for _ in range(6000):
        z1 = Z[3376][rng.integers(len(Z[3376]))]; z2 = Z[3274][rng.integers(len(Z[3274]))]
        a = rng.uniform(R.WARMUP_S + 1, len(z1) - R.WINDOW_S - 1)
        m2null.append(m2_stat(z1, z2, a, lag0=rng.uniform(-100, 100)))
    m2null = np.array(m2null); m2null = m2null[np.isfinite(m2null)]
    np.save(out / "null_maxima_M2_pairs.npy", m2null)
    thresholds["M2_pairs"] = {str(a): float(np.quantile(m2null, 1 - a)) for a in R.ALPHAS}
    json.dump(thresholds, open(out / "thresholds.json", "w"), indent=1)
    # ---- injections
    keys = [k for k in T.files if k.startswith("h2_")]
    rgrid = np.array(sorted(float(k[3:]) for k in keys))
    rgrid = rgrid[(rgrid >= R.INJ_RANGE_KM[0]) & (rgrid <= R.INJ_RANGE_KM[1])]
    pulses = {}
    for cid in R.FILE_STRIDE:
        bmed = summary["bg_median_level_db"][cid]
        jobs = []
        for tau in R.TAUS:
            for snr in R.SNRS:
                for _ in range(R.N_INJ[cid]):
                    r = float(rng.choice(rgrid))
                    key = (r, tau)
                    if key not in pulses:
                        pulses[key] = B.pulse(T, f"h2_{r:.1f}", tau)
                    p = pulses[key]
                    _, (lev,) = M.band_levels(np.concatenate([p, np.zeros(R.FS)]), R.FS, [R.BAND])
                    base = float(np.max(lev)) - bmed
                    g = 10 ** ((snr - base) / 20)
                    xi = int(rng.integers(len(X[cid])))
                    on = float(rng.uniform(75.0, len(X[cid][xi]) / R.FS - 70.0))
                    jobs.append((xi, on, g, p, float(snr), float(tau), r))
        with Pool(nproc, initializer=_set_bg, initargs=(X[cid], tpath, ctx)) as pool:
            res = pool.map(inj_one, jobs, chunksize=8)
        for rrow in res:
            rrow["logger"] = cid
        rows.extend(res)
        summary["seconds"][f"inj_{cid}"] = round(time.time() - t0)
        print("inj", cid, len(res), round(time.time() - t0), flush=True)
        # M2 pairs (3376 primary with 3274 as the second station), same SNR both, lag0 known, +-30 s search
        if cid == 3376:
            for tau in R.TAUS:
                for snr in R.SNRS:
                    for _ in range(R.N_INJ[cid] // 2):
                        r = float(rng.choice(rgrid)); p = pulses.get((r, tau)) if (r, tau) in pulses else B.pulse(T, f"h2_{r:.1f}", tau)
                        pulses[(r, tau)] = p
                        _, (lev,) = M.band_levels(np.concatenate([p, np.zeros(R.FS)]), R.FS, [R.BAND])
                        zz = []
                        for c2 in (3376, 3274):
                            g = 10 ** ((snr - (float(np.max(lev)) - summary["bg_median_level_db"][c2])) / 20)
                            xi = int(rng.integers(len(X[c2]))); x = X[c2][xi].astype(float).copy()
                            on = 150.0; i0 = int(on * R.FS); x[i0: i0 + len(p)] += g * p
                            zz.append(z_series(C.band_level_1s(x)[0]))
                        st = m2_stat(zz[0], zz[1], on - R.INJ_WIN[0], lag0=0.0)
                        pairs.append(dict(snr_db=snr, tau=tau, range_km=r, M2_pairs=st))
    df = pd.DataFrame(rows); df.to_csv(out / "injection_scores.csv", index=False)
    pr = pd.DataFrame(pairs); pr.to_csv(out / "m2_pairs.csv", index=False)
    # ---- P_D tables
    from scipy.optimize import minimize
    pdrows, fits = [], {}
    def wilson(k, n, z=1.96):
        p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return c - h, c + h
    def fit(g):
        def nll(th):
            p = 1 / (1 + np.exp(-(g.snr_db.values - th[0]) / max(th[1], 0.05))); p = np.clip(p, 1e-9, 1 - 1e-9)
            return -np.sum(g.k * np.log(p) + (g.n - g.k) * np.log(1 - p))
        th = minimize(nll, [0.0, 3.0], method="Nelder-Mead").x
        return float(th[0]), float(th[0] + np.log(9) * max(th[1], 0.05))
    for cid, g0 in df.groupby("logger"):
        for name in M.METHODS:
            for a in R.ALPHAS:
                thr = thresholds[cid][name][str(a)]
                for tau, g1 in g0.groupby("tau"):
                    for snr, g2 in g1.groupby("snr_db"):
                        k = int((g2[name] >= thr).sum()); n = int(g2[name].notna().sum())
                        lo, hi = wilson(k, max(n, 1))
                        pdrows.append(dict(logger=cid, method=name, alpha=a, tau=tau, snr_db=snr, k=k, n=n, pd=k / max(n, 1), ci_lo=lo, ci_hi=hi, threshold=thr))
    for name in ["M2_pairs"]:
        for a in R.ALPHAS:
            thr = thresholds["M2_pairs"][str(a)]
            for tau, g1 in pr.groupby("tau"):
                for snr, g2 in g1.groupby("snr_db"):
                    k = int((g2[name] >= thr).sum()); n = int(len(g2)); lo, hi = wilson(k, n)
                    pdrows.append(dict(logger="3376+3274", method=name, alpha=a, tau=tau, snr_db=snr, k=k, n=n, pd=k / n, ci_lo=lo, ci_hi=hi, threshold=thr))
    PD = pd.DataFrame(pdrows); PD.to_csv(out / "pd_vs_snr.csv", index=False)
    for (cid, name, a, tau), g in PD.groupby(["logger", "method", "alpha", "tau"]):
        reached = bool((g.pd >= 0.5).any())
        s50, s90 = fit(g)
        fits[f"{cid}|{name}|{a}|{tau}"] = dict(snr50=s50 if reached else None, snr90=s90 if reached else None, reached=reached, pd_at_10db=float(g[g.snr_db == 10].pd.iloc[0]) if (g.snr_db == 10).any() else None)
    summary["fits"] = fits; summary["thresholds"] = thresholds; summary["seconds"]["total"] = round(time.time() - t0)
    summary["bank_keys"] = [list(k) for k in ctx["bank_keys"]]; summary["q_band"] = list(ctx["q_band"])
    json.dump(summary, open(out / "summary.json", "w"), indent=1, default=str)
    print("done", round(time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
EOF
# smoke on 6 files with reduced settings via monkeypatch (NOT evidence)
python - <<'EOF'
import sys, numpy as np, time; sys.path.insert(0,'.')
import preregistration as R, common as C, methods as M, bank as B, run_injection as RI
t0=time.time(); files=C.bg_files(3376)[:3]; xs=[C.load_100(f) for f in files]; print("load", round(time.time()-t0,2), [len(x) for x in xs])
T=np.load("../../../../../../../out/templates/templates_raw.npz"); ctx=B.build(T); ctx.update(sr_k=1.0, sr_sigma=0.5)
RI._init("../../../../../../../out/templates/templates_raw.npz", ctx)
t0=time.time(); o=RI.null_one((xs[0], 60.0, 32.0)); print("null_one", round(time.time()-t0,2), {k:(len(v), float(np.nanmax(v))) for k,v in o.items() if k!='_lev'})
RI.BG_X=xs; p=B.pulse(T,"h2_2200.0",1.0)
t0=time.time(); r=RI.inj_one((0, 150.0, 10.0, p, 0.0, 1.0, 2200.0)); print("inj_one", round(time.time()-t0,2), {k:round(v,3) for k,v in r.items() if k.startswith('M')})
EOF