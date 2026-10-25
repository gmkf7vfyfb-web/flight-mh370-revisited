"""Declared explosion source models (prereg P3). Output: out/source_levels.csv, SL(1 m) band-average ESD, dB re 1 uPa^2 s/Hz.
SA: Gaspin & Shuler (1971) construction re-implemented (audit gs_reconstruct.py, kappa 4, sin^2), + 191.1 dB (audit conversion:
    10 log10(rho c 1e10) + 20 log10(91.44 m), rho c 1.539e5 cgs).
SB: G&S Table 3 (printed p. 12) column scaled by explosion similitude: ESD(f) = ESD_ref(f s) + 20 log10(a s),
    a = (W/W_ref)^(1/3), s = (W/W_ref)^(1/3) ((z_ref+33 ft)/(z+33 ft))^(5/6); log-f interpolation between band centres;
    f s below 12.5 Hz (lowest Table 3 band) is flagged 'below_table' and not used."""
import sys, numpy as np, pandas as pd
D = "coord/Claude Science Project Sep 29/results/hydroacoustics-audit/gaspin-shuler"; sys.path.insert(0, D); import gs_reconstruct as GS
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]; CONV = 191.1; LB = 0.45359237
T3 = pd.read_csv(f"{D}/gs1971_table3_third_octave.csv")
REF = {"e_1p8lb_800ft": (1.8, 800), "e_1p8lb_300ft": (1.8, 300), "e_1p8lb_60ft": (1.8, 60), "e_3lb_60ft": (3.0, 60), "e_3lb_500ft": (3.0, 500)}
CASES = {"charge_108kg_33m": (108, 33), "charge_108kg_30m": (108, 30), "charge_108kg_38m": (108, 38), "charge_102kg_33m": (102, 33),
         "fsst16_6759kg_61m": (6759, 61), "fsst16_6759kg_30m": (6759, 30), "fsst16_6759kg_100m": (6759, 100),
         "fsst21_18000kg_61m": (18000, 61), "fsst21_18000kg_30m": (18000, 30), "fsst21_18000kg_100m": (18000, 100)}
rows = []
for case, (wkg, zm) in CASES.items():
    W = wkg / LB; zft = zm / 0.3048
    t, x, p = GS.pulse(W, zft, kappa=4.0, neg="sin2")
    for fc in BANDS:
        rows.append(dict(case=case, W_kg=wkg, z_m=zm, model="SA_GS_construction", ref="", fc_hz=fc, sl_db=float(GS.band_db(t, x, fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 60) + CONV),
                         f_bubble_hz=float(p["fb"]), note=""))
    for col, (Wr, zr) in REF.items():
        a = (W / Wr) ** (1 / 3); s = a * ((zr + 33.0) / (zft + 33.0)) ** (5 / 6)
        lf = np.log10(T3.fc_nominal_hz.values); e = T3[col].values
        for fc in BANDS:
            fm = fc * s
            ok = fm >= 12.5
            v = float(np.interp(np.log10(fm), lf, e)) + 20 * np.log10(a * s) + CONV if ok else np.nan
            rows.append(dict(case=case, W_kg=wkg, z_m=zm, model="SB_GS_table3_similitude", ref=col, fc_hz=fc, sl_db=v, f_bubble_hz=float(p["fb"]),
                             note=f"a={a:.3f} s={s:.3f} f_ref={fm:.1f} Hz" + ("" if ok else " below_table")))
df = pd.DataFrame(rows); df.to_csv("out/source_levels.csv", index=False)
pv = df[df.case.isin(["charge_108kg_33m", "fsst16_6759kg_61m", "fsst21_18000kg_61m"])].pivot_table(index=["case", "model", "ref"], columns="fc_hz", values="sl_db").round(1)
print(pv.to_string()); print(df.groupby("case").f_bubble_hz.first().round(3))
# reduced depth z/W^(1/3) ft/lb^(1/3)
for c, (wkg, zm) in CASES.items(): print(c, round((zm / 0.3048) / (wkg / LB) ** (1 / 3), 1))
for col, (Wr, zr) in REF.items(): print(col, round(zr / Wr ** (1 / 3), 1))
