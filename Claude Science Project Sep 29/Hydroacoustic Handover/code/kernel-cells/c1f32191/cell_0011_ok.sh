H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; P="$H/prepare"
grep -n "^def \|^    def \|^[A-Z_0-9]* = " "$P/tl_grid_table.py" | head -40
echo ---- run_j_windows
grep -n "^def \|^[A-Z_0-9]* = " "$P/run_j_windows.py" | head -60
echo ---- lhyd consts
grep -n "^[A-Z_0-9]* *= " "$P/exploratory/pleiades_test/lhyd.py" | head -40
echo ---- recordings
head -3 "$H/data/imos/recordings.csv"; wc -l "$H/data/imos/recordings.csv"
echo ---- candidates
ls "$H/results-data/searches_run_j/imos" "$H/results-data/searches_run_j/coincidence" "$H/results-data/searches_run_j/named" "$H/results-data/searches_run_j/geometry" "$H/results-data/searches_run_j/panels"
head -2 "$H/results-data/searches_run_j/imos/imos_candidates.csv"
cat "$H/results-data/searches_run_j/prereg_windows.csv"
echo ---- fits keys
python - <<'EOF'
import json
f=json.load(open("hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/injection_run_j/fits.json"))
ks=list(f); print(len(ks), ks[:3]); print(f[ks[0]])
s=json.load(open("hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/injection_run_j/summary.json"))
print(list(s)); print(s["taus"], s["bg_median_level_db"], s["abs_offset_db"]); print({k:list(v)[:3] for k,v in s["t_eff_s"].items()})
EOF
ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/ /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary /Users/pete/Downloads/mh370-exchange/end-of-flight/bin 2>/dev/null | head -40
cat /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt | tr '\n' ' '