#!/usr/bin/env python3
"""Item 7 (work order 15 Oct 2026, Task A): the dive-probability sweep by exact re-weighting.

Usage: python dive_probability_sweep.py RUN_ROOT OUT_DIR
  RUN_ROOT  e.g. mh370-exchange/end-of-flight/run-i-dive (STRATUM/seed-k/{impacts32.npy,tau90_v1.npz,run.json})

No simulation. Each impact is re-weighted by the push-over branch recorded in latent:pushover_to_surface:
2p if the push-over continued to the water, 2(1-p) if it levelled off, 1 if no push-over was drawn
(the proposal is the coin at 0.5, so the factor is identically 1 at p = 0.5 and the p = 0.5 column is
the stored sample). Impact energy and peak radiated power come from the tau90_v1.npz sidecar, joined by
row order; the impact table's own energy columns are non-finite.

Reported per 00:19 data treatment and per p: the flight-path-angle band shares, the loud-decile share
(threshold fixed at the held-out p = 0.5 90th percentile of peak radiated power), the impact-energy
quantiles, the effective impacts overall and per family, the family shares, and ln Z(p) with the
posterior mean of a global p under a U[0,1] prior (Z is affine in p, so p = 0 and p = 1 fix the curve).

CAVEAT to carry with every energy, angle and duration number from this arm: the uncontrolled-arm
dynamics are not calibrated (Boeing leave-one-out gate failed in all three rounds); they are a
labelled sensitivity on uncalibrated dynamics, not a physical prediction.
"""
import numpy as np, json, glob, os, sys

STRATA = {"next-i-waypoints": 0.9982, "next-i-free": 0.0011, "next-i-repro-radar": 0.0004, "next-i-descent-climb": 0.0002}
PGRID = [0.0, 0.25, 0.5, 0.75, 1.0]
OPTIONS = {"held out (D0 data)": None,
           "D2 R600 BTO + R600 BFO": "loglik:r600/no-offset",
           "D4 R600 BTO + both BFOs, Holland transient bias added": "loglik:both/startup-offset"}
FAMS = {1: "A1", 2: "A2", 3: "B controlled", 6: "B uncontrolled"}


def load(root):
    cols = json.load(open(f"{root}/next-i-free/seed-1/run.json"))["impact_columns"]
    ix = {c: i for i, c in enumerate(cols)}
    keep = ["parent", "weight", "flight_path_angle_deg", "family4_code",
            "latent:pushover_drawn", "latent:pushover_to_surface"] + [o for o in OPTIONS.values() if o]
    out, rng = {k: [] for k in keep + ["energy_j", "peak_w"]}, {}
    pos = 0
    for s in STRATA:
        a = pos
        for f in sorted(glob.glob(f"{root}/{s}/seed-*/impacts32.npy")):
            assert json.load(open(os.path.join(os.path.dirname(f), "run.json")))["impact_columns"] == cols, f
            arr = np.load(f, mmap_mode="r"); n = arr.shape[0]
            parts = {k: np.empty(n, np.float64 if k == "weight" else np.float32) for k in keep}
            for i in range(0, n, 500_000):
                blk = np.asarray(arr[i:i + 500_000])
                for k in keep:
                    parts[k][i:i + 500_000] = blk[:, ix[k]]
            z = np.load(f.replace("impacts32.npy", "tau90_v1.npz")); assert z["peak_rate_w"].shape[0] == n, f
            for k in keep:
                out[k].append(parts[k])
            out["energy_j"].append(z["energy_transferred_j"]); out["peak_w"].append(z["peak_rate_w"])
            pos += n
        rng[s] = (a, pos)
    return {k: np.concatenate(v) for k, v in out.items()}, rng


def main(root, outdir):
    d, rng = load(root)
    os.makedirs(outdir, exist_ok=True)
    drawn = d["latent:pushover_drawn"] == 1
    surf = d["latent:pushover_to_surface"] == 1          # NaN where no push-over was drawn; gate on `drawn`
    assert not (surf & ~drawn).any()
    w, fpa, en, pr = d["weight"], d["flight_path_angle_deg"], d["energy_j"], d["peak_w"]
    fam = d["family4_code"].astype(np.int64)

    def pooled(opt, p):
        W = np.empty(len(w)); Z = {}
        for s, prior_w in STRATA.items():
            a, b = rng[s]
            ww = w[a:b].copy()
            if opt:
                lw = d[opt][a:b].astype(np.float64)
                ww = ww * np.exp(np.where(np.isfinite(lw), lw, -np.inf))
            f = np.ones(b - a)
            f[drawn[a:b] & surf[a:b]] = 2.0 * p
            f[drawn[a:b] & ~surf[a:b]] = 2.0 * (1.0 - p)
            ww *= f
            tot = ww.sum(); Z[s] = tot / w[a:b].sum()
            W[a:b] = (ww / tot) * prior_w if tot > 0 else 0.0
        return W, float(np.log(sum(STRATA[s] * Z[s] for s in STRATA)))

    order_en = np.argsort(en, kind="stable"); en_s = en[order_en]
    order_pr = np.argsort(pr, kind="stable"); pr_s = pr[order_pr]

    def wq(order, vals, W, qs):
        c = np.cumsum(W[order]); c /= c[-1]
        return [float(vals[min(int(np.searchsorted(c, q)), len(c) - 1)]) for q in qs]

    W0, _ = pooled(None, 0.5)
    thr90 = wq(order_pr, pr_s, W0, [0.90])[0]
    loud = pr > thr90
    bands = {"lt10": fpa < 10.0, "10_45": (fpa >= 10.0) & (fpa <= 45.0), "gt45": fpa > 45.0}
    rows, ident = [], []
    for name, opt in OPTIONS.items():
        lnz = {}
        for p in sorted(set(PGRID) | {0.0, 1.0}):
            W, lz = pooled(opt, p); lnz[p] = lz
            if p not in PGRID:
                continue
            tot = W.sum(); ess = lambda v: float(v.sum() ** 2 / np.square(v).sum()) if v.sum() > 0 else 0.0
            q05, q50, q95 = wq(order_en, en_s, W, [0.05, 0.5, 0.95])
            rows.append(dict(option=name, p=p, ess=ess(W), lnZ=lz, loud_decile_share=float(W[loud].sum() / tot),
                             energy_q05_GJ=q05 / 1e9, energy_q50_GJ=q50 / 1e9, energy_q95_GJ=q95 / 1e9,
                             **{f"band_{k}": float(W[m].sum() / tot) for k, m in bands.items()},
                             **{f"share_{l}": float(W[fam == c].sum() / tot) for c, l in FAMS.items()},
                             **{f"ess_{l}": ess(W[fam == c]) for c, l in FAMS.items()}))
            print(f"{name[:26]:26s} p={p:4.2f} band10-45={rows[-1]['band_10_45']:.4f} "
                  f"loud={rows[-1]['loud_decile_share']:.4f} E50={rows[-1]['energy_q50_GJ']:6.2f}GJ "
                  f"ESS={rows[-1]['ess']:12,.0f}", flush=True)
        r = np.exp(lnz[1.0] - lnz[0.0]) - 1.0
        ident.append(dict(option=name, lnZ_p0=lnz[0.0], lnZ_p1=lnz[1.0], range_nat=lnz[1.0] - lnz[0.0],
                          posterior_mean_p=(0.5 + r / 3.0) / (1.0 + r / 2.0)))
        print(f"  ln Z range {ident[-1]['range_nat']:+.4f} nat, posterior mean p {ident[-1]['posterior_mean_p']:.3f}")
    json.dump(dict(loud_decile_threshold_W=thr90, rows=rows, identifiability=ident, n_impacts=int(len(w))),
              open(os.path.join(outdir, "sweep.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
