
RUNO=OUT+"/run"; S=json.load(open(RUNO+"/summary.json")); F=json.load(open(RUNO+"/fits.json"))
print("n_null", S["n_null_windows"], "\np_floor", {k:round(v,5) for k,v in S["p_floor"].items()})
print("bmed", {k:round(v,1) for k,v in S["bg_median_level_db"].items()}, "\nabs_off", {k:round(v,1) for k,v in S["abs_offset_db"].items()})
print("bg stats", {k:(round(v['q10']-v['median'],1), round(v['q90']-v['median'],1), round(v['q99']-v['median'],1)) for k,v in S["bg_level_stats"].items()})
rows=[]
for k,v in F.items():
    rx,m,a,t=k.split("|")
    rows.append(dict(rx=rx,method=m,alpha=float(a),tau=float(t),L50=v.get("L50_re_noise_db"),L90=v.get("L90_re_noise_db"),reached=v.get("reached"),res=v.get("resolvable"),pd0=v.get("pd_at_0db"),pd10=v.get("pd_at_10db")))
FD=pd.DataFrame(rows)
piv=FD[FD.method=="M1b_mf_envelope"].pivot_table(index=["rx","tau"],columns="alpha",values="L50"); print(piv.round(1).to_string())
print(FD[(FD.alpha==0.01)].pivot_table(index=["rx","tau"],columns="method",values="L50").round(1).to_string())
print(FD[(FD.alpha==0.01)&(FD.method=="M1b_mf_envelope")][["rx","tau","pd0","pd10"]].to_string())
