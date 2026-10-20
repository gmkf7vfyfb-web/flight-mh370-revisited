"""Run J northern supplement, step 1: what the 00:11 hand-offs and filter populations hold, per family, mode and band of
00:11 latitude. Hand-off rows (100k per seed, look-ahead corrected), distinct particle indices, distinct states, Kish ESS
of the corrected row weights; and from diagnostics.json the population size, ESS after the 00:11 update and the distinct
parents of the 00:11 resample per mode."""
import json, pathlib, sys, numpy as np
X = pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/run-j")
FAM = {"run-j-waypoints": 0.9982, "run-j-free": 0.0013, "run-j-repro-radar": 0.0003, "run-j-descent-climb": 0.0002}
EDGES = np.arange(-45, -9, 1.0)
BANDS = [(-35, -30), (-30, -25), (-25, -20), (-40, -35), (-20, -15)]
MODES = ["TrueHeading", "MagneticHeading", "TrueTrack", "MagneticTrack", "LateralNavigation"]
out = {}
for fam, PF in FAM.items():
    seeds = sorted((X / fam / "bto-bfo").glob("seed-*"), key=lambda p: int(p.name[5:]))
    T = {}
    hist = np.zeros((5, len(EDGES) - 1))
    for sd in seeds:
        H = np.load(sd / "handoff-m0011" / "handoff.npy"); d = json.load(open(sd / "diagnostics.json"))
        w = H[:, 0] * np.exp(H[:, 13]); lat = H[:, 1]; mode = H[:, 6].astype(int); part = H[:, 12].astype(np.int64)
        for md in range(5):
            s = mode == md
            hist[md] += np.histogram(lat[s], EDGES, weights=w[s])[0] / len(seeds)
            mr = d["modes"][md]; e = [x for x in mr["epochs"] if x["epoch"] == "m0011"][0]
            for (lo, hi) in BANDS + [(-90, 90)]:
                b = s & (lat >= lo) & (lat < hi); key = (md, f"{-hi}-{-lo} S" if lo > -90 else "all")
                t = T.setdefault(key, {"rows": 0, "distinct_particles": 0, "distinct_states": 0, "mass": 0.0, "w2": 0.0, "seeds_with_rows": 0,
                                        "pop_n": 0, "pop_ess_0011": 0.0, "pop_distinct_parents_0011": 0})
                t["rows"] += int(b.sum()); t["distinct_particles"] += len(np.unique(part[b]))
                t["distinct_states"] += len(np.unique(H[b][:, [1, 2, 3, 8]], axis=0)) if b.any() else 0
                t["mass"] += float(w[b].sum()) / len(seeds); t["w2"] += float((w[b] ** 2).sum()) / len(seeds) ** 2
                t["seeds_with_rows"] += int(b.any())
                if key[1] == "all":
                    t["pop_n"] += int(d["particles_per_mode"][md]); t["pop_ess_0011"] += e["ess_after_update"]
                    t["pop_distinct_parents_0011"] += int(e["distinct_parents"] or 0)
    for t in T.values(): t["kish_ess_rows"] = t["mass"] ** 2 / t["w2"] if t["w2"] > 0 else 0.0
    out[fam] = {"seeds": len(seeds), "P_family": PF, "cells": {f"{MODES[k[0]]}|{k[1]}": v for k, v in T.items()},
                "lat_hist_0011_by_mode": hist.tolist(), "edges": EDGES.tolist()}
json.dump(out, open("core_handoff_measure.json", "w"), indent=1)
for fam in out:
    print(fam, out[fam]["seeds"])
    for k, v in out[fam]["cells"].items():
        if k.endswith("all") or "35-30" in k or "30-25" in k or "25-20" in k:
            print(f"  {k:32s} rows {v['rows']:8d} dpart {v['distinct_particles']:8d} dstate {v['distinct_states']:8d} mass {v['mass']:.4f} kish {v['kish_ess_rows']:9.0f}" + (f" pop {v['pop_n']} popESS {v['pop_ess_0011']:.0f} popDP {v['pop_distinct_parents_0011']}" if k.endswith('all') else ''))
