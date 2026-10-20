"""Latitude histograms (impact) per replicate and pooled, for figure 1 of the smoke note. Usage: hist_case.py CASE_DIR"""
import sys, json, glob, pathlib
import numpy as np
from scipy.special import logsumexp
cd = sys.argv[1]; T = json.load(open(f"{cd}/truth.json")); E = np.arange(-45.0, 30.01, 0.25)
files = sorted(glob.glob(f"{cd}/rows-seed-*.npz")); out = {"edges": E.tolist(), "truth_lat": T["impact"]["lat"], "cells": {}}
R = [np.load(f) for f in files]
for d in ("D0", "D1", "D3", "D4"):
    for st in ("core", "all"):
        per, pooled_a, lats = [], [], []
        for r in R:
            a = r["base"] + r[f"D_{d}"]
            if st == "all":
                ld = r["ld"]; ok = np.isfinite(a) & np.isfinite(ld); wv = np.exp(a - a[np.isfinite(a)].max()); wv[~np.isfinite(a)] = 0
                fill = logsumexp(ld[ok], b=wv[ok]) - np.log(wv[ok].sum()) if ok.any() else 0.0
                a = a + np.where(np.isfinite(ld), ld, fill) + r["ls"]
            ok = np.isfinite(a); w = np.exp(a - a[ok].max()); w[~ok] = 0
            per.append((np.histogram(r["lat"], E, weights=w / w.sum())[0]).tolist()); pooled_a.append(a - np.log(len(R))); lats.append(r["lat"])
        a = np.concatenate(pooled_a); ok = np.isfinite(a); w = np.exp(a - a[ok].max()); w[~ok] = 0
        out["cells"][f"{d}|{st}"] = {"per_seed": per, "pooled": (np.histogram(np.concatenate(lats), E, weights=w / w.sum())[0]).tolist()}
json.dump(out, open(f"{cd}/hist.json", "w"))
print("ok", len(files))
