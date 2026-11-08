"""Weighted summaries of the method-1 energy-transfer sidecars.

Usage: python summarise.py HANDOFF_DIR SIDECAR_DIR OUT_CSV
Rows: route x treatment (all nine headline treatments; D7, D9, D10 are the ordered set) x family subset
(all, no pilot, piloted, planned descent) x band (10-30 headline, 5-45 sensitivity).
Weights w = exp(log_weight_<treatment>) normalised within the route model. Shares are of the route's total weight.
"""
import sys
import numpy as np, pandas as pd
import settling_energy_transfer_m1 as m1

TREAT = ["D7", "D9", "D10", "D13", "D0", "D8", "D14", "D11", "D12"]
FAM = {"all": None, "no pilot": [1], "piloted": [2], "planned descent": [3]}
Q = [0.05, 0.5, 0.95]


def main(hdir, sdir, out):
    rows = []
    for route in ("df", "wp"):
        h = np.load(f"{hdir}/eof-final-handoff-{route}.npz"); s = np.load(f"{sdir}/settling-energy-transfer-m1-{route}.npz")
        fam = h["family_code"]; th = np.abs(h["flight_path_angle_deg_descent_positive"].astype(float))
        v = s["contact_speed_mps"].astype(float); ba = s["bank_assigned"].astype(bool)
        for t in TREAT:
            lw = h[f"log_weight_{t}"].astype(float)
            w = np.exp(lw - np.nanmax(lw)); w[~np.isfinite(w)] = 0.0; w /= w.sum()
            for fname, fc in FAM.items():
                sel = np.ones(len(w), bool) if fc is None else np.isin(fam, fc)
                if not sel.any():
                    continue
                ws = np.where(sel, w, 0.0)
                for band, suf, lo, hi in (("10-30", "", 10.0, 30.0), ("5-45", "_band5_45", 5.0, 45.0)):
                    tau = s["energy_transfer_tau90_s" + suf].astype(float); pk = s["energy_transfer_peak_rate_w" + suf].astype(float)
                    ww = s["w_steep" + suf].astype(float)
                    tq = m1.weighted_quantiles(tau[sel], ws[sel], Q); pq = m1.weighted_quantiles(pk[sel], ws[sel], Q)
                    sh = th <= lo; st = th >= hi; bl = ~sh & ~st
                    r = dict(route=route, treatment=t, family=fname, band_deg=band, weight_share=ws.sum(),
                             ess=m1.ess(ws[sel]), n_rows=int(sel.sum()),
                             share_shallow=ws[sh].sum() / ws.sum(), share_blend=ws[bl].sum() / ws.sum(),
                             share_steep=ws[st].sum() / ws.sum(), mean_w_steep=(ws * ww).sum() / ws.sum(),
                             ess_shallow=m1.ess(ws[sh & sel]), ess_blend=m1.ess(ws[bl & sel]), ess_steep=m1.ess(ws[st & sel]),
                             tau90_q05_s=tq[0], tau90_q50_s=tq[1], tau90_q95_s=tq[2],
                             tau90_min_s=np.nanmin(tau[sel & (ws > 0)]), tau90_max_s=np.nanmax(tau[sel & (ws > 0)]),
                             peak_rate_q05_w=pq[0], peak_rate_q50_w=pq[1], peak_rate_q95_w=pq[2],
                             peak_rate_min_w=np.nanmin(pk[sel & (ws > 0)]), peak_rate_max_w=np.nanmax(pk[sel & (ws > 0)]),
                             share_shallow_v_gt_100=ws[sh & (v > 100)].sum() / ws.sum(),
                             share_bank_assigned=ws[ba].sum() / ws.sum(),
                             share_nan=ws[~np.isfinite(tau)].sum() / ws.sum())
                    if band == "10-30":
                        lb = s["energy_transfer_tau90_logblend_s"].astype(float)
                        d = np.abs(lb - tau) / tau
                        r["max_rel_diff_logblend_vs_t95_minus_t05"] = float(np.nanmax(d[sel & (ws > 0)]))
                        r["weighted_mean_rel_diff_in_band"] = float((ws * np.nan_to_num(d))[bl].sum() / max(ws[bl].sum(), 1e-300))
                    rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False, float_format="%.6g")
    return df


if __name__ == "__main__":
    main(*sys.argv[1:4])
