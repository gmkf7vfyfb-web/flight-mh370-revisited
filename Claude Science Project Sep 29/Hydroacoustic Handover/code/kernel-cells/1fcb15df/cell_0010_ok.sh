H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 205,245p "$H/prepare/composition_run_j/reduce.py"
grep -n "def \|^[A-Z_]* =" "$H/prepare/composition_run_j/common.py" | head -60
cat "$H/data/stations.csv" | head -30; head -5 "$H/data/imos/recordings.csv"; wc -l "$H/data/imos/recordings.csv"