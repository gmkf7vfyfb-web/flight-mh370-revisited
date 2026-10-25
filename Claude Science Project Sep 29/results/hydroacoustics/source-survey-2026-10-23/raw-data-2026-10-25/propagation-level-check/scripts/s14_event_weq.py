"""San Juan event: TNT-equivalent W such that a G&S charge at depth z gives the same 5-40 Hz radiated energy as the inversion
through the chain (energy match, bands with SNR >= 3 dB). Source models SA (construction) and SB (table 3, 1.8 lb/300 ft; 3 lb/60 ft).
A label for an explosion-equivalent source, NOT an implosion model; the event mechanism is not known (Vergoz 2021)."""
import sys, numpy as np, pandas as pd
D = "coord/Claude Science Project Sep 29/results/hydroacoustics-audit/gaspin-shuler"; sys.path.insert(0, D); import gs_reconstruct as GS
B = np.array([5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]); RHOC = 1.54e6; LB = 0.45359237; CONV = 191.1
T3 = pd.read_csv(f"{D}/gs1971_table3_third_octave.csv")
def sl(model, Wkg, zm):
    W = Wkg / LB; zft = zm / 0.3048
    if model == "GS_construction":
        t, x, p = GS.pulse(W, zft, kappa=4.0, neg="sin2"); return np.array([GS.band_db(t, x, f * 2 ** (-1 / 6), f * 2 ** (1 / 6), 40) + CONV for f in B])
    col, Wr, zr = {"GS_table3_1p8lb_300ft": ("e_1p8lb_300ft", 1.8, 300), "GS_table3_3lb_60ft": ("e_3lb_60ft", 3.0, 60), "GS_table3_1p8lb_800ft": ("e_1p8lb_800ft", 1.8, 800), "GS_table3_3lb_500ft": ("e_3lb_500ft", 3.0, 500)}[model]
    a = (W / Wr) ** (1 / 3); s = a * ((zr + 33) / (zft + 33)) ** (5 / 6); fm = B * s
    v = np.interp(np.log10(fm), np.log10(T3.fc_nominal_hz), T3[col]) + 20 * np.log10(a * s) + CONV; v[(fm < 12.5) | (fm > 10000)] = np.nan; return v
bw = B * (2 ** (1 / 6) - 2 ** (-1 / 6))
def E_of(levels, m): return 4 * np.pi / RHOC * np.nansum(np.where(m, 10 ** ((levels - 120) / 10) * bw, 0))
tb = pd.read_csv("out/triad_bands.csv"); tb = tb[(tb.window == "W60") & (tb.event == "sj_event")]
TL = pd.concat([pd.read_csv("out/tl_kraken.csv"), pd.read_csv("out/tl_ram.csv")]); TL = TL[TL.path.str.startswith("sje") & TL.tl_db.notna()]
rows = []; Ws = np.geomspace(1, 1e4, 161)
for tri in ("H10N", "H10S"):
    m = tb[tb.triad == tri].set_index("fc_hz").reindex(B); ok = (m.snr_dB >= 3).values
    for (model, z), g in TL[TL.path == f"sje-{tri}"].groupby(["model", "src_depth_m"]):
        t = g.set_index("fc_hz").tl_db.reindex(B).values; Einv = E_of(m.esd_dB.values + t, ok)
        for smod in ("GS_construction", "GS_table3_1p8lb_300ft", "GS_table3_1p8lb_800ft", "GS_table3_3lb_500ft", "GS_table3_3lb_60ft"):
            Em = []
            for W in Ws:
                v = sl(smod, W, z); mm = ok & np.isfinite(v); Em.append(E_of(np.where(np.isfinite(v), v, 0), mm) if mm.sum() >= 5 else np.nan)
            Em = np.array(Em); good = np.isfinite(Em)
            Weq = float(np.exp(np.interp(np.log(Einv), np.log(Em[good]), np.log(Ws[good])))) if good.sum() > 5 and Einv >= Em[good].min() and Einv <= Em[good].max() else np.nan
            rows.append(dict(triad=tri, chain=model, z_m=z, source=smod, E_rad_inverted_J=Einv, W_eq_kg=Weq))
df = pd.DataFrame(rows); df.to_csv("out/sanjuan_event_tnt_equivalent.csv", index=False)
print(df.pivot_table(index=["chain", "z_m"], columns=["source", "triad"], values="W_eq_kg").round(0).to_string())
