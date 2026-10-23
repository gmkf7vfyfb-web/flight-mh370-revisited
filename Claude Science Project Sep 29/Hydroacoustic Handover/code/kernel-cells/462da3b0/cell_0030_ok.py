MW=pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/hydro-wt/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/search_windows/reference-289")
def rec(p): return {(r["variant"],r["receiver"],r["branch"]):r for r in csv.DictReader(open(p/"recommended_windows.csv"))}
R289=rec(MW); RM=rec(O/"mixture"); RS={s:rec(O/s) for s in STR}
rxs=["H01W","H08S","H08N","3315","3376","3250","3274","3275"]
print("rx | var | mix sofar | agw end | ref289 sofar | agw end | n_arms mix/289 | unconv | per-stratum sofar")
for rx in rxs:
    for v in ("alive","silent"):
        m=RM[(v,rx,"sofar")]; ma=RM[(v,rx,"agw")]; r=R289[(v,rx,"sofar")]; ra=R289[(v,rx,"agw")]
        ps=" ".join(f'{RS[s][(v,rx,"sofar")]["window_start"][:5]}-{RS[s][(v,rx,"sofar")]["window_end"][:5]}' for s in STR)
        print(rx,v,m["window_start"][:5]+"-"+m["window_end"][:5], ma["window_end"][:5], r["window_start"][:5]+"-"+r["window_end"][:5], ra["window_end"][:5], m["n_arms"],r["n_arms"], m["any_unconverged"], "|", ps)
# arms in union
print(RM[("alive","H01W","sofar")]["arms"]); print(R289[("alive","H01W","sofar")]["arms"]==RM[("alive","H01W","sofar")]["arms"])