import pandas as pd, json, numpy as np
C=pd.read_csv(O+"candidates.csv"); L=pd.read_csv(O+"likelihood_ratio.csv")
s=json.load(open(O+"summary.json")); d=json.load(open(O+"h01w_time_discriminant.json"))
comp=C[C.computable==True]
print("pre-registered rows:",len(C),"computable:",len(comp),"not computable:",int((C.computable==False).sum()))
pr=comp[comp.role=="primary"]
print("primary computable:",len(pr))
for tier,a in [("screen",0.3),("mark",0.1),("report",0.05)]:
    print(f"  <= {a}: panel {(comp.p_panel<=a).sum()}  expected {len(comp.dropna(subset=['p_panel']))*a:.1f}")
print("\nbelow report tier:")
print(comp[comp.p_panel<=0.05][["station","option","statistic","observed","p_panel","indep_rank_panel","n_indep_panel","peak_utc"]].to_string(index=False))
print("\npooled below report:")
print(comp[comp.p_pooled<=0.05][["station","option","statistic","p_pooled","indep_rank_pooled"]].to_string(index=False))
print("\nenergy GJ:", {k:round(v["e_q50"]/1e9,3) for k,v in s["dive_energy"].items()})
print("ess:", {k:f"{v['ess']:.3e}" for k,v in s["dive_energy"].items()})
print("LR range:", L.lr_nondetection.min(), L.lr_nondetection.max())
print("verdict:", d["verdict"], "| panel max", d["panel_max"]["t_utc"])
