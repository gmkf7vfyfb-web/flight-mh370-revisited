mixj=json.load(open(N/"summary/mixture.json"))
dmax=0; worst=None; n=0
for s in STR:
    S=json.load(open(O/s/"summary.json"))["arms"]
    for key,v in ss[s]["options"].items():
        if key in S:
            d=abs(S[key]["ess_pooled"]-v["ess_total"])/v["ess_total"]; n+=1
            if d>dmax: dmax, worst = d,(s,key,S[key]["ess_pooled"],v["ess_total"])
print("ESS vs EoF sweep summary: n",n,"max rel diff",dmax,worst)
M=json.load(open(O/"mixture/summary.json"))["arms"]
dm=0;nm=0
for key,v in mixj["options"].items():
    if key in M and "ess" in v:
        nm+=1; dm=max(dm,abs(M[key]["ess_mixture_kish"]-v["ess"])/v["ess"])
print("mixture ESS vs mixture.json: n",nm,"max rel",dm)
print("max mass beyond grid", max(a["mass_beyond_grid"] for a in M.values()))
# shares by variant (mixture)
for k in ["none__other","none__other+alive","none__other+silent","none__fuel-exhaustion","none__fuel-exhaustion+alive","r600-bto__other+alive"]:
    a=M[k]; print(k, round(a["ess_mixture_kish"]), round(a["share_before_001937"],4), round(a["share_after_011556"],4), a["impact_q_pooled_utc"][0], a["impact_q_pooled_utc"][4], a["impact_q_pooled_utc"][-1])