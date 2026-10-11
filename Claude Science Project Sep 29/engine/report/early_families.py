"""Compare early-flight family runs: evidence, 00:11 / 00:19 latitude PDFs, 18:22 position,
and what each family's posterior says about its own latents (early.npy).

usage: python early_families.py <runs dir> <out dir> arm[=label] ...
Each arm is <runs dir>/<arm> written by mh370 (run.json, bto-bfo/seed-*/final.npy, routes.npy,
optional early.npy). Final rows are at the last SATCOM epoch (00:19:37); the 00:11 latitude is
read from the stored posterior routes at the 00:11:49 vertex (2,000 per seed, unweighted).
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R_NM = 3440.065
MEKAR = (6.5038889, 96.4911111)
NILAM = (6.7563889, 95.9766667)
FIX1822 = (6.5779, 96.3410)
FIRST = ["VAMPI-MEKAR-NILAM-IGOGU", "VAMPI-MEKAR-NILAM-ANOKO", "VAMPI-MEKAR-NILAM-SAMAK",
         "VAMPI-MEKAR-NILAM-NOPEK", "VAMPI-MEKAR-NILAM-LAGOG", "VAMPI-MEKAR-SAMAK"]
THEN = ["", "BEDAX", "BULVA", "ISBIX", "POSOD", "MUTMI", "PIPOV", "BEBIM"]
ROUTES = [a + ("-" + b if b else "") for a in FIRST for b in THEN]


def gc(a, b):
    la1, lo1, la2, lo2 = map(np.radians, (a[0], a[1], b[0], b[1]))
    d = 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))
    y = np.sin(lo2 - lo1) * np.cos(la2)
    x = np.cos(la1) * np.sin(la2) - np.sin(la1) * np.cos(la2) * np.cos(lo2 - lo1)
    return R_NM * d, np.arctan2(y, x)


def xtrack(p, a, b):
    """Signed cross-track (NM, + right of a->b) and along-track from a."""
    d13, t13 = gc(a, p)
    _, t12 = gc(a, b)
    xt = np.arcsin(np.sin(d13 / R_NM) * np.sin(t13 - t12)) * R_NM
    at = np.arccos(np.clip(np.cos(d13 / R_NM) / np.cos(xt / R_NM), -1, 1)) * R_NM
    return xt, at


def wq(x, w, q):
    x, w = np.asarray(x, np.float64), np.asarray(w, np.float64)
    o = np.argsort(x)
    c = np.cumsum(w[o]) / w.sum()
    return np.interp(q, c, x[o])


def kde(x, w, grid, bw):
    w = w / w.sum()
    return np.array([(w * np.exp(-0.5 * ((g - x) / bw) ** 2)).sum() for g in grid]) / (bw * np.sqrt(2 * np.pi))


def load(arm_dir):
    run = json.load(open(os.path.join(arm_dir, "run.json")))
    cols = run["final_columns"]
    seeds = sorted(d for d in os.listdir(os.path.join(arm_dir, "bto-bfo")) if d.startswith("seed-"))
    F, E, Ro = [], [], []
    for s in seeds:
        d = os.path.join(arm_dir, "bto-bfo", s)
        # float64: a float32 cumulative sum over 8 seeds x 3.5-7M rows stops short of 1 and pushes
        # the upper quantiles into the tail (run C, 10 Oct: p95 -5.5 instead of -30.0).
        f = np.load(os.path.join(d, "final.npy")).astype(np.float64)
        f[:, 0] /= f[:, 0].sum() * len(seeds)
        F.append(f)
        if os.path.exists(os.path.join(d, "early.npy")):
            E.append(np.load(os.path.join(d, "early.npy")))
        Ro.append(np.load(os.path.join(d, "routes.npy")))
    logz = [x["log_evidence"] for x in run["replicates"]]
    return run, cols, np.vstack(F), (np.vstack(E) if E else None), np.concatenate(Ro), logz, run["prior_unix_s"]


def _log_mean_exp(x):
    x = np.asarray(x, float)
    m = x.max()
    return float(m + np.log(np.mean(np.exp(x - m))))


def main():
    runs, out = sys.argv[1], sys.argv[2]
    arms = [a.split("=") if "=" in a else (a, a) for a in sys.argv[3:]]
    os.makedirs(out, exist_ok=True)
    rows, curves = [], {}
    g19, g11 = np.linspace(-41, -30, 441), np.linspace(-41, -28, 521)
    for arm, label in arms:
        d = os.path.join(runs, arm)
        if not os.path.exists(os.path.join(d, "run.json")):
            continue
        run, cols, F, E, Ro, logz, t0 = load(d)
        w = F[:, 0]
        lat = F[:, cols.index("latitude_deg")]
        k22 = int(round((1394216532.0 - 23 - t0) / 600.0))  # vertex nearest 18:21:49
        p22 = Ro[:, k22, :].astype(float)
        xt, at = xtrack((p22[:, 0], p22[:, 1]), MEKAR, NILAM)
        k11 = Ro.shape[1] - 1
        lat11 = Ro[:, k11, 0].astype(float)
        r = {"arm": arm, "label": label, "seeds": len(logz), "logZ_mean": float(np.mean(logz)),
             "logZ_seeds": " ".join(f"{z:.3f}" for z in logz),
             "lat0019_p05": wq(lat, w, .05), "lat0019_p25": wq(lat, w, .25), "lat0019_p50": wq(lat, w, .5),
             "lat0019_p75": wq(lat, w, .75), "lat0019_p95": wq(lat, w, .95),
             "lat0011_p05": np.percentile(lat11, 5), "lat0011_p50": np.percentile(lat11, 50), "lat0011_p95": np.percentile(lat11, 95),
             "xtrack_N571_1822_p50_nm": float(np.median(xt)), "xtrack_N571_1822_p05": float(np.percentile(xt, 5)),
             "xtrack_N571_1822_p95": float(np.percentile(xt, 95)), "along_from_MEKAR_1822_p50_nm": float(np.median(np.where(p22[:, 1] < MEKAR[1], at, -at))),
             "dist_fix1822_p50_nm": float(np.median(gc(FIX1822, (p22[:, 0], p22[:, 1]))[0]))}
        if E is not None:
            r["initial_mach_p50"] = wq(E[:, 13], w, .5)
            turn = E[:, 11] == 1
            r["P_turn_1822"] = float(w[turn].sum() / w.sum())
            if turn.any():
                r["turn_track_p05"], r["turn_track_p50"], r["turn_track_p95"] = (wq(E[turn, 12], w[turn], q) for q in (.05, .5, .95))
            exc = E[:, 0] == 1
            if exc.any():
                r["excursion_low_ft_p05"], r["excursion_low_ft_p50"], r["excursion_low_ft_p95"] = (wq(E[exc, 6], w[exc], q) for q in (.05, .5, .95))
                r["excursion_cas_p50"] = wq(E[exc, 10], w[exc], .5)
                r["excursion_end_ft_p50"] = wq(E[exc, 7], w[exc], .5)
                r["excursion_mean_rejections"] = float(np.average(E[exc, 14], weights=w[exc]))
            rt = E[:, 15] >= 0
            if rt.any():
                idx = E[rt, 15].astype(int)
                post = np.bincount(idx, weights=w[rt], minlength=len(ROUTES)) / w[rt].sum()
                top = np.argsort(post)[::-1][:6]
                r["routes_top"] = "; ".join(f"{ROUTES[i]} {post[i]:.3f}" for i in top if post[i] > 0)
                pd_ = os.path.join(out, f"route-posterior-{arm}.csv")
                with open(pd_, "w") as fh:
                    fh.write("index,route,posterior\n")
                    for i, n in enumerate(ROUTES):
                        fh.write(f"{i},{n},{post[i]:.6f}\n")
        rows.append(r)
        curves[label] = (kde(lat, w, g19, 0.1), kde(lat11, np.ones_like(lat11), g11, 0.1))
    # Posterior probability of each family under equal prior odds, from log of the mean
    # evidence over seeds (the pooled estimator; the mean of log Z is Jensen-biased low).
    lmz = {r["label"]: _log_mean_exp([float(v) for v in str(r["logZ_seeds"]).split()])
           for r in rows}
    top = max(lmz.values())
    pf = {k: np.exp(v - top) for k, v in lmz.items()}
    tot = sum(pf.values())
    pf = {k: v / tot for k, v in pf.items()}
    for r in rows:
        r["log_mean_Z"] = float(lmz[r["label"]])
        r["P_family_equal_prior"] = float(pf[r["label"]])
    mix19 = sum(pf[k] * curves[k][0] for k in curves)
    mix11 = sum(pf[k] * curves[k][1] for k in curves)
    with open(os.path.join(out, "early-families-mixture.json"), "w") as fh:
        json.dump({"P_family": pf, "log_mean_Z": lmz,
                   "mixture_0019_median": float(np.interp(0.5, np.cumsum(mix19) / np.sum(mix19), g19)),
                   "mixture_0011_median": float(np.interp(0.5, np.cumsum(mix11) / np.sum(mix11), g11))}, fh, indent=1)
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(out, "early-families-summary.csv"), "w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join(f"{r[k]:.4f}" if isinstance(r.get(k), float) else f"\"{r.get(k, '')}\"" if isinstance(r.get(k), str) else str(r.get(k, "")) for k in keys) + "\n")
    foot = os.environ.get("FOOTNOTE", "")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6 if foot else 4.2), constrained_layout=True)
    for label, (c19, c11) in curves.items():
        ax[0].plot(g11, c11, lw=1.3, label=f"{label} (P={pf[label]:.2f})")
        ax[1].plot(g19, c19, lw=1.3, label=f"{label} (P={pf[label]:.2f})")
    ax[0].plot(g11, mix11, lw=2.0, color="k", label="mixture, equal prior odds")
    ax[1].plot(g19, mix19, lw=2.0, color="k", label="mixture, equal prior odds")
    if foot:
        fig.get_layout_engine().set(rect=(0, 0.13, 1, 0.87))
        fig.text(0.01, 0.01, foot, fontsize=6.3, va="bottom", ha="left", wrap=True)
    ax[0].set(title="00:11:49 (posterior routes, 6th arc)", xlabel="latitude (deg)", ylabel="density (per deg)")
    ax[1].set(title="00:19:37 (final posterior, 7th arc)", xlabel="latitude (deg)")
    ax[1].legend(fontsize=7, frameon=False)
    fig.savefig(os.path.join(out, "early-families-latitude.png"), dpi=180)
    fig.savefig(os.path.join(out, "early-families-latitude.pdf"))
    json.dump(rows, open(os.path.join(out, "early-families-summary.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
