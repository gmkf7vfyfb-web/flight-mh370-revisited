
E=json.load(open(OUT+"/eta/eta_map.json"))
print("ess", {k:round(v) for k,v in E["ess"].items()}, "thin", E["thin"], "rows", E["n_rows"], "north pending share", round(E["share_north_of_20S_pending"],4))
print("blocked share", {k:round(v,3) for k,v in E["blocked_share"].items()})
print("bmed abs", {k:round(v,1) for k,v in E["bg_median_abs_db_re_uPa"].items()})
for k in ["D0/p0.5|alpha0.01|nocal","D0/p0.5|alpha0.01|cal","D0/p0.5|alpha0.05|cal","D0/p0.5|alpha0.001|cal","D0/p0|alpha0.01|cal","D0/p1|alpha0.01|cal","D2/p0.5|alpha0.01|cal","D3/p0.5|alpha0.01|cal","D4/p0.5|alpha0.01|cal"]:
    print(k, "eta50=%.2e"%E["eta50"][k]["eta50"], "Pd(anchor)=%.3f"%E["pd_any_at_anchor"][k], {d:round(v,3) for d,v in E["pd_any_by_decade"][k].items()})
print("by receiver", {k:("%.2e"%v["eta50"] if v["eta50"] else None, round(v["pd_at_anchor"],3)) for k,v in E["eta50_by_receiver"].items()})
lb=pd.read_csv(OUT+"/eta/eta50_by_lat_band.csv"); print(lb[lb.n>0][["lat_lo","share","n","eta50","pd_any_at_anchor"]].to_string())
