"""Merge a rank.py re-run (raw tables) into the committed 22 Oct ranked tables (overnight 23 Oct 2026, X03).

The committed tables (results-data/ranked_candidates = exchange graphics-2026-10-22/ranked) were written by the interactive session;
rank.py is its consolidated form and writes *_raw.csv without the descriptive columns. A rank.py re-run with the 22 Oct settings
reproduces every committed finite ln LR exactly (max |d| 0.0; singles 115, pairs 713, triples 1,201; -inf pattern identical) on the
join keys below. This script keeps every committed column and replaces only the prior-dependent ones from the re-run:
  lnLR, lnLR_D2/D3/D4 (lnN_Dx - lnB), lnLR_pB (lnN - lnB_pB), lnLR_no_bearing, ln_f_amp_given_time (lnN - ln_ftime), eta_post_med,
  rank_lnLR (descending lnLR; ties by plain p as before), and restates eta_x_F35A / eta_level_x_F35A on 2.26e-3 (X02).
Prior-independent columns (eta_needed, eta_pd50_all_a005, eta_level_locus, loci, implied times) are kept and checked equal.
Usage: python merge_rerank.py <committed_dir> <raw_dir> <out_dir> <label>
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

KEYS = {"ranked_singles": ["rx", "time_utc", "det", "band", "p"],
        "ranked_pairs": ["rx_a", "t_a", "det_a", "band_a", "p_a", "rx_b", "t_b", "det_b", "band_b", "p_b", "family"],
        "ranked_triples": ["cids"]}
ETA_F35A = 2.26e-3


def main(cdir, rdir, out, label):
    cdir, rdir, out = Path(cdir), Path(rdir), Path(out); out.mkdir(parents=True, exist_ok=True); rep = {"label": label}
    for n, keys in KEYS.items():
        a = pd.read_csv(cdir / f"{n}.csv", low_memory=False); b = pd.read_csv(rdir / f"{n}_raw.csv", low_memory=False)
        a["_ord"] = np.arange(len(a))
        for k in keys: a[k] = a[k].astype(str); b[k] = b[k].astype(str)
        assert not a.duplicated(keys).any() and not b.duplicated(keys).any()
        b = b.rename(columns={c: c + "__new" for c in b.columns if c not in keys})
        m = a.merge(b, on=keys, how="left", validate="one_to_one"); assert m["lnLR__new"].notna().sum() + m["lnLR__new"].isna().sum() == len(a)
        chk = {}
        for c in ["eta_pd50_all_a005", "eta_level_locus", "locus_lat", "locus_lon", "eta_needed_searches", "ln_ftime", "lnB"]:
            if c in a.columns and c + "__new" in m.columns:
                x, y = m[c].astype(float), m[c + "__new"].astype(float); f = np.isfinite(x) & np.isfinite(y)
                chk[c] = dict(max_abs_diff=float(np.max(np.abs(x[f] - y[f]))) if f.any() else None, nan_pattern_equal=bool((np.isfinite(x) == np.isfinite(y)).all()))
        old = m["lnLR"].astype(float).copy()
        m["lnLR"] = m["lnLR__new"].astype(float)
        for o in ("D2", "D3", "D4"):
            if f"lnLR_{o}" in m.columns: m[f"lnLR_{o}"] = m[f"lnN_{o}__new"] - m["lnB__new"]
        if "lnLR_pB" in m.columns: m["lnLR_pB"] = m["lnN__new"] - m["lnB_pB__new"]
        if "lnLR_no_bearing" in m.columns: m["lnLR_no_bearing"] = m["lnLR_no_bearing__new"]
        if "ln_f_amp_given_time" in m.columns: m["ln_f_amp_given_time"] = m["lnN__new"] - m["ln_ftime__new"]
        if "eta_post_med" in m.columns: m["eta_post_med"] = m["eta_post_med__new"]
        pcol = "p" if n == "ranked_singles" else ("max_p" if "max_p" in m.columns else None)
        m = m.sort_values(["lnLR"] + ([pcol] if pcol else []), ascending=[False] + ([True] if pcol else []), na_position="last", kind="mergesort")
        m["rank_lnLR"] = np.arange(1, len(m) + 1)
        for c, base in (("eta_x_F35A", "eta_needed" if n == "ranked_singles" else "eta_pd50_all_a005"), ("eta_level_x_F35A", "eta_level_locus")):
            if c in m.columns and base in m.columns: m[c] = m[base].astype(float) / ETA_F35A
        if "F35A_anchor" in m.columns: m["F35A_anchor"] = "2.26e-3 (Metz 2023 arrival, module definition; X02)"
        m["lnLR_22oct_prior_1e-2"] = old
        m = m.drop(columns=[c for c in m.columns if c.endswith("__new")] + ["_ord"])
        m.to_csv(out / f"{n}.csv", index=False)
        fin = np.isfinite(m.lnLR) & np.isfinite(m["lnLR_22oct_prior_1e-2"])
        rep[n] = dict(rows=len(m), finite=int(np.isfinite(m.lnLR).sum()), prior_independent_checks=chk,
                      lnLR_change_q05_q50_q95=[float(q) for q in np.quantile((m.lnLR - m["lnLR_22oct_prior_1e-2"])[fin], [0.05, 0.5, 0.95])] if fin.any() else None,
                      spearman_old_new=float(pd.Series(m.lnLR[fin]).rank().corr(pd.Series(m["lnLR_22oct_prior_1e-2"][fin]).rank())) if fin.any() else None)
    (out / "README.txt").write_text(__doc__ + f"\nLabel: {label}\n")
    json.dump(rep, open(out / "merge_report.json", "w"), indent=1); print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:5])
