"""Triad levels (M6) and residuals r_b = measured - predicted (prereg S). Writes out/triad_bands.csv, out/residuals.csv, out/scores.csv."""
import sys, numpy as np, pandas as pd
B = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
mb = pd.read_csv("out/meas_bands.csv"); mb["triad"] = mb.station.str[:4]
# M6 flag: element departs from triad median by > 6 dB in >= 3 bands (W60, 5-40 Hz)
w = mb[(mb.window == "W60") & mb.fc_hz.isin(B)].copy(); w["lvl"] = 10 * np.log10(w.E_total_Pa2s)
w["dev"] = w.lvl - w.groupby(["event", "triad", "fc_hz"]).lvl.transform("median")
fl = w.assign(bad=w.dev.abs() > 6).groupby(["event", "station"]).bad.sum().reset_index(); fl["flagged"] = fl.bad >= 3
flags = set(map(tuple, fl[fl.flagged][["event", "station"]].values)); print("flagged elements:", sorted(flags))
mb["flagged"] = [(e, s) in flags for e, s in zip(mb.event, mb.station)]
g = mb[~mb.flagged].groupby(["event", "triad", "window", "fc_hz"])
tb = g.agg(E_total=("E_total_Pa2s", "mean"), E_noise=("E_noise_med_Pa2s", "mean"), E_noise_p16=("E_noise_p16", "mean"), E_noise_p84=("E_noise_p84", "mean"),
           n_el=("station", "nunique"), el_sd_dB=("esd_signal_dB", "std")).reset_index()
tb["E_signal_Pa2s"] = tb.E_total - tb.E_noise; tb["snr_dB"] = 10 * np.log10(tb.E_total / tb.E_noise)
bw = tb.fc_hz * (2 ** (1 / 6) - 2 ** (-1 / 6)); tb["esd_dB"] = np.where(tb.E_signal_Pa2s > 0, 10 * np.log10(tb.E_signal_Pa2s.clip(1e-30) / bw) + 120, np.nan)
# noise-subtraction uncertainty: signal with noise at its 16/84 % values
tb["esd_dB_lo"] = 10 * np.log10((tb.E_total - tb.E_noise_p84).clip(1e-30) / bw) + 120; tb["esd_dB_hi"] = 10 * np.log10((tb.E_total - tb.E_noise_p16).clip(1e-30) / bw) + 120
tb.to_csv("out/triad_bands.csv", index=False)
SRC = {"sj_charge": ("sjc", "charge_108kg", [30.0, 33.0, 38.0], 33.0), **{f"fsst16_{i}": (f"fsst16_{i}", "fsst16_6759kg", [30.0, 61.0, 100.0], 61.0) for i in range(1, 6)},
       **{f"fsst21_{i}": (f"fsst21_{i}", "fsst21_18000kg", [30.0, 61.0, 100.0], 61.0) for i in range(1, 4)}}
sl = pd.read_csv("out/source_levels.csv")
TL = [pd.read_csv("out/tl_kraken.csv")]
try: TL.append(pd.read_csv("out/tl_ram.csv"))
except FileNotFoundError: pass
TL = pd.concat(TL); TL = TL[TL.tl_db.notna()]
def stats(fc, r):
    x = np.log2(np.asarray(fc)); r = np.asarray(r); A = np.vstack([np.ones_like(x), x]).T
    c, *_ = np.linalg.lstsq(A, r, rcond=None); res = r - A @ c
    se = np.sqrt(np.sum(res ** 2) / max(1, len(r) - 2) / np.sum((x - x.mean()) ** 2))
    return float(np.median(r)), float(c[1]), float(se), float(np.sqrt(np.mean(res ** 2)))
def grade(v, p, q): v = abs(v); return "PASS" if v <= p else ("PARTIAL" if v <= q else "FAIL")
rows, sc = [], []
for ev, (pfx, scase, zlist, z0) in SRC.items():
    for tri in ("H10N", "H10S"):
        m = tb[(tb.event == ev) & (tb.triad == tri) & (tb.window == "W60") & tb.fc_hz.isin(B)].set_index("fc_hz")
        if m.empty: continue
        posvar = ["V", "N"] if ev == "sj_charge" else [""]
        for pv in posvar:
            path = f"{pfx}{pv}-{tri}"
            for model in ("KRAKEN", "RAM"):
                for z in zlist:
                    t = TL[(TL.path == path) & (TL.model == model) & np.isclose(TL.src_depth_m, z)].set_index("fc_hz").tl_db
                    if len(t) < len(B): continue
                    for smod, ref in (("SA_GS_construction", ""), ("SB_GS_table3_similitude", "e_3lb_60ft"), ("SB_GS_table3_similitude", "e_1p8lb_60ft"),
                                      ("SB_GS_table3_similitude", "e_1p8lb_300ft"), ("SB_GS_table3_similitude", "e_1p8lb_800ft"), ("SB_GS_table3_similitude", "e_3lb_500ft")):
                        case = f"{scase}_{z:g}m"
                        s = sl[(sl.case == case) & (sl.model == smod) & (sl.ref.fillna("") == ref)].set_index("fc_hz").sl_db
                        if s.empty: continue
                        ok = (m.snr_dB >= 3) & s.reindex(m.index).notna()
                        fc = [f for f in B if ok.get(f, False)]
                        pred = s[fc] - t[fc]; r = m.esd_dB[fc] - pred
                        for f in fc:
                            rows.append(dict(event=ev, triad=tri, path=path, model=model, src_depth_m=z, source_model=smod, source_ref=ref, fc_hz=f, sl_db=s[f], tl_db=t[f],
                                             pred_esd_dB=pred[f], meas_esd_dB=m.esd_dB[f], meas_lo=m.esd_dB_lo[f], meas_hi=m.esd_dB_hi[f], snr_dB=m.snr_dB[f], resid_dB=r[f]))
                        if len(fc) >= 4:
                            lv, sl_, se, sh = stats(fc, r.values)
                            g3 = dict(level=grade(lv, 4, 7), slope=grade(sl_, 1.5, 3), shape=grade(sh, 3, 5))
                            sc.append(dict(event=ev, triad=tri, path=path, model=model, src_depth_m=z, source_model=smod, source_ref=ref, n_bands=len(fc), level_median_dB=lv,
                                           slope_dB_per_oct=sl_, slope_se=se, shape_rms_dB=sh, **{f"grade_{k}": v for k, v in g3.items()},
                                           verdict="FAIL" if "FAIL" in g3.values() else ("PASS" if all(v == "PASS" for v in g3.values()) else "PARTIAL")))
pd.DataFrame(rows).to_csv("out/residuals.csv", index=False); S = pd.DataFrame(sc); S.to_csv("out/scores.csv", index=False)
prim = S[(S.source_ref.isin(["", "e_3lb_60ft"])) & (S.src_depth_m.isin([33.0, 61.0])) & (S.path.str.contains("V-|fsst"))]
print(prim[["event", "triad", "model", "source_model", "n_bands", "level_median_dB", "slope_dB_per_oct", "slope_se", "shape_rms_dB", "verdict"]].round(2).to_string())
