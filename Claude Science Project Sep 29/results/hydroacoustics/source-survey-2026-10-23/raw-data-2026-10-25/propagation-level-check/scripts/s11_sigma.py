"""sigma_model table (event, station, band, measured - predicted dB, chain, source model) and pooled statistics.
Primary rows: charge 33 m (Vergoz position), FSST 61 m. Sensitivity rows (depth, position, other source columns) kept in residuals.csv."""
import numpy as np, pandas as pd
r = pd.read_csv("out/residuals.csv"); r["source_ref"] = r.source_ref.fillna("")
r["source"] = np.where(r.source_model.str.startswith("SA"), "GS_construction", "GS_table3_" + r.source_ref.str.replace("e_", ""))
r["chain"] = r.model.map({"KRAKEN": "MODULE_KRAKEN_ONLY", "RAM": "MODULE_KRAKEN_RAM"})
prim = r[((r.event == "sj_charge") & (r.src_depth_m == 33.0) & r.path.str.contains("V-")) | ((r.event != "sj_charge") & (r.src_depth_m == 61.0))]
prim = prim[prim.source.isin(["GS_construction", "GS_table3_3lb_60ft", "GS_table3_1p8lb_300ft"])]
cols = ["event", "triad", "fc_hz", "resid_dB", "chain", "source", "src_depth_m", "path", "meas_esd_dB", "pred_esd_dB", "sl_db", "tl_db", "snr_dB"]
prim[cols].sort_values(["event", "triad", "chain", "source", "fc_hz"]).round(2).to_csv("out/sigma_model_table.csv", index=False)
# pooled per band across event x triad (FSST shots each counted; charge once per triad)
prim = prim.assign(group=np.where(prim.event.str.startswith("fsst16"), "FSST 2016", np.where(prim.event.str.startswith("fsst21"), "FSST 2021", "San Juan charge")))
pb = prim.groupby(["chain", "source", "fc_hz"]).resid_dB.agg(["mean", "std", "count"]).reset_index(); pb.round(2).to_csv("out/sigma_model_pooled_by_band.csv", index=False)
S = pd.read_csv("out/scores.csv"); S["source_ref"] = S.source_ref.fillna("")
S["source"] = np.where(S.source_model.str.startswith("SA"), "GS_construction", "GS_table3_" + S.source_ref.str.replace("e_", ""))
S["chain"] = S.model.map({"KRAKEN": "MODULE_KRAKEN_ONLY", "RAM": "MODULE_KRAKEN_RAM"})
SP = S[((S.event == "sj_charge") & (S.src_depth_m == 33.0) & S.path.str.contains("V-")) | ((S.event != "sj_charge") & (S.src_depth_m == 61.0))]
SP = SP[SP.source.isin(["GS_construction", "GS_table3_3lb_60ft", "GS_table3_1p8lb_300ft"])]
SP.round(3).to_csv("out/scores_primary.csv", index=False)
agg = SP.groupby(["chain", "source"]).agg(n=("level_median_dB", "size"), level_mean=("level_median_dB", "mean"), level_sd=("level_median_dB", "std"),
                                          level_min=("level_median_dB", "min"), level_max=("level_median_dB", "max"), slope_mean=("slope_dB_per_oct", "mean"),
                                          slope_sd=("slope_dB_per_oct", "std"), slope_min=("slope_dB_per_oct", "min"), slope_max=("slope_dB_per_oct", "max"),
                                          shape_median=("shape_rms_dB", "median")).reset_index()
agg.round(2).to_csv("out/sigma_model_summary.csv", index=False); print(agg.round(2).to_string())
# station difference H10S - H10N (measured vs predicted), per event, same source cancels
tb = pd.read_csv("out/triad_bands.csv"); tb = tb[tb.window == "W60"]
rows = []
for ev in sorted(set(prim.event)):
    for ch in ("MODULE_KRAKEN_ONLY", "MODULE_KRAKEN_RAM"):
        a = prim[(prim.event == ev) & (prim.chain == ch) & (prim.source == "GS_construction")].pivot_table(index="fc_hz", columns="triad", values=["meas_esd_dB", "tl_db"])
        if ("meas_esd_dB", "H10S") not in a.columns or ("meas_esd_dB", "H10N") not in a.columns: continue
        dm = a["meas_esd_dB"]["H10S"] - a["meas_esd_dB"]["H10N"]; dp = -(a["tl_db"]["H10S"] - a["tl_db"]["H10N"])
        d = (dm - dp).dropna()
        rows.append(dict(event=ev, chain=ch, n_bands=len(d), meas_S_minus_N_median_dB=float(dm.median()), pred_S_minus_N_median_dB=float(dp.median()), misfit_median_dB=float(d.median()),
                         misfit_slope_dB_per_oct=float(np.polyfit(np.log2(d.index.values), d.values, 1)[0]) if len(d) > 3 else np.nan))
sd = pd.DataFrame(rows); sd.round(2).to_csv("out/station_difference.csv", index=False); print(sd.round(2).to_string())
