cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22" && python - <<'EOF'
import pandas as pd, numpy as np
d=pd.read_csv('predictions.csv')
etas=[('0.01','1e-2'),('0.001','1e-3'),('0.00021','2.1e-4 (F-35A anchor)'),('0.0001','1e-4'),('1e-05','1e-5')]
lines=["Predicted 5–40 Hz 1 s SPL at the receiver (dB re 1 µPa, single element; our table, mass-weighted over the run J cells,",
"primary option, cell-median energy and duration; add 4.8 dB for the triad), against our noise proxy. **PREDICTIVE (C1, C2).**","",
"| η | H01W q05 / q50 / q95 | H08S q05 / q50 / q95 |","|---|---|---|"]
def q(rx,col):
    r=d[(d.receiver==rx)&(d['weight_D0_p0.5']>0)]; v=r[col].values; w=r['weight_D0_p0.5'].values; ok=np.isfinite(v)
    o=np.argsort(v[ok]); cv=np.cumsum(w[ok][o])/w[ok].sum(); return [float(np.interp(p,cv,v[ok][o])) for p in (0.05,0.5,0.95)]
for e,lab in etas:
    a=q('H01W',f'spl_1s_db_5-40hz_eta{e}'); b=q('H08S',f'spl_1s_db_5-40hz_eta{e}')
    lines.append(f"| {lab} | {a[0]:.0f} / {a[1]:.0f} / {a[2]:.0f} | {b[0]:.0f} / {b[1]:.0f} / {b[2]:.0f} |")
n=d[d.receiver=='H01W'].iloc[0]['noise_median_db_5-40hz']; n2=d[d.receiver=='H08S'].iloc[0]['noise_median_db_5-40hz']
lines+=["",f"Noise proxy medians (5–40 Hz, 1 s): H01W {n:.1f} dB, H08S {n2:.1f} dB (IMOS 3376 + Blackman 2004 offsets; digitised 2003).",
"**Injection levels requested:** H01W 70–115 dB in 5 dB steps; H08S 55–105 dB in 5 dB steps (received single-element 5–40 Hz 1 s SPL",
"at the pulse peak), so that the full η range 1e-5 to 1e-2 is covered at both stations; the pulse model is `pulse_runj.npz`",
"(H01W range) and, for H08S, the 3,703.5 km envelope template is the shape (a waveform at that range can be supplied on request).",
"Report P_D(level) with 90 % intervals and the false-alarm rate per hour at the same threshold on the control windows."]
t=open('REQUESTS.md').read().replace('<!-- LEVELS -->','\n'.join(lines)); open('REQUESTS.md','w').write(t)
print('\n'.join(lines))
EOF