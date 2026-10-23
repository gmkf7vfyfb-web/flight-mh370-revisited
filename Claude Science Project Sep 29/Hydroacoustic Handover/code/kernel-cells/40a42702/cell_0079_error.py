
import prereg as R
exec(open("/dev/stdin").read()) if False else None
rowsA=[]
for rx in R.RECEIVERS:
    babs=bmed[rx]+abs_off[rx]
    r={"Receiver":NAME[rx],"Background":S["background"][rx],"Null windows":S["n_null_windows"][rx],"p floor":f"{S['p_floor'][rx]:.4f}","Median band level (dB re 1 µPa, 5–40 Hz, 1 s)":f"{babs:.1f}"}
    for a in R.ALPHAS:
        v=F.get(f"{rx}|M1b_mf_envelope|{a}|{taus[1]}",{}); l=v.get("L50_re_noise_db")
        r[f"L50 α={a}"]= "n/r" if not v.get("resolvable",True) else (f"{l:.1f}" if l is not None else "not reached")
    rowsA.append(r)
TA=pd.DataFrame(rowsA); print(TA.to_markdown(index=False))
rowsB=[]
for rx in R.RECEIVERS:
    r={"Receiver":NAME[rx]}
    for m,lab in [("M1b_mf_envelope","matched filter"),("M0a_stalta","STA/LTA"),("M0b_bandenergy","band energy")]:
        v=F.get(f"{rx}|{m}|0.01|{taus[1]}",{}); r[f"{lab} L50"]=f1(v.get("L50_re_noise_db")) if v.get("L50_re_noise_db") is not None else "not reached"; r[f"{lab} L90"]=f1(v.get("L90_re_noise_db")) if v.get("L90_re_noise_db") is not None else "—"
    rowsB.append(r)
print(); print(pd.DataFrame(rowsB).to_markdown(index=False))
rowsC=[]
for rx in R.RECEIVERS:
    r={"Receiver":NAME[rx]}
    for t in taus:
        v=F.get(f"{rx}|M1b_mf_envelope|0.01|{t}",{}); r[f"τ={t:.2f} s"]=f1(v.get("L50_re_noise_db"))
    v=F.get(f"{rx}|M1b_mf_envelope|0.01|{taus[1]}",{}); r["P_D at 0 dB"]=f"{v.get('pd_at_0db'):.2f}"; r["P_D at +10 dB"]=f"{v.get('pd_at_10db'):.2f}"
    rowsC.append(r)
print(); print(pd.DataFrame(rowsC).to_markdown(index=False))
g=PD[(PD.method=="M1b_mf_envelope")&(PD.alpha==0.01)&np.isclose(PD.tau_s,taus[1])].pivot(index="level_re_noise_db",columns="receiver",values="pd")[R.RECEIVERS]
g.index=[f"{v:+.1f}" for v in g.index]; print(); print(g.round(2).to_markdown())
print(); print({k:(round(v['q10']-v['median'],1), round(v['q90']-v['median'],1), round(v['q99']-v['median'],1), v['n_1s']) for k,v in S["bg_level_stats"].items()})
print(S["own8mar_3315"], S["own8mar_3275"]); print(S["seconds"]["total"], S["n_injections"])
