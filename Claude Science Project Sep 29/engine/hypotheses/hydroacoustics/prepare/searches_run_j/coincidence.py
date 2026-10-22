"""BLOCK 5 step 3: two-site coincidence over all candidate pairs (preregistration.py section 8), with time-slide
significance. Primary = M1b rows (H08S: M1b and M1b_res), secondary = any detector; screen level or better.
AMENDMENT 1 (disclosed, after the first run): the pre-registered time slides (k x 300 s) move a receiver's rows out
of its held data (307 s IMOS records every 15 min; 10 min panels), so the slide null is schedule-biased and reaches
its floor trivially. A HELD-SPAN PERMUTATION null is added and sets p: 2,000 draws in which each receiver's candidate
times are redrawn uniformly inside the spans actually searched (its records / panels), counts per receiver kept;
p_perm = (#draws with N >= N_obs + 1)/2001; expected_by_chance = the mean. The slide numbers are kept beside it.
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


N_PERM = 2000


def held_spans(Wall):
    """Searched spans per receiver from the scored windows: [window_start, window_start + 55 s] merged."""
    sp = {}
    for rx, g in Wall.groupby("receiver"):
        st = np.sort(np.unique((g.t_unix - (g.t_unix % 1)).values))  # placeholder, replaced below
        ws = g.apply(lambda r: R.hms_to_unix(r.window_start_utc + ".0"), axis=1).values
        iv = sorted(set((float(w), float(w) + R.WINDOW_S) for w in ws))
        merged = []
        for a, b in iv:
            if merged and a <= merged[-1][1] + 1e-6: merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else: merged.append((a, b))
        sp[str(rx)] = merged
    return sp


def draw_times(rng, spans, n):
    L = np.array([b - a for a, b in spans]); c = np.cumsum(L) / L.sum()
    u = rng.random(n); k = np.searchsorted(c, u); off = rng.random(n) * L[k]
    return np.array([spans[i][0] for i in k]) + off


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    Wall = pd.concat([pd.read_csv(out.parent / "imos" / "imos_windows.csv"), pd.read_csv(out.parent / "panels" / "panel_windows.csv")], ignore_index=True)
    Wall["receiver"] = Wall.receiver.astype(str)
    spans = held_spans(Wall)
    rng = np.random.default_rng(R.SEED)
    C = Wall[Wall.p < R.SCREEN_P].copy()
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
            perm = np.array([count_pairs(draw_times(rng, spans[a], len(A)), draw_times(rng, spans[b], len(B)), lo, hi)[0] for _ in range(N_PERM)]) if n_obs > 0 else np.zeros(1)
            p_perm = (np.sum(perm >= n_obs) + 1) / (N_PERM + 1) if n_obs > 0 else 1.0
            best = None
            for i, j in idx:
                ra, rb = A.iloc[i], B.iloc[j]; pm = max(ra.p, rb.p)
                pairs.append(dict(rx_a=a, rx_b=b, family=fam, t_a=ra.time_utc, det_a=ra.detector, band_a=ra.band_hz, p_a=ra.p, lab_a=ra.label,
                                  t_b=rb.time_utc, det_b=rb.detector, band_b=rb.band_hz, p_b=rb.p, lab_b=rb.label, lag_s=rb.t_unix - ra.t_unix, lag_lo_s=lo, lag_hi_s=hi, max_p=pm,
                                  kadri_a=ra.kadri_label, kadri_b=rb.kadri_label, n_pairs_obs=n_obs, p_perm=p_perm, p_slide=p_slide, caveats=R.CAVEATS))
                if best is None or pm < best: best = pm
            rows.append(dict(rx_a=a, rx_b=b, family=fam, n_a=len(A), n_b=len(B), lag_lo_s=round(lo), lag_hi_s=round(hi), n_pairs_obs=n_obs,
                             expected_by_chance=float(perm.mean()), p_perm=p_perm, slide_mean=float(slide.mean()), slide_max=int(slide.max()), p_slide=p_slide,
                             strongest_pair_max_p=best, caveats=R.CAVEATS))
    S = pd.DataFrame(rows); S.to_csv(out / "coincidence_summary.csv", index=False)
    P = pd.DataFrame(pairs).sort_values("max_p") if pairs else pd.DataFrame(columns=["rx_a"]); P.to_csv(out / "pairs.csv", index=False)
    print(S[["rx_a", "rx_b", "family", "n_a", "n_b", "n_pairs_obs", "expected_by_chance", "p_perm", "p_slide", "strongest_pair_max_p"]].to_string(index=False))
    if len(P): print(P[P.family == "primary_M1b"].head(10)[["rx_a", "rx_b", "t_a", "det_a", "p_a", "t_b", "det_b", "p_b", "lag_s", "max_p", "p_perm", "kadri_a"]].to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1])
