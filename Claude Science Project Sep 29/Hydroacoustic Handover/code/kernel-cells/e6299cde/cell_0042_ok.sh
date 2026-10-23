cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
cat > coincidence.py <<'EOF'
"""BLOCK 5 step 3: two-site coincidence over all candidate pairs (preregistration.py section 8), with time-slide
significance. Primary = M1b rows (H08S: M1b and M1b_res), secondary = any detector; screen level or better.
Usage: python coincidence.py <out_dir>   Outputs: pairs.csv, coincidence_summary.csv"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import preregistration as R


def count_pairs(ta, tb, lo, hi):
    if len(ta) == 0 or len(tb) == 0: return 0, []
    d = tb[None, :] - ta[:, None]
    m = (d >= lo) & (d <= hi)
    return int(m.sum()), np.argwhere(m)


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    C = pd.concat([pd.read_csv(out.parent / "imos" / "imos_windows.csv"), pd.read_csv(out.parent / "panels" / "panel_windows.csv")], ignore_index=True)
    C = C[C.p < R.SCREEN_P].copy(); C["receiver"] = C.receiver.astype(str)
    L = pd.read_csv(R.RD / "searches_run_j" / "prereg_lag_intervals.csv")
    shifts = np.array([k * R.SLIDE_STEP_S for k in range(-R.SLIDE_K, R.SLIDE_K + 1) if k != 0])
    rows, pairs = [], []
    for a, b in R.PAIRS:
        lr = L[(L.rx_a == a) & (L.rx_b == b)].iloc[0]; lo, hi = lr.lag_lo_s, lr.lag_hi_s
        for fam, sel in (("primary_M1b", C.detector.isin(["M1b", "M1b_res"])), ("secondary_any", np.ones(len(C), bool))):
            A = C[(C.receiver == a) & sel]; B = C[(C.receiver == b) & sel]
            n_obs, idx = count_pairs(A.t_unix.values, B.t_unix.values, lo, hi)
            slide = np.array([count_pairs(A.t_unix.values, B.t_unix.values + s, lo, hi)[0] for s in shifts])
            p_slide = (np.sum(slide >= n_obs) + 1) / (len(shifts) + 1) if n_obs > 0 else 1.0
            best = None
            for i, j in idx:
                ra, rb = A.iloc[i], B.iloc[j]; pm = max(ra.p, rb.p)
                pairs.append(dict(rx_a=a, rx_b=b, family=fam, t_a=ra.time_utc, det_a=ra.detector, band_a=ra.band_hz, p_a=ra.p, lab_a=ra.label,
                                  t_b=rb.time_utc, det_b=rb.detector, band_b=rb.band_hz, p_b=rb.p, lab_b=rb.label, lag_s=rb.t_unix - ra.t_unix, lag_lo_s=lo, lag_hi_s=hi, max_p=pm,
                                  kadri_a=ra.kadri_label, kadri_b=rb.kadri_label, n_pairs_obs=n_obs, p_slide=p_slide, caveats=R.CAVEATS))
                if best is None or pm < best: best = pm
            rows.append(dict(rx_a=a, rx_b=b, family=fam, n_a=len(A), n_b=len(B), lag_lo_s=round(lo), lag_hi_s=round(hi), n_pairs_obs=n_obs,
                             expected_by_chance=float(slide.mean()), slide_max=int(slide.max()), p_slide=p_slide, strongest_pair_max_p=best, caveats=R.CAVEATS))
    S = pd.DataFrame(rows); S.to_csv(out / "coincidence_summary.csv", index=False)
    P = pd.DataFrame(pairs).sort_values("max_p") if pairs else pd.DataFrame(columns=["rx_a"]); P.to_csv(out / "pairs.csv", index=False)
    print(S.to_string(index=False))
    if len(P): print(P.head(12)[["rx_a", "rx_b", "family", "t_a", "det_a", "p_a", "t_b", "det_b", "p_b", "lag_s", "max_p", "p_slide", "kadri_a"]].to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1])
EOF
python coincidence.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/coincidence 2>&1 | tail -60