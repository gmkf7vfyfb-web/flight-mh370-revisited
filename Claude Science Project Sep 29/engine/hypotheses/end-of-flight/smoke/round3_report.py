"""Item 8 (Task B) report: rule-11 before/after for the round-3 sensitivity arm, and the distributions this arm
exists to make quotable (impact energy, flight-path angle, energy-transfer duration) as a LABELLED SENSITIVITY.

Usage: python round3_report.py R3_SUMMARY_DIR PRODUCTION_SUMMARY_DIR OUT_JSON
  R3_SUMMARY_DIR          r3/arm/summary (per-stratum tables + subsample-*.npz, produced by sweep_round3.sh)
  PRODUCTION_SUMMARY_DIR  mh370-exchange/end-of-flight/run-i-dive/summary (the "before")

Caveat carried by every energy, angle and duration number below: the uncontrolled-arm dynamics are not calibrated;
the Boeing leave-one-out gate failed in all three rounds. These are a labelled sensitivity, not a prediction.
"""
import sys, json, glob, pathlib
import numpy as np
from scipy.special import logsumexp

STRATA = {"next-i-waypoints": 0.9982, "next-i-free": 0.0011, "next-i-repro-radar": 0.0004, "next-i-descent-climb": 0.0002}
CELLS = ["D0 total q=0.333 (C2 silent)", "D1 total q=0.333 (C2 silent)", "D2 total q=0.333 (C2 silent)",
         "D3 total q=0.333 (C2 silent)", "D4 total q=0.333 (C2 silent)", "D5 total q=0.333 (C2 silent)",
         "D0xC1", "D4xC1", "D4xC2 silent"]


def mixture(sdir, weights):
    tabs = {}
    for st, P in weights.items():
        f = pathlib.Path(sdir) / f"table-0019-{st}.json"
        if f.exists():
            tabs[st] = json.load(open(f))
    out = {}
    for c in set().union(*[set(t["cells"]) for t in tabs.values()]):
        lz = [np.log(weights[st]) + t["cells"][c]["ln_Z"] for st, t in tabs.items() if c in t["cells"]]
        l2 = [2 * (np.log(weights[st]) + t["cells"][c]["ln_Z"]) - np.log(t["cells"][c]["eff_impacts"])
              for st, t in tabs.items() if c in t["cells"] and t["cells"][c]["eff_impacts"] > 0]
        Z = float(logsumexp(lz))
        h, lat = None, None
        for st, t in tabs.items():
            p = pathlib.Path(sdir) / f"table-0019-{st}-latitude.npz"
            key = c.replace(" ", "_").replace("=", "").replace("(", "").replace(")", "").replace("/", "_")
            if p.exists() and c in t["cells"]:
                z = np.load(p)
                if key in z.files:
                    v = z[key] * np.exp(np.log(weights[st]) + t["cells"][c]["ln_Z"] - Z)
                    h = v if h is None else h + v
                    lat = z["lat"]
        q = None
        if h is not None and h.sum() > 0:
            hc = np.cumsum(h); hc /= hc[-1]
            q = [float(lat[np.searchsorted(hc, x)]) for x in (0.05, 0.5, 0.95)]
        fam = {}
        for n in ("A1", "A2", "B"):
            f1 = [np.log(weights[st]) + t["cells"][c]["ln_Z"] + np.log(max(t["cells"][c]["families"][n]["share"], 1e-300))
                  for st, t in tabs.items() if c in t["cells"]]
            fam[n] = float(np.exp(logsumexp(f1) - Z))
        out[c] = {"ln_Z": Z, "eff_impacts": float(np.exp(2 * Z - logsumexp(l2))), "latitude_q05_q50_q95": q,
                  "family_shares": fam,
                  "per_stratum_ln_Z": {st: t["cells"][c]["ln_Z"] for st, t in tabs.items() if c in t["cells"]}}
    return out, sorted(tabs)


def wq(v, w, qs):
    o = np.argsort(v, kind="stable"); c = np.cumsum(w[o]); c /= c[-1]
    return [float(v[o][min(int(np.searchsorted(c, q)), len(c) - 1)]) for q in qs]


def distributions(sdir):
    """Weighted distributions of the sensitivity fields, from the per-stratum subsamples."""
    out = {}
    for st, P in STRATA.items():
        f = pathlib.Path(sdir) / f"subsample-{st}.npz"
        if not f.exists():
            continue
        z = np.load(f, allow_pickle=True)
        cols = list(z["columns"]); R = z["rows"]
        ix = {c: i for i, c in enumerate(cols)}
        w = R[:, ix["weight"]].astype(np.float64)
        out[st] = {"P": P, "n": int(len(w)),
                   "energy_GJ_q05_q50_q95": [x / 1e9 for x in wq(R[:, ix["energy_transferred_j"]], w, [0.05, 0.5, 0.95])],
                   "fpa_deg_q05_q50_q95": wq(R[:, ix["flight_path_angle_deg"]], w, [0.05, 0.5, 0.95]),
                   "tau90_s_q05_q50_q95": wq(R[:, ix["tau90_s"]], w, [0.05, 0.5, 0.95]),
                   "peak_W_q50_q90": wq(R[:, ix["peak_rate_w"]], w, [0.5, 0.9]),
                   "band_10_45_share": float(w[(R[:, ix["flight_path_angle_deg"]] >= 10) &
                                               (R[:, ix["flight_path_angle_deg"]] <= 45)].sum() / w.sum()),
                   "dive_share_of_drawn": float(w[(R[:, ix["latent:pushover_to_surface"]] == 1)].sum() /
                                                max(w[(R[:, ix["latent:pushover_drawn"]] == 1)].sum(), 1e-300))}
    return out


def main(r3, prod, outp):
    new, strata_done = mixture(r3, {k: v for k, v in STRATA.items() if (pathlib.Path(r3) / f"table-0019-{k}.json").exists()})
    old, _ = mixture(prod, STRATA)
    res = {"strata_in_round3_arm": strata_done, "rule11": {}, "distributions_round3": distributions(r3)}
    for c in CELLS:
        if c in new and c in old:
            a, b = old[c], new[c]
            res["rule11"][c] = {
                "ln_Z_before": a["ln_Z"], "ln_Z_after": b["ln_Z"], "d_ln_Z": b["ln_Z"] - a["ln_Z"],
                "lat_median_before": a["latitude_q05_q50_q95"][1] if a["latitude_q05_q50_q95"] else None,
                "lat_median_after": b["latitude_q05_q50_q95"][1] if b["latitude_q05_q50_q95"] else None,
                "lat_q05_q95_before": [a["latitude_q05_q50_q95"][0], a["latitude_q05_q50_q95"][2]] if a["latitude_q05_q50_q95"] else None,
                "lat_q05_q95_after": [b["latitude_q05_q50_q95"][0], b["latitude_q05_q50_q95"][2]] if b["latitude_q05_q50_q95"] else None,
                "eff_before": a["eff_impacts"], "eff_after": b["eff_impacts"],
                "family_shares_before": a["family_shares"], "family_shares_after": b["family_shares"]}
    json.dump(res, open(outp, "w"), indent=1)
    print(f"{'cell':32s} {'lnZ before':>11s} {'lnZ after':>10s} {'d lnZ':>8s} {'lat med before':>14s} {'after':>8s}")
    for c, v in res["rule11"].items():
        print(f"{c:32s} {v['ln_Z_before']:11.3f} {v['ln_Z_after']:10.3f} {v['d_ln_Z']:+8.3f} "
              f"{v['lat_median_before']:14.2f} {v['lat_median_after']:8.2f}")
    d = res["rule11"].get("D0 total q=0.333 (C2 silent)")
    if d:
        print(f"\nSTOP CONDITION (held-out log evidence moves by more than 1 nat): d lnZ = {d['d_ln_Z']:+.3f} nat -> "
              f"{'TRIPPED, STOP AND REPORT' if abs(d['d_ln_Z']) > 1 else 'not tripped'}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
