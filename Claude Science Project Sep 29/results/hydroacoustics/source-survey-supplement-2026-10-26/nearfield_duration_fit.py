"""Source-duration test on the near-field envelopes (exploratory source-model calibration on the F-35A; nothing returns
to end of flight). Predicted 1-s RMS envelope = Bellhop path impulse response (nearfield_arrivals.py) convolved with a
source energy envelope (boxcar of length tau, or one-sided exponential with time constant tau) and the 1-s RMS window
(boxcar 1 s, step 0.02 s as Metz), plus the station's noise power. Free per fit: time shift, level. Misfit = RMS dB over
onset - 3 s .. onset + 15 s. Also: envelope metrics of the tau = 0 prediction (path + window only).
Usage: python nearfield_duration_fit.py <out_dir>
"""
import sys, json, pathlib, importlib.util
import numpy as np, pandas as pd
out = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("dv", pathlib.Path(__file__).with_name("derive_nearfield.py"))
src = open(pathlib.Path(__file__).with_name("derive_nearfield.py")).read().split("rows, bands, timing")[0]
ns = {}; sys.argv_bak = sys.argv; sys.argv = ["x", str(out), str(out), str(out)]; exec(src, ns); sys.argv = sys.argv_bak
env_metrics = ns["env_metrics"]
IR = pd.read_csv(out / "arr" / "nearfield_impulse_response.csv"); DV = pd.read_csv(out / "metz-nearfield-derived.csv")
DT = 0.02; TAUS = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
def predict(h, tau, kind):
    s = np.zeros(int(round(max(tau, DT) / DT)) + 1)
    if kind == "box": s[: max(1, int(round(tau / DT)))] = 1.0
    else:
        tt = np.arange(int(round(5 * max(tau, DT) / DT)) + 1) * DT; s = np.exp(-tt / max(tau, 1e-6))
    y = np.convolve(h, s / s.sum()); w = np.ones(int(round(1.0 / DT))) / int(round(1.0 / DT))
    return np.convolve(y, w)
rows, fits = [], []
for st in ["DSOH", "KSP1", "KSP2", "KSP3"]:
    E = pd.read_csv(out / f"metz-fig2-digitised-{st}.csv"); t, L = E.utc_s_of_day.values, E.rms_db_re_1uPa.values
    d = DV[(DV.station == st) & np.isclose(DV.floor_fill_db, 90.0)].iloc[0]; Ln = float(d.noise_pre_onset_db); ton = float(d.onset_utc_s)
    win = (t >= ton - 3.0) & (t <= ton + 15.0); Pn = 10 ** (Ln / 10)
    for zs in (2.0, 10.0, 30.0):
        g = IR[(IR.station == st) & np.isclose(IR.src_depth_m, zs)]
        h = np.zeros(int(round(g.t_rel_first_s.max() / DT)) + 2); h[np.round(g.t_rel_first_s.values / DT).astype(int)] = g.energy.values
        for kind in ("box", "exp"):
            for tau in TAUS:
                y = predict(h, tau, kind); best = (np.inf, None)
                for sh in np.arange(-4.0, 2.01, 0.1):                  # shift of the first ray relative to observed onset
                    tp = ton + sh + np.arange(len(y)) * DT
                    yp = np.interp(t[win], tp, y, left=0.0, right=0.0)
                    # level: fit peak excess to observed peak excess (closed-form in linear power is ill-posed in dB; grid)
                    for a in 10 ** np.linspace(-1.0, 1.0, 41) * (10 ** (d.peak_db / 10) - Pn) / max(y.max(), 1e-30):
                        Lp = 10 * np.log10(a * yp + Pn); r = float(np.sqrt(np.mean((Lp - L[win]) ** 2)))
                        if r < best[0]: best = (r, (sh, a))
                sh, a = best[1]; tp = ton + sh + np.arange(len(y)) * DT
                Lfull = 10 * np.log10(a * np.interp(t, tp, y, left=0.0, right=0.0) + Pn)
                M = env_metrics(t, Lfull, DT)
                fits.append(dict(station=st, src_depth_m=zs, kind=kind, tau_s=tau, rms_misfit_db=best[0], shift_s=sh, pred_w6_s=M["w6_s"],
                                 pred_span_5_95_s=M["span_5_95_s"], pred_rise_10_90_s=M["rise_10_90_s"], pred_decay_db_per_s=M["decay_db_per_s"],
                                 obs_w6_s=float(d.w6_s), obs_span_5_95_s=float(d.span_5_95_s), obs_rise_10_90_s=float(d.rise_10_90_s), obs_decay_db_per_s=float(d.decay_db_per_s)))
                if tau in (0.0, 2.0, 5.0) and kind == "box":
                    rows += [dict(station=st, src_depth_m=zs, tau_s=tau, utc_s_of_day=tt_, pred_db=v) for tt_, v in zip(t, Lfull)]
F = pd.DataFrame(fits); F.to_csv(out / "metz-nearfield-duration-fit.csv", index=False); pd.DataFrame(rows).to_csv(out / "metz-nearfield-pred-envelopes.csv", index=False)
best = F.loc[F.groupby(["station", "src_depth_m", "kind"]).rms_misfit_db.idxmin()]
pd.set_option("display.width", 250)
print(best[["station", "src_depth_m", "kind", "tau_s", "rms_misfit_db", "pred_span_5_95_s", "obs_span_5_95_s", "pred_w6_s", "obs_w6_s"]].round(2).to_string())
z0 = F[(F.tau_s == 0.0) & (F.kind == "box")]
print(z0[["station", "src_depth_m", "rms_misfit_db", "pred_span_5_95_s", "obs_span_5_95_s", "pred_w6_s", "obs_w6_s", "pred_rise_10_90_s", "obs_rise_10_90_s", "pred_decay_db_per_s", "obs_decay_db_per_s"]].round(2).to_string())
# misfit curve, z_s 10 m boxcar
print(F[(F.src_depth_m == 10.0) & (F.kind == "box")].pivot_table(index="tau_s", columns="station", values="rms_misfit_db").round(2).to_string())
