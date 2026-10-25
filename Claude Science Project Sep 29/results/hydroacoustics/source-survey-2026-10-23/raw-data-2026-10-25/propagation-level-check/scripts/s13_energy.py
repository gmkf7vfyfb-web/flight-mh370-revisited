"""(a) Known charges: radiated acoustic energy in 5-40 Hz inverted through the chain (SL_b = ESD_b + TL_b; E = 4 pi/(rho c) sum SL_b BW_b)
divided by explosive energy (4.184 MJ/kg TNT), and the same fraction predicted by each G&S source model. Not stored as coupling rows (see note).
(b) San Juan event: inverted 5-40 Hz radiated energy as a function of source depth (KRAKEN 200-900 m; RAM 500, 900 m) and
E/(P V) for declared trapped volumes V (not known: 10, 100, 1000 m^3), P = rho g z."""
import numpy as np, pandas as pd
B = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]; RHOC = 1.54e6; Q = 4.184e6
tb = pd.read_csv("out/triad_bands.csv"); tb = tb[tb.window == "W60"]
TL = pd.concat([pd.read_csv("out/tl_kraken.csv"), pd.read_csv("out/tl_ram.csv")]); TL = TL[TL.tl_db.notna()]
sl = pd.read_csv("out/source_levels.csv")
def E_of(levels, fcs): bw = np.array([f * (2 ** (1 / 6) - 2 ** (-1 / 6)) for f in fcs]); return 4 * np.pi / RHOC * np.sum(10 ** ((np.asarray(levels) - 120) / 10) * bw)
rows = []
EV = {"sj_charge": ("sjcV", 108.0, 33.0, "charge_108kg_33m"), **{f"fsst16_{i}": (f"fsst16_{i}", 6759.0, 61.0, "fsst16_6759kg_61m") for i in range(1, 6)},
      **{f"fsst21_{i}": (f"fsst21_{i}", 18000.0, 61.0, "fsst21_18000kg_61m") for i in range(1, 4)}}
for ev, (pfx, W, z, case) in EV.items():
    for tri in ("H10N", "H10S"):
        m = tb[(tb.event == ev) & (tb.triad == tri)].set_index("fc_hz")
        if m.empty: continue
        fc = [f for f in B if m.snr_dB[f] >= 3]
        for model in ("KRAKEN", "RAM"):
            t = TL[(TL.path == f"{pfx}-{tri}") & (TL.model == model) & np.isclose(TL.src_depth_m, z)].set_index("fc_hz").tl_db
            if len(t) < 10: continue
            Ei = E_of([m.esd_dB[f] + t[f] for f in fc], fc)
            d = dict(event=ev, triad=tri, chain=model, W_kg=W, z_m=z, n_bands=len(fc), E_rad_inverted_J=Ei, frac_inverted=Ei / (W * Q))
            for smod, ref, lab in (("SA_GS_construction", "", "GS_construction"), ("SB_GS_table3_similitude", "e_3lb_60ft", "GS_table3_3lb_60ft"), ("SB_GS_table3_similitude", "e_1p8lb_300ft", "GS_table3_1p8lb_300ft")):
                s = sl[(sl.case == case) & (sl.model == smod) & (sl.ref.fillna("") == ref)].set_index("fc_hz").sl_db
                ff = [f for f in fc if np.isfinite(s.get(f, np.nan))]; d[f"frac_pred_{lab}"] = E_of(s[ff].values, ff) / (W * Q); d[f"n_pred_bands_{lab}"] = len(ff)
            rows.append(d)
fr = pd.DataFrame(rows); fr.to_csv("out/explosion_radiated_fraction.csv", index=False); print(fr.round(4).to_string())
# San Juan event ridge
rr = []
for tri in ("H10N", "H10S"):
    m = tb[(tb.event == "sj_event") & (tb.triad == tri)].set_index("fc_hz"); fc = [f for f in B if m.snr_dB[f] >= 3]
    for model in ("KRAKEN", "RAM"):
        for z in sorted(set(TL[(TL.path == f"sje-{tri}") & (TL.model == model)].src_depth_m)):
            t = TL[(TL.path == f"sje-{tri}") & (TL.model == model) & np.isclose(TL.src_depth_m, z)].set_index("fc_hz").tl_db
            E = E_of([m.esd_dB[f] + t[f] for f in fc], fc); P = 1025 * 9.81 * z
            rr.append(dict(triad=tri, chain=model, z_m=z, E_rad_5_40_J=E, TNT_eq_kg_at_4184kJ=E / Q, **{f"eta_imp_V{V}m3": E / (P * V) for V in (10, 100, 1000)}))
ridge = pd.DataFrame(rr); ridge.to_csv("out/sanjuan_event_energy_vs_depth.csv", index=False); print(ridge.round(5).to_string())
