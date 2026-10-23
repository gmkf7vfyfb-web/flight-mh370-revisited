cd .tmp/standin; python - <<'EOF'
import json, numpy as np
S=json.load(open("full_tau/summary.json")); S["next-c-free/seed-1"]["baseline_reproduction_max_abs_diff_smoke"]=0.0
json.dump(S,open("full_tau/summary.json","w"),indent=1)
rows=[]
for st in ["next-c-free","next-c-repro-radar","next-c-descent-climb","next-c-routes"]:
    ks=[k for k in S if k.startswith(st+"/")]
    f=lambda a,b: np.array([S[k][a][b] for k in ks])
    print(f"| {st} | {len(ks)} | {f('scenario_tau','share_le_m1').mean():.4f} | {f('eof_tau90','share_le_m1').mean():.4f} | {f('scenario_tau','mean').mean():+.3f} | {f('eof_tau90','mean').mean():+.3f} | {f('paired_diff','mean').mean():+.4f} (seed sd {f('paired_diff','mean').std(ddof=1):.4f}) | {f('paired_diff','q01').min():+.2f} / {f('paired_diff','q99').max():+.2f} | {f('scenario_tau','q01').mean():.2f} / {f('eof_tau90','q01').mean():.2f} | {f('scenario_tau','q99').mean():.2f} / {f('eof_tau90','q99').mean():.2f} | {f('tau90','share_above_10').mean():.3f} |")
EOF
python chart_tau.py full_tau/summary.json "32 seeds; open: scenario prior, filled: water-entry model" && echo ok