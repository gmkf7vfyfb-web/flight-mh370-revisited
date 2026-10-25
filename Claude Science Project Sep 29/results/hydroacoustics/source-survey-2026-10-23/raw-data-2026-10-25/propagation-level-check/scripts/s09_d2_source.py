"""(a) D2 Arons-relative ratio: Arons-equivalent in-channel yield from the measured peak, P = 52.4e6 (R/W^(1/3))^-1.13 Pa
(R m, W kg TNT; Arons 1954 via Brown 2026 Eq. 2), divided by the declared yield. Primary band 1-60 Hz (Vergoz Fig. 2);
4-9 and 5-20 Hz reported. Triad median over good elements.
(b) Source inversion through the chain: SL_b = measured ESD_b + TL_b (dB re 1 uPa^2 s/Hz at 1 m, free field, surface image
in TL). Radiated acoustic energy in 5-40 Hz: E = 4 pi (1 m)^2 / (rho c) * sum_b 10^((SL_b-120)/10) * BW_b, rho c = 1.54e6.
(c) San Juan event TNT-equivalent: W such that the G&S model (SA, SB 3 lb/60 ft and 1.8 lb/300 ft) at the event depth gives the
same band-median SL as the inversion; also the event/charge energy ratio times 108 kg (energy-proportional analogue)."""
import sys, numpy as np, pandas as pd
D = "coord/Claude Science Project Sep 29/results/hydroacoustics-audit/gaspin-shuler"; sys.path.insert(0, D); import gs_reconstruct as GS
B = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]; RHOC = 1.54e6; LB = 0.45359237; CONV = 191.1
pk = pd.read_csv("out/peaks_by_band.csv"); pk = pk[pk.station != "H10S1"]; pk["triad"] = pk.station.str[:4]
DECL = {"sj_charge": 108.0, **{f"fsst16_{i}": 6759.0 for i in range(1, 6)}, **{f"fsst21_{i}": 18000.0 for i in range(1, 4)}}
rows = []
for (ev, tri), g in pk.groupby(["event", "triad"]):
    R = g.range_km.median() * 1e3
    for band in ("1-60", "4-9", "5-20"):
        P = g[f"peak_{band}_Pa"].median(); W = (R * (P / 52.4e6) ** (1 / 1.13)) ** 3
        rows.append(dict(event=ev, triad=tri, band_Hz=band, peak_Pa=P, peak_dB=20 * np.log10(P / 1e-6), range_km=R / 1e3, W_arons_kg=W, W_declared_kg=DECL.get(ev, np.nan), D2_ratio=W / DECL[ev] if ev in DECL else np.nan))
d2 = pd.DataFrame(rows); d2.to_csv("out/d2_arons.csv", index=False); print(d2[d2.band_Hz == "1-60"].round(4).to_string())
tb = pd.read_csv("out/triad_bands.csv"); tb = tb[tb.window == "W60"]
TL = [pd.read_csv("out/tl_kraken.csv")]
try: TL.append(pd.read_csv("out/tl_ram.csv"))
except FileNotFoundError: pass
TL = pd.concat(TL); TL = TL[TL.tl_db.notna()]
inv = []
for ev, pfx, zs in (("sj_event", "sje", (500.0, 900.0)), ("sj_charge", "sjcV", (33.0,))):
    for tri in ("H10N", "H10S"):
        m = tb[(tb.event == ev) & (tb.triad == tri)].set_index("fc_hz")
        for model in ("KRAKEN", "RAM"):
            for z in zs:
                t = TL[(TL.path == f"{pfx}-{tri}") & (TL.model == model) & np.isclose(TL.src_depth_m, z)].set_index("fc_hz").tl_db
                if len(t) < len(B): continue
                fc = [f for f in B if m.snr_dB[f] >= 3]
                sl = pd.Series({f: m.esd_dB[f] + t[f] for f in fc})
                bw = np.array([f * (2 ** (1 / 6) - 2 ** (-1 / 6)) for f in fc])
                E = 4 * np.pi / RHOC * np.sum(10 ** ((sl.values - 120) / 10) * bw)
                inv.append(dict(event=ev, triad=tri, model=model, src_depth_m=z, n_bands=len(fc), sl_median_dB=float(sl.median()), E_rad_5_40_J=E,
                                **{f"sl_{f:g}": sl.get(f, np.nan) for f in B}))
iv = pd.DataFrame(inv)
# event / charge energy ratio per triad x model (charge at 33 m)
for i, r in iv[iv.event == "sj_event"].iterrows():
    c = iv[(iv.event == "sj_charge") & (iv.triad == r.triad) & (iv.model == r.model)]
    if len(c): iv.loc[i, "E_ratio_event_over_charge"] = r.E_rad_5_40_J / c.E_rad_5_40_J.iloc[0]; iv.loc[i, "W_eq_energy_scaled_kg"] = 108.0 * iv.loc[i, "E_ratio_event_over_charge"]
# G&S equivalent yield at the event depth (band-median SL match)
def gs_sl(Wkg, zm, model):
    W = Wkg / LB; zft = zm / 0.3048
    if model == "SA":
        t, x, p = GS.pulse(W, zft, kappa=4.0, neg="sin2"); return np.array([GS.band_db(t, x, f * 2 ** (-1 / 6), f * 2 ** (1 / 6), 40) + CONV for f in B])
    T3 = pd.read_csv(f"{D}/gs1971_table3_third_octave.csv"); col, Wr, zr = {"SB60": ("e_3lb_60ft", 3.0, 60), "SB300": ("e_1p8lb_300ft", 1.8, 300)}[model]
    a = (W / Wr) ** (1 / 3); s = a * ((zr + 33) / (zft + 33)) ** (5 / 6); fm = np.array(B) * s
    v = np.interp(np.log10(fm), np.log10(T3.fc_nominal_hz), T3[col]) + 20 * np.log10(a * s) + CONV; v[fm < 12.5] = np.nan; v[fm > 10000] = np.nan; return v
for i, r in iv[iv.event == "sj_event"].iterrows():
    target = np.array([r[f"sl_{f:g}"] for f in B])
    for mdl in ("SA", "SB60", "SB300"):
        Ws = np.geomspace(1, 1e5, 61); best = None
        for W in Ws:
            v = gs_sl(W, r.src_depth_m, mdl); ok = np.isfinite(v) & np.isfinite(target)
            if ok.sum() < 3: continue
            dev = np.median(target[ok] - v[ok])
            if best is None or abs(dev) < abs(best[1]): best = (W, dev, int(ok.sum()))
        if best: iv.loc[i, f"W_eq_GS_{mdl}_kg"] = best[0] * 10 ** (best[1] / 20 / (1 / 3 + 1 / 3)) if False else best[0]; iv.loc[i, f"W_eq_GS_{mdl}_resid_dB"] = best[1]
iv.to_csv("out/source_inversion.csv", index=False)
print(iv.drop(columns=[f"sl_{f:g}" for f in B]).round(3).to_string())
