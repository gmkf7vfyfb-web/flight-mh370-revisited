import json, csv, pathlib, numpy as np
WS=pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/462da3b0-2381-4cf6-84db-fe178606bed4")
O=WS/"out/next-run-b"; N=pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run")
STR=["next-free","next-repro-radar","next-descent-climb","next-routes"]
sq=json.load(open(O/"mixture/per_stratum_quantiles_selfcheck.json"))
QK=["q0.5","q2.5","q5","q25","q50","q75","q95","q97.5","q99.5"]
mism=0; tot=0
for s in STR:
    for r in csv.DictReader(open(O/s/"windows_by_arm.csv")):
        key=r["arm"]+("" if r["variant"]=="plain" else "+"+r["variant"])
        w=sq[s][key][f'{r["receiver"]}|{r["branch"]}']
        tot+=1; mism+= [r[k] for k in QK]!=w
    S=json.load(open(O/s/"summary.json"))["arms"]
    for key,a in S.items():
        tot+=1; mism+= a["impact_q_pooled_utc"]!=sq[s][key]["impact"]
print("selfcheck mismatches", mism, "of", tot)
# ESS cross-check vs EoF sweep summary
ss={s:json.load(open(N/"summary"/f"sweep-summary-{s}.json")) for s in STR}
print(list(ss["next-free"]["options"])[:3], json.dumps(ss["next-free"]["options"]["none__other"])[:600])