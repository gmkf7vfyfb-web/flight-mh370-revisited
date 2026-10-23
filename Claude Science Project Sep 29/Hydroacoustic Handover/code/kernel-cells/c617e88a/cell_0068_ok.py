import json, numpy as np, os
os.chdir("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/c617e88a-f70d-4d8a-847b-7a608fe526f4")
PW={o: json.load(open(f"work/power/{o}/power_check.json")) for o in ["r600-bto-only","held-out"] if os.path.exists(f"work/power/{o}/power_check.json")}
p=PW["r600-bto-only"]
for s,v in p["windows"].items():
    r=v["reweighted"]; print(s, round(r["ovl"],3), [round(x/60,1) for x in r["q_flight"]], [round(x/60,1) for x in r["q_H"]], r["mean_pd_flight"] and round(r["mean_pd_flight"],3), r["mean_pd_H"] and round(r["mean_pd_H"],3), [round(x,1) for x in r["baz_q_flight"]])
for sc,v in p["synthetic"].items():
    for h in ("H","noH"):
        for lab in ("reweighted","fixed"):
            r=v[h][lab]; print(sc,h,lab, round(r["mean"],3), "+-",round(r["mc_se_mean"],3), "sd",round(r["sd"],3), [round(x,2) for x in r["q"]], r["p_abs_ge_0p5"], r["p_abs_ge_1"], r["p_abs_ge_2p3"], round(r["mean_p_any_signal"],3), round(r["mean_events"],1))
print(p["not_computed"], "apply_figure_style" in dir())