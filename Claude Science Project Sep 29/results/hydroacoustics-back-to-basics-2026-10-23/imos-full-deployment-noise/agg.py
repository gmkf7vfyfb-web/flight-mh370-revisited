#!/usr/bin/env python3
"""Aggregate per-day outputs of imos_deploy_noise.py into small summaries (run on deskstar).

Inputs: ~/imos-noise/out/<lg>/{rows,psd,hist}; qc.json = {lg: {"exclude_files": [...], "exclude_days_hist": [...]}}
Outputs (~/imos-noise/agg/):
  rows_all.parquet                 every record, all loggers (no QC applied; QC is in the analysis)
  spectra_<lg>.npz                 f_hz; groups (months 'YYYY-MM', 'deployment', '2014-03', 'win_20140308');
                                   rec_pct[group, pct, f]  percentiles over QC-passed records of the per-record
                                   Welch mean spectrum (dB re 1 uPa^2/Hz); rec_mean[group, f] linear mean;
                                   n_rec[group]; s1_pct[group, pct, f] percentiles of pooled 1 s levels from the
                                   daily histograms (0.5 dB bins; only days with no excluded record);
                                   n_1s[group]; rank_win_dep[f], rank_win_mar[f]: percentile rank of the
                                   8 March window median spectrum among the deployment / March per-record spectra.
"""
import glob
import os
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

W = Path.home() / "imos-noise"
OUT = W / "out"
AGG = W / "agg"
AGG.mkdir(exist_ok=True)
PCTS = [1, 5, 10, 25, 50, 75, 90, 95, 99]
WIN = (pd.Timestamp("2014-03-08T00:00Z").timestamp(), pd.Timestamp("2014-03-08T08:00Z").timestamp())
qc = json.loads(Path(sys.argv[1]).read_text())
sys.path.insert(0, str(W))
import imos_deploy_noise as D  # noqa: E402
CFG = json.loads((W / "cfg.json").read_text())
D.init_worker(CFG, str(W / "cal"))
TMP = W / "raw" / "agg_refetch"
TMP.mkdir(parents=True, exist_ok=True)
sub_log = []


def excluded_hist(lg, day, files):
    """Re-fetch excluded records of a mixed day and recompute their 1 s histogram contribution (same code)."""
    keys = {Path(k).name: (k, s) for k, s in D.s3_list(f"{D.ROOT}/{CFG[lg]['site']}/{lg}/{day}/raw/", delim="")[1]}
    tot = None
    for fn in files:
        k, s = keys[fn]
        p = D.fetch(k, s, str(TMP / fn))
        res = D.process_record(p, lg, k, s)
        os.remove(p)
        if res[2] is None:
            sub_log.append((lg, day, fn, "no hist (processing error) - not in day hist either"))
            continue
        h = res[2].astype(np.int64)
        tot = h if tot is None else tot + h
        sub_log.append((lg, day, fn, "subtracted"))
    return tot

rows_all = []
for lg in qc:
    files = sorted(glob.glob(str(OUT / lg / "rows" / "*.parquet")))
    R = pd.concat([pd.read_parquet(f).assign(day=Path(f).stem) for f in files], ignore_index=True)
    rows_all.append(R)
    excl = set(qc[lg]["exclude_files"])
    excl_days = set(qc[lg]["exclude_days_hist"])
    # per-record spectra
    S, T, F = [], [], []
    for f in sorted(glob.glob(str(OUT / lg / "psd" / "*.npz"))):
        z = np.load(f)
        keep = ~np.isin(z["files"], list(excl))
        S.append(z["psd_db"][keep, 0, :])
        T.append(z["start_utc_unix"][keep])
        F.append(z["files"][keep])
        f_hz = z["f_hz"]
    S = np.concatenate(S).astype(np.float32)
    T = np.concatenate(T)
    month = pd.to_datetime(T, unit="s").strftime("%Y-%m").values
    groups = sorted(set(month)) + ["deployment", "win_20140308"]
    sel = {g: (month == g) for g in sorted(set(month))}
    sel["deployment"] = np.ones(len(T), bool)
    sel["win_20140308"] = (T >= WIN[0]) & (T < WIN[1])
    # hist
    H = {}
    for f in sorted(glob.glob(str(OUT / lg / "hist" / "*.npz"))):
        d = Path(f).stem
        z = np.load(f)
        edges = z["edges_db"]
        C = z["counts"].astype(np.int64)
        if d in excl_days:
            dayfiles = set(R.loc[R.day == d, "file"])
            ex = sorted(dayfiles & excl)
            if len(ex) == len(dayfiles):
                sub_log.append((lg, d, "*", "day dropped (all records excluded)"))
                continue
            sub = excluded_hist(lg, d, ex)
            if sub is not None:
                C = C - sub
            assert C.min() >= 0
        H[d] = C
    centres = 0.5 * (edges[:-1] + edges[1:])

    def hist_pct(days):
        if not days:
            return np.full((len(PCTS), len(f_hz)), np.nan), 0
        C = np.sum([H[d] for d in days], axis=0).astype(np.float64)       # (f, bins)
        cum = np.cumsum(C, axis=1)
        n = cum[:, -1]
        out = np.empty((len(PCTS), C.shape[0]))
        for i, p in enumerate(PCTS):
            k = np.argmax(cum >= n[:, None] * p / 100.0, axis=1)
            out[i] = centres[k]
        return out, int(n[0])

    rec_pct = np.full((len(groups), len(PCTS), len(f_hz)), np.nan, np.float32)
    rec_mean = np.full((len(groups), len(f_hz)), np.nan, np.float32)
    s1_pct = np.full((len(groups), len(PCTS), len(f_hz)), np.nan, np.float32)
    n_rec = np.zeros(len(groups), int)
    n_1s = np.zeros(len(groups), int)
    for gi, g in enumerate(groups):
        m = sel[g]
        n_rec[gi] = m.sum()
        if m.any():
            rec_pct[gi] = np.percentile(S[m], PCTS, axis=0)
            rec_mean[gi] = 10 * np.log10(np.mean(10 ** (S[m].astype(np.float64) / 10), axis=0))
        if g == "deployment":
            days = list(H)
        elif g == "win_20140308":
            days = []
        else:
            days = [d for d in H if d[:4] + "-" + d[4:6] == g]
        s1_pct[gi], n_1s[gi] = hist_pct(days)
    wmed = np.median(S[sel["win_20140308"]], axis=0)
    rank_dep = 100 * (S < wmed).mean(axis=0)
    mar = month == "2014-03"
    rank_mar = 100 * (S[mar] < wmed).mean(axis=0)
    np.savez(AGG / f"spectra_{lg}.npz", f_hz=f_hz, groups=np.array(groups), pcts=np.array(PCTS),
             rec_pct=rec_pct, rec_mean=rec_mean, n_rec=n_rec, s1_pct=s1_pct, n_1s=n_1s,
             win_median=wmed, rank_win_dep=rank_dep, rank_win_mar=rank_mar)
    print(lg, "records", len(T), "groups", len(groups), "hist days", len(H))
pd.concat(rows_all, ignore_index=True).to_parquet(AGG / "rows_all.parquet", index=False)
pd.DataFrame(sub_log, columns=["logger", "day", "file", "action"]).to_csv(AGG / "hist_exclusion_log.csv", index=False)
print("ok")
