cd work; python standin-scripts/rhyd_mix.py result/per_seed.json /Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/summary/mixture.json result/rhyd_mixture.json; python - <<'E'
import json, numpy as np
o=json.load(open("result/rhyd_mixture.json"))
z=np.load("/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/sources-0019-r600-bto-only.npz")
print("pleiades pfam rw", dict(zip(z["stratum_names"], np.round(z["p_family_reweighted"],4))))
for opt,d in o.items():
    print("==",opt, "pf_rw", {k[5:]:round(v,4) for k,v in d["p_family_reweighted"].items()}, "lnZ", {k[5:]:round(v,3) for k,v in d["ln_Z0019_per_family"].items()}, "lnZ sd",{k[5:]:round(v,3) for k,v in d["ln_Z0019_seed_sd"].items()})
    print(" ess", {k[5:]:int(v) for k,v in d["ess_flight"].items()}, {k[5:]:int(v) for k,v in d["ess_H"].items()}, "nc", {k[5:]:round(v,4) for k,v in d["not_computed_weight"].items()})
    for k,v in d.items():
        if "|" in k and isinstance(v,dict) and "lnR" in v: print("  ",k, round(v["lnR"],4), "se",round(v["split_half_se"],4), "max",round(v["split_half_max"],4), v["reading"], "|", v["reading_lo"], "..", v["reading_hi"])
    print("  per stratum rw", {k[5:]:round(x,3) for k,x in d["reweighted|per_stratum_A"].items()})
E