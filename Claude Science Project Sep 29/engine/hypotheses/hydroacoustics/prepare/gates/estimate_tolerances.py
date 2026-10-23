"""X04 / X05: timing tolerances estimated from data (overnight run 23-24 Oct 2026; Pete: "You'd estimate this using the data").

X04  H08S airgun-shot coincidence. Data: offset dt = (nearest shot time) - (detection time) for every H08S row of the detection
     register (register-2026-10-23/register_singles.csv) whose time lies inside the shot sequence (first shot - 5 s .. last
     shot + 5 s). Shots: results-data/h08s_template/h08s_template_shots.csv (cadence median 9.975 s). Model (maximum likelihood):
       f(dt) = pi * N(dt; mu, sigma) + (1 - pi) * U(-T/2, T/2),  T = median shot interval.
     Output: mu, sigma, pi with bootstrap 95 % intervals (2,000 resamples), the per-row probability
       P(shot-related | dt) = pi N / (pi N + (1 - pi)/T), and the window |dt - mu| <= w where that probability is >= 0.5.
     The label stays a label (Pete, 23 Oct): a shot coincidence is not an exclusion.
X05  Royer 2016 known events. Three parts.
     (a) Prediction at a station from a Royer origin: travel-time residual fraction r = t_obs / (R / c0) - 1 over every Table 5
         arrival (royer_arrivals.csv, 143 arrivals), c0 = median implied speed. Robust sigma_r = 1.4826 * MAD.
         Predicted-arrival 1-sigma: s(T) = sqrt((sigma_r T)^2 + e_t^2 + s_pick^2), e_t = Royer origin-time error of the event,
         s_pick = pick sigma (part b). Tolerance = 2 s(T) (about 95 %).
     (b) Pick sigma: Royer map labels against Table 5 (royer_map_labels.csv) and pick bars at stations other than H01W-2
         (royer_figure_marks.csv); robust sigma of the residuals.
     (c) H01W-2 figure-mark offset: mean and sd of mark_minus_table5_s for H01W-2 pick bars (digitised Fig. 4). If the offset is
         not consistent with 0 (|mean| > 2 sd/sqrt(n)), marks are bias-corrected by the mean before any match, and Table 5 is the
         primary time base.
Usage: python estimate_tolerances.py <module_dir> <register_singles.csv> <out_dir>
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import optimize, stats


def hms(s):
    h, m, x = str(s).split(":"); return int(h) * 3600 + int(m) * 60 + float(x)


def fit_mixture(dt, T):
    def nll(p):
        mu, ls, lp = p; s = np.exp(ls); pi = 1 / (1 + np.exp(-lp))
        return -np.sum(np.log(pi * stats.norm.pdf(dt, mu, s) + (1 - pi) / T))
    r = optimize.minimize(nll, [np.median(dt), np.log(0.4), 2.0], method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    mu, ls, lp = r.x; return dict(mu=float(mu), sigma=float(np.exp(ls)), pi=float(1 / (1 + np.exp(-lp))), nll=float(r.fun), ok=bool(r.success))


def main(mod, reg, out):
    mod, out = Path(mod), Path(out); out.mkdir(parents=True, exist_ok=True); rng = np.random.default_rng(20261024)
    # ---------------- X04
    sh = np.sort(pd.read_csv(mod / "results-data/h08s_template/h08s_template_shots.csv").t.values.astype(float))
    T = float(np.median(np.diff(sh)))
    g = pd.read_csv(reg); h = g[g.rx == "H08S"].copy(); h["t"] = h.time_utc.map(hms)
    h["in_shot_sequence"] = (h.t >= sh[0] - T / 2) & (h.t <= sh[-1] + T / 2)
    h["dt"] = [float((sh - t)[np.argmin(np.abs(sh - t))]) for t in h.t]
    x = h.loc[h.in_shot_sequence, "dt"].values
    f = fit_mixture(x, T)
    boot = [fit_mixture(rng.choice(x, len(x)), T) for _ in range(2000)]
    ci = {k: [float(np.quantile([b[k] for b in boot], q)) for q in (0.025, 0.975)] for k in ("mu", "sigma", "pi")}
    post = lambda d: f["pi"] * stats.norm.pdf(d, f["mu"], f["sigma"]) / (f["pi"] * stats.norm.pdf(d, f["mu"], f["sigma"]) + (1 - f["pi"]) / T)
    # window: |dt - mu| where post = 0.5
    w = optimize.brentq(lambda z: post(f["mu"] + z) - 0.5, 1e-6, T / 2) if post(f["mu"] + T / 2 - 1e-9) < 0.5 else T / 2
    wb = []
    for b in boot:
        pb = lambda d: b["pi"] * stats.norm.pdf(d, b["mu"], b["sigma"]) / (b["pi"] * stats.norm.pdf(d, b["mu"], b["sigma"]) + (1 - b["pi"]) / T)
        wb.append(optimize.brentq(lambda z: pb(b["mu"] + z) - 0.5, 1e-6, T / 2) if pb(b["mu"] + T / 2 - 1e-9) < 0.5 else T / 2)
    h["p_shot_related"] = np.where(h.in_shot_sequence, post(h.dt.values), np.nan)
    h[["time_utc", "det", "band", "t", "in_shot_sequence", "dt", "p_shot_related"]].to_csv(out / "x04_h08s_shot_offsets.csv", index=False)
    x04 = dict(n_rows_h08s=int(len(h)), n_in_shot_sequence=int(h.in_shot_sequence.sum()), shot_interval_median_s=T, n_shots=int(len(sh)),
               fit=f, ci95_bootstrap=ci, window_half_width_s=float(w), window_center_s=f["mu"], window_ci95=[float(np.quantile(wb, 0.025)), float(np.quantile(wb, 0.975))],
               n_within_old_1p5s=int((np.abs(x) <= 1.5).sum()), n_within_new_window=int((np.abs(x - f["mu"]) <= w).sum()),
               note="Detection times are given to 1 s (time_utc), so about 0.29 s of sigma is rounding. Label only; not an exclusion.")
    # ---------------- X05
    rd = mod / "results-data/digitised/royer-2016"
    a = pd.read_csv(rd / "royer_arrivals.csv").dropna(subset=["arrival_utc", "range_km", "travel_s"])
    c0 = float(np.median(a.implied_speed_km_s)); a["r_frac"] = a.travel_s / (a.range_km / c0) - 1
    mad = lambda v: float(1.4826 * np.median(np.abs(v - np.median(v))))
    sig_r = mad(a.r_frac.values)
    lab = pd.read_csv(rd / "royer_map_labels.csv"); mk = pd.read_csv(rd / "royer_figure_marks.csv")
    pb_other = mk[(mk.kind == "pick_bar") & (mk.station != "H01W-2")].mark_minus_table5_s.dropna().values
    s_pick_labels = mad(lab.map_minus_table5_s.dropna().values); s_pick_bars = mad(pb_other)
    s_pick = float(max(s_pick_labels, s_pick_bars))
    hb = mk[(mk.kind == "pick_bar") & (mk.station == "H01W-2")].mark_minus_table5_s.dropna().values
    h01w2 = dict(n=int(len(hb)), mean_s=float(hb.mean()), sd_s=float(hb.std(ddof=1)), se_s=float(hb.std(ddof=1) / np.sqrt(len(hb))),
                 consistent_with_zero=bool(abs(hb.mean()) <= 2 * hb.std(ddof=1) / np.sqrt(len(hb))))
    ev = pd.read_csv(rd / "royer_events.csv").set_index("index")
    # tolerance for the cross-ID rows
    cx = pd.read_csv(sys.argv[4]) if len(sys.argv) > 4 else None
    rows = []
    if cx is not None:
        for _, r in cx.iterrows():
            Tt = r.range_km / c0; et = float(ev.loc[int(r.event), "err_time_s"])
            s = float(np.sqrt((sig_r * Tt) ** 2 + et ** 2 + s_pick ** 2))
            rows.append(dict(event=int(r.event), label=r.label, rx=r.rx, range_km=r.range_km, travel_s=Tt, err_time_s=et, sigma_pred_s=s, tol_new_s=2 * s, tol_old_s=r.tol_s, basis_old=r.basis))
        pd.DataFrame(rows).to_csv(out / "x05_crossid_tolerances.csv", index=False)
    x05 = dict(c0_km_s=c0, n_arrivals=int(len(a)), sigma_r_frac=sig_r, sigma_r_frac_sd=float(a.r_frac.std(ddof=1)),
               s_pick_map_labels_s=s_pick_labels, n_map_labels=int(lab.map_minus_table5_s.notna().sum()), s_pick_bars_other_s=s_pick_bars, n_bars_other=int(len(pb_other)),
               s_pick_used_s=s_pick, h01w2_pick_bar_offset=h01w2, tolerance_rule="tol = 2 sqrt((sigma_r T)^2 + e_t^2 + s_pick^2); H01W: Table 5 primary; H01W-2 marks bias-corrected by mean offset if not consistent with 0",
               tol_new_summary=(pd.DataFrame(rows).groupby("rx").tol_new_s.describe().round(1).to_dict("index") if rows else None),
               tol_old_summary=(pd.DataFrame(rows).groupby("rx").tol_old_s.describe().round(1).to_dict("index") if rows else None))
    a[["index", "station", "range_km", "travel_s", "implied_speed_km_s", "r_frac"]].to_csv(out / "x05_royer_travel_residuals.csv", index=False)
    json.dump(dict(x04=x04, x05=x05), open(out / "tolerances.json", "w"), indent=1)
    print(json.dumps(dict(x04={k: x04[k] for k in ("n_in_shot_sequence", "fit", "ci95_bootstrap", "window_half_width_s", "window_ci95", "n_within_old_1p5s", "n_within_new_window")},
                          x05={k: x05[k] for k in ("c0_km_s", "sigma_r_frac", "sigma_r_frac_sd", "s_pick_map_labels_s", "s_pick_bars_other_s", "s_pick_used_s", "h01w2_pick_bar_offset")}), indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
