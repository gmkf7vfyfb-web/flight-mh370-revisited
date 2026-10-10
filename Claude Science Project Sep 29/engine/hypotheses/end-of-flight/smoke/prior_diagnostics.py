"""Prior diagnostics of the descent envelope from one end-of-flight run (seed 1, with a dense trace).

Measures the prior (impact `weight` column, before any likelihood) on:
onset timing after the hand-off by mechanism, profile-shape shares, and level-off
statistics from `traces-dense.csv` (|vz| < 300 ft/min for >= 2 min above 500 ft).
Written for Pete's 10 Oct critique of the V2 profiles (onsets late, 10,000/4,000 ft
level-offs undersampled). Usage: python prior_diagnostics.py RUN_DIR [OUT_JSON]
"""
import json, pathlib, sys
import numpy as np, pandas as pd


def wq(x, ww, qs):
    o = np.argsort(x); c = np.cumsum(ww[o]) / ww[o].sum()
    return [round(float(x[o][min(np.searchsorted(c, q), len(o) - 1)]), 1) for q in qs]


def diagnose(run):
    run = pathlib.Path(run); sd = run / "bto-bfo/seed-1"
    m = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(m["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r"); g = lambda c: np.array(X[:, cols[c]], float)
    t0 = m["stop"]["unix_s"]; w = g("weight"); w /= w.sum()
    on = g("latent:onset_unix_s"); mech = g("latent:onset_mechanism"); sh = g("latent:profile_shape")
    pred = on + g("latent:predicted_endurance_at_onset_s")
    out = {"run": str(run), "handoff_unix_s": t0,
           "predicted_exhaustion_min_q05_50_95": wq((pred - t0) / 60, w, (0.05, 0.5, 0.95)), "onset": {}}
    for code, n in ((0, "anticipatory"), (1, "fuel_cue"), (2, "flame_out")):
        s = mech == code
        if w[s].sum() > 0:
            out["onset"][n] = {"share": round(float(w[s].sum()), 3),
                               "min_after_handoff_q05_25_50_75_95": wq((on[s] - t0) / 60, w[s], (0.05, 0.25, 0.5, 0.75, 0.95))}
    edges = np.arange(0, 181, 15)
    out["onset_hist_15min"] = np.round(np.histogram((on - t0) / 60, bins=edges, weights=w)[0], 3).tolist()
    out["shape_shares"] = {int(k): round(float(w[sh == k].sum()), 3) for k in np.unique(sh)}
    pw = g("latent:engines_thrusting_at_onset") > 0
    out["shape_shares_powered"] = {int(k): round(float(w[pw & (sh == k)].sum() / w[pw].sum()), 3) for k in np.unique(sh)}
    out["shape_codes"] = "0 continuous, 1 emergency+transition, 2 stepped, 3 best glide, 4 free trim"
    tp = run / "traces-dense.csv"
    if tp.exists():
        tr = pd.read_csv(tp, header=None, names=["it", "ilat", "ilon", "t", "alt", "vz"])
        lv = []
        for _, d in tr.groupby(["it", "ilat"]):
            a = d["alt"].to_numpy(); vz = d["vz"].to_numpy(); tt = d["t"].to_numpy()
            flat = (np.abs(vz) < 300) & (a > 500); i = 1; found = []
            while i < len(a):
                if flat[i]:
                    j = i
                    while j + 1 < len(a) and flat[j + 1]: j += 1
                    if tt[j] - tt[i] >= 120: found.append((float(np.median(a[i:j + 1])), float(tt[j] - tt[i])))
                    i = j + 1
                else: i += 1
            lv.append(found)
        n = len(lv); alts = np.array([x[0] for f in lv for x in f]); durs = np.array([x[1] for f in lv for x in f])
        near = lambda c: round(sum(1 for f in lv if any(abs(x[0] - c) <= 500 for x in f)) / n, 3)
        out["levels"] = {"traced_descents": n, "share_with_level_segment": round(sum(1 for f in lv if f) / n, 3),
                         "leveloff_alt_hist_2000ft": dict(zip(range(0, 34000, 2000), np.histogram(alts, bins=np.arange(0, 34001, 2000))[0].tolist())),
                         "share_leveloff_10000ft_pm500": near(10000), "share_leveloff_4000ft_pm500": near(4000),
                         "median_level_duration_min": round(float(np.median(durs) / 60), 1) if len(durs) else None}
    return out


if __name__ == "__main__":
    r = diagnose(sys.argv[1]); s = json.dumps(r, indent=1)
    if len(sys.argv) > 2: pathlib.Path(sys.argv[2]).write_text(s)
    print(s)
