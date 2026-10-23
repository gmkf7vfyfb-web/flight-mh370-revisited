O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated; H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - <<'EOF'
import json,glob,numpy as np
O="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated"
parts=[json.load(open(f)) for f in glob.glob(f"{O}/_parts/*.json") if not f.endswith("supplement.json")]
rows=sum(p["rows"] for p in parts); nc=sum(p["not_computed"] for p in parts); sc=np.average([p["scored_any_share"] for p in parts],weights=[p["rows"] for p in parts])
nz=np.average([p["share_nonzero"]["hydro-lnL-imos-margeta"] for p in parts],weights=[p["rows"] for p in parts])
q=np.array([p["quantiles"]["hydro-lnL-imos-margeta"] for p in parts]); print("rows",rows,"nc",nc,"scored_any(incl IMS)",round(sc,3),"nonzero imos marg",round(nz,3))
print("marg quantiles 0.1/1/50/99/99.9 % (median over seeds):", np.round(np.median(q,0),3), "min over seeds", np.round(q.min(0),2), "max", np.round(q.max(0),2))
q2=np.array([p["quantiles"]["hydro-lnL-imos-eta1e-3"] for p in parts]); print("eta1e-3 quantiles median over seeds:", np.round(np.median(q2,0),3))
print("seconds total", round(sum(p["seconds"] for p in parts)), "code_revision", set(p["run_json"]["code_revision"] for p in parts))
sp=json.load(open(f"{O}/_parts/supplement.json")); print("supplement", sp["rows"], sp["used"], {o: round(v["supplement"]/v["total"],3) for o,v in sp["share"].items()})
s=json.load(open(f"{O}/reduce/summary.json")); print("cands 0.05:", {k:[(c["time_utc"],round(c["p"],3),c["eta_needed"]) for c in v] for k,v in s["candidates"].items() if k.endswith("|0.05") and v})
print("windows", s["scored_windows"]); print("Zrun", s["Zrun_D0_p05"])
h=np.array(s["lnL_hist_D0_p05"]); e=np.array(s["lnL_hist_edges"]); c=np.cumsum(h)/h.sum(); print("D0 p0.5 lnL_marg weighted quantiles 1/5/50/95/99 %:", [round(float(np.interp(qq,c,e[1:])),2) for qq in (.01,.05,.5,.95,.99)], "mass at |lnL|<0.05:", round(float(h[(e[:-1]>=-0.25)&(e[:-1]<0.25)].sum()/h.sum()),3))
EOF
mkdir -p "$H/results-data/composition_run_j" && cp $O/reduce/*.csv $O/reduce/*.json $O/reduce/tables.md "$H/results-data/composition_run_j/" && cp $O/README.txt "$H/results-data/composition_run_j/exchange_README.txt" && du -sh "$H/results-data/composition_run_j"
cd $O && find . -name "*.npy" -o -name "README.txt" -o -name "SHA256SUMS" | grep -v reduce | sort | xargs shasum -a 256 > SHA256SUMS.tmp 2>/dev/null; mv SHA256SUMS.tmp SHA256SUMS; wc -l SHA256SUMS; du -sh $O; df -k /System/Volumes/Data | tail -1