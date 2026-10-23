H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - <<'EOF'
import json
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
tp=json.load(open(f"{H}/results-data/tl_grid_run_j/table_points.json")); ks=list(tp); print(len(ks), ks[:3], tp[ks[0]])
a=json.load(open(f"{H}/results-data/windows_run_j/arc_lat_lon.json")); v=a['D0/p0.5']; print(type(v), (list(v)[:3] if isinstance(v,dict) else v[:3]))
import csv
rows=[r for r in csv.reader(open(f"{H}/data/stations.csv")) if r and not r[0].startswith("#")]; print(rows[0], rows[1])
EOF
grep -n "ETA_PRIOR\|log-uniform\|logu" "$H/prepare/injection_recovery_run_j/prereg.py" | head -5
grep -n "C_SOFAR" "$H/prepare/run_j_windows.py" | head -3
cat /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/run.json | python -c "import json,sys; d=json.load(sys.stdin); print(list(d)[:20]); print(d.get('code_revision'), d.get('prior_track'), d['config']['hypotheses']['end-of-flight']['logon'])"