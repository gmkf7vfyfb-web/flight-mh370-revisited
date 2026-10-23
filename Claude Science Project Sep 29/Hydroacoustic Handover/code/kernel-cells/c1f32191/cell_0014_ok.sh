H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; S="$H/results-data/searches_run_j"
head -3 "$S/imos/imos_windows.csv"; wc -l "$S/imos/imos_windows.csv"
python - <<'EOF'
import json,pandas as pd
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
a=json.load(open(f"{H}/results-data/windows_run_j/arc_lat_lon.json")); print(type(a), (list(a)[:5] if isinstance(a,dict) else a[:3]))
w=pd.read_csv(f"{H}/results-data/searches_run_j/imos/imos_windows.csv"); print(w.receiver.value_counts().to_dict()); print(w.columns.tolist())
p=pd.read_csv(f"{H}/results-data/searches_run_j/panels/panel_windows.csv"); print(p.columns.tolist(), len(p)); print(p.head(2).to_string())
pc=pd.read_csv(f"{H}/results-data/searches_run_j/panels/panel_candidates.csv"); print(pc.columns.tolist()); m=pc[(pc.detector.str.startswith("M1b"))&(pc.p<0.1)]; print(m[["receiver","time_utc","t_unix","detector","p","label"]].to_string())
e=pd.read_csv(f"{H}/results-data/injection_run_j/errors.csv"); print(e.columns.tolist()); print(e[(e.alpha==0.05)&(e.method=="M1b_mf_envelope")&(e.level_db.isin([0.0,5.0,10.0]))].groupby(["receiver","level_db"])[["dt_q05","dt_q95"]].mean().round(2).to_string() if "dt_q05" in e.columns else e.head())
rd=pd.read_csv(f"{H}/results-data/near_limits/ims_ram_delta.csv"); print(rd.head(3).to_string(), rd.path.unique())
EOF
df -k /System/Volumes/Data | tail -1; du -sh /Users/pete/Downloads/mh370-exchange/hydroacoustics/ 2>/dev/null