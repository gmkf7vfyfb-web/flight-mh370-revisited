def load_rows(p): return list(csv.DictReader(open(p/"windows_by_arm.csv")))
RowsM=load_rows(O/"mixture"); Rows289=load_rows(MW)
S289=json.load(open(MW/"summary.json"))["arms"]
SS={s:json.load(open(O/s/"summary.json"))["arms"] for s in STR}
print("unconverged rows mix", sum(r["converged"]=="no" for r in RowsM), len(RowsM), "| 289", sum(r["converged"]=="no" for r in Rows289))
for s in STR:
    rr=load_rows(O/s); print(s, "unconv", sum(r["converged"]=="no" for r in rr))
sel=[r for r in RowsM if r["variant"] in("alive","silent") and int(r["ess_pooled"])>=1000]
uc=[r for r in sel if r["converged"]=="no"]
print("ESS>=1000 alive/silent rows", len(sel), "unconv", len(uc), "max lo spread", max(float(r["seed_spread_q0p5_s"]) for r in sel), "hi spread range unconv", min(float(r["seed_spread_q99p5_s"]) for r in uc), max(float(r["seed_spread_q99p5_s"]) for r in uc))
print(sorted({(r["arm"].split("__")[1]) for r in uc}))
# held-out impact time table, mixture + strata + 289
for v in ("","+alive","+silent"):
    k="none__other"+v
    print(k, "MIX", M[k]["impact_q_pooled_utc"][0],M[k]["impact_q_pooled_utc"][4],M[k]["impact_q_pooled_utc"][-1], "| 289", S289[k]["impact_q_pooled_utc"][0],S289[k]["impact_q_pooled_utc"][4],S289[k]["impact_q_pooled_utc"][-1], "|", " ".join(SS[s][k]["impact_q_pooled_utc"][4] for s in STR))
for k in ["both_startup-offset__fuel-exhaustion","both_no-offset__other"]:
    print(k, [round(M[k+v]["ess_mixture_kish"]) for v in ("","+alive","+silent")], round(S289[k]["ess_pooled"]))