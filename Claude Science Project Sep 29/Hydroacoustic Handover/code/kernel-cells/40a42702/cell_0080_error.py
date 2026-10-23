
def md(df):
    cols=list(df.columns); out=["| "+" | ".join(map(str,cols))+" |","|"+"---|"*len(cols)]
    for _,r in df.iterrows(): out.append("| "+" | ".join(str(r[c]) for c in cols)+" |")
    return "\n".join(out)
print(md(TA)); print(); print(md(pd.DataFrame(rowsB)))
rowsC=[]
for rx in R.RECEIVERS:
    r={"Receiver":NAME[rx]}
    for t in taus:
        v=F.get(f"{rx}|M1b_mf_envelope|0.01|{t}",{}); r[f"τ={t:.2f} s"]=f1(v.get("L50_re_noise_db"))
    v=F.get(f"{rx}|M1b_mf_envelope|0.01|{taus[1]}",{}); r["P_D at 0 dB"]=f"{v.get('pd_at_0db'):.2f}"; r["P_D at +10 dB"]=f"{v.get('pd_at_10db'):.2f}"
    rowsC.append(r)
print(); print(md(pd.DataFrame(rowsC)))
g=PD[(PD.method=="M1b_mf_envelope")&(PD.alpha==0.01)&np.isclose(PD.tau_s,taus[1])].pivot(index="level_re_noise_db",columns="receiver",values="pd")[R.RECEIVERS]
g=g.round(2); g.insert(0,"Level re noise (dB)",[f"{v:+.1f}" for v in g.index]); print(); print(md(g))
print(); print({k:(round(v['q10']-v['median'],1), round(v['q90']-v['median'],1), round(v['q99']-v['median'],1), v['n_1s']) for k,v in S["bg_level_stats"].items()})
print(S["own8mar_3315"], S["own8mar_3275"]); print(S["seconds"]["total"], S["n_injections"])
