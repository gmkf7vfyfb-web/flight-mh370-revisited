
import json, numpy as np, pandas as pd
S = json.load(open("out/injection/summary.json")); E = json.load(open("out/injection_ext/summary_ext.json"))
PDU = pd.read_csv("out/injection_ext/pd_vs_snr_union.csv"); PD0 = pd.read_csv("out/injection/pd_vs_snr.csv")
fu = pd.DataFrame([dict(key=k, **v) for k,v in E["fits_union"].items()]); fu[["logger","method","alpha","tau"]] = fu.key.str.split("|", expand=True)
def s50(lg, m, a, tau):
    r = fu[(fu.logger==str(lg))&(fu.method==m)&(fu.alpha==str(a))&(fu.tau==str(tau))]
    if len(r)==0 or r.snr50.isna().iloc[0]: return "not reached (P_D max %.2f)" % r.pd_max.iloc[0] if len(r) else "—"
    return "%.1f" % r.snr50.iloc[0]
methods = ["M0a_stalta","M0b_bandenergy","M1a_mf_waveform","M1b_mf_envelope","M3_cepstral","M4a_spectral_kurtosis","M4b_kurtosis","M5_synchrosqueezed","M6_changepoint","M7_stochastic_resonance"]
lines=[]
for m in methods:
    row=[m]
    for a in (0.01,0.001):
        for tau in (0.1,1.0,10.0): row.append(s50(3376,m,a,tau))
    lines.append("| "+" | ".join(row)+" |")
tab1="\n".join(lines)
# P_D at selected SNRs (3376, tau 1, alpha 0.01 and 0.001)
def pdtab(lg,a,tau):
    t=PDU[(PDU.logger==lg)&(PDU.alpha==a)&(PDU.tau==tau)].pivot_table(index="method",columns="snr_db",values="pd").reindex(methods)
    return "| method | "+" | ".join(f"{int(c)} dB" for c in t.columns)+" |\n|---|"+"---|"*len(t.columns)+"\n"+"\n".join("| "+m+" | "+" | ".join(f"{v:.2f}" for v in t.loc[m])+" |" for m in t.index)
pd_3376_01 = pdtab(3376,0.01,1.0); pd_3376_001 = pdtab(3376,0.001,1.0)
# secondary
sec=[]
for lg in (3274,3250):
    for m in ("M0a_stalta","M0b_bandenergy","M1a_mf_waveform","M1b_mf_envelope","M4a_spectral_kurtosis"):
        sec.append(f"| {lg} | {m} | {s50(lg,m,0.01,1.0)} | {s50(lg,m,0.001,1.0)} |")
sec="\n".join(sec)
m2 = PD0[PD0.method=="M2_pairs"].pivot_table(index=["alpha"],columns="snr_db",values="pd")
m2tab = "| alpha | "+" | ".join(f"{int(c)} dB" for c in m2.columns)+" |\n|---|"+"---|"*len(m2.columns)+"\n"+"\n".join(f"| {a} | "+" | ".join(f"{v:.2f}" for v in m2.loc[a])+" |" for a in m2.index)
thr = S["thresholds"]["3376"]
thrtab = "\n".join(f"| {m} | {thr[m]['0.01']:.3g} | {thr[m]['0.001']:.3g} |" for m in methods)
# Kadri
cd = pd.read_csv("out/kadri/candidates.csv"); bx = pd.read_csv("out/kadri/box_maxima.csv"); m2c = pd.read_csv("out/kadri/m2_cross_station.csv"); ks = json.load(open("out/kadri/summary.json"))
counts = cd.pivot_table(index="method", columns=["station","label"], values="utc", aggfunc="count", fill_value=0)
cnt_lines = "| method | H01W screen / mark / report | H08S screen / mark / report |\n|---|---|---|\n" + "\n".join(f"| {m} | " + " / ".join(str(counts.loc[m].get(('H01W',l),0)) if m in counts.index else "0" for l in ("screen","mark","report")) + " | " + " / ".join(str(counts.loc[m].get(('H08S',l),0)) if m in counts.index else "0" for l in ("screen","mark","report")) + " |" for m in [x for x in methods if x!="M1a_mf_waveform"])
h01 = cd[(cd.station=="H01W")&(cd.p_null<0.3)].sort_values("p_null")
h01tab = "| panel | method | UTC | statistic | p (null) | label | box / Table 1 |\n|---|---|---|---|---|---|---|\n" + "\n".join(f"| {r.panel} | {r.method} | {r.utc} | {r.statistic:.3g} | {r.p_null:.3f} | {r.label} | {r.box} |" for r in h01.head(25).itertuples())
bxp = bx.pivot_table(index="box", columns="method", values="p_null")
bxtab = "| box | " + " | ".join(bxp.columns) + " |\n|---|" + "---|"*len(bxp.columns) + "\n" + "\n".join(f"| {b} | " + " | ".join(f"{v:.2f}" for v in bxp.loc[b]) + " |" for b in bxp.index)
m2tab_k = "| H01W UTC | lag (s) | H08S UTC | statistic | p (null) | label | box / Table 1 |\n|---|---|---|---|---|---|---|\n" + "\n".join(f"| {r.utc_h01w} | {r.lag_s} | {r.utc_h08s} | {r.M2:.2f} | {r.p_null:.3f} | {r.label} | {r.box} |" for r in m2c.head(8).itertuples())
h08_c = cd[(cd.station=="H08S")]
# H08S
sup = pd.read_csv("out/h08s/suppression.csv"); sc = pd.read_csv("out/h08s/surviving_candidates.csv"); ip = pd.read_csv("out/h08s/injection_pd.csv")
suptab = "| panel | shots | cadence (s) | gated fraction | (c1) residual, whole panel (dB) | (c1) shot-free gaps (dB) | (c2) gating alone (dB) | (c1)+(c2) (dB) |\n|---|---|---|---|---|---|---|---|\n" + "\n".join(f"| {r.panel} | {r.n_shots} | {r.cadence_s:.2f} | {r.gated_fraction:.2f} | {r.c1_reduction_db_whole:+.1f} | {r.c1_reduction_db_shotfree:+.1f} | {r.c2_reduction_db:+.1f} | {r.c1c2_reduction_db:+.1f} |" for r in sup.itertuples())
surv = sc.groupby(["panel","stage"]).size().unstack()
survtab = "| panel | raw | after (c1) | after (c1)+(c2) |\n|---|---|---|---|\n" + "\n".join(f"| {p} | {surv.loc[p,'raw']} | {surv.loc[p,'c1']} | {surv.loc[p,'c1+c2']} |" for p in surv.index)
s12 = sc[sc.stage=="c1+c2"].sort_values("z", ascending=False)
s12tab = "| panel | UTC | z | off cadence | lag-consistent with H01W box |\n|---|---|---|---|---|\n" + "\n".join(f"| {r.panel} | {r.utc} | {r.z:.1f} | {'yes' if r.off_cadence else 'no'} | {r.lag_consistent_with} |" for r in s12.itertuples())
iptab = "| panel | level (dB re median shot peak) | raw: hit / chance | (c1): hit / chance | (c1)+(c2): hit / chance | peak in gate |\n|---|---|---|---|---|---|\n" + "\n".join(f"| {r.panel} | {r.level_db:+.0f} | {r.hit_raw:.2f} / {r.ctl_raw:.2f} | {r.hit_c1:.2f} / {r.ctl_c1:.2f} | {r.hit_c1c2:.2f} / {r.ctl_c1c2:.2f} | {r.peak_gated:.2f} |" for r in ip.itertuples())
TB = json.load(open("out/templates/template_build.json"))
json.dump(dict(tab1=tab1, pd_3376_01=pd_3376_01, pd_3376_001=pd_3376_001, sec=sec, m2tab=m2tab, thrtab=thrtab, cnt_lines=cnt_lines, h01tab=h01tab, bxtab=bxtab, m2tab_k=m2tab_k, suptab=suptab, survtab=survtab, s12tab=s12tab, iptab=iptab, S=S, ks=ks, TB=TB, E_seconds=E["seconds"], n_h08_cands=int(len(h08_c)), n_cands=int(len(cd))), open("handoff/note_tables.json","w"), indent=1, default=str)
print(tab1); print(sec); print(m2tab); print(cnt_lines); print(h01tab[:1500]); print(m2tab_k); print(survtab); print(TB["n_modes_min"], TB["n_modes_max"], ks["sr"], ks["q_band"], S["sr"], S["q_band"])
