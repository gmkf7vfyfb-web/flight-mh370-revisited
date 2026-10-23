H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; S="$H/results-data/searches_run_j"
python - <<'EOF'
import pandas as pd, numpy as np, json
S="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/searches_run_j"
c=pd.read_csv(f"{S}/imos/imos_candidates.csv")
print(c.shape, c.receiver.value_counts().to_dict())
m=c[c.detector=="M1b"]; print("M1b rows", len(m)); print(m[["receiver","time_utc","t_unix","p","label","in_window_sofar"]].sort_values("p").to_string(index=False))
print(open(f"{S}/coincidence/coincidence_summary.csv").read()[:1500])
r=pd.read_csv(f"{S}/named/royer_verdicts.csv"); print(r.to_string())
print(pd.read_csv(f"{S}/named/poster_boxes.csv").to_string())
print(open(f"{S}/geometry/lags.csv").read()[:600])
z=np.load("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz"); print(z.files); 
fe=json.load(open("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/family-evidence-run-j.json")); print(list(fe), fe.get("p_core"))
EOF
grep -n "def band_fraction" -A 12 "$H/prepare/imos_stageB_map.py" | head -20