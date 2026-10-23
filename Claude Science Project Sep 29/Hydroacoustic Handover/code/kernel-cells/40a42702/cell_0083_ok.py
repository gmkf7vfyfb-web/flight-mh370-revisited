
E=json.load(open(OUT+"/eta/eta_map.json"))
print("ess", {k:round(v) for k,v in E["ess"].items()}, "tl extrap share", round(E["share_tl_extrapolated_imos"],4))
print("blocked share", {k:round(v,3) for k,v in E["blocked_share"].items()})
rows=[]
for o in R.OPTIONS:
    for p in R.PS:
        k=f"{o}/p{p:g}"; r={"Option / p":k, "ESS (thin)":round(E["ess"][k])}
        for a in (0.01,0.05,0.001):
            v=E["eta50"][f"{k}|alpha{a}|cal"]["eta50"]; r[f"η50 α={a}"]=f"{v:.1e}" if v else "not reached"
        r["η50 α=0.01 no cal err"]=f"{E['eta50'][f'{k}|alpha0.01|nocal']['eta50']:.1e}"
        r["P_D(any) at F-35A anchor, α=0.01"]=f"{E['pd_any_at_anchor'][f'{k}|alpha0.01|cal']:.2f}"
        rows.append(r)
print(md(pd.DataFrame(rows)))
k="D0/p0.5|alpha0.01|cal"; print(); print(md(pd.DataFrame([{"η":d,"P_D(any), α 0.01":round(v,3),"α 0.05":round(E["pd_any_by_decade"]["D0/p0.5|alpha0.05|cal"][d],3),"α 0.001":round(E["pd_any_by_decade"]["D0/p0.5|alpha0.001|cal"][d],3)} for d,v in E["pd_any_by_decade"][k].items()])))
print(); print(md(pd.DataFrame([{"Receiver":NAME[k],"η50 (alone)":(f"{v['eta50']:.1e}" if v["eta50"] else "not reached below 1e-2"),"P_D at anchor":round(v["pd_at_anchor"],3)} for k,v in E["eta50_by_receiver"].items()])))
lb=pd.read_csv(OUT+"/eta/eta50_by_lat_band.csv"); lb2=lb[lb.n>0].copy(); lb2["eta50"]=lb2.eta50.map(lambda v: f"{v:.1e}" if pd.notna(v) else "not reached"); lb2["share"]=lb2.share.round(4); lb2["pd_any_at_anchor"]=lb2.pd_any_at_anchor.round(3)
print(); print(md(lb2[["lat_lo","lat_hi","share","n","eta50","pd_any_at_anchor"]]))
