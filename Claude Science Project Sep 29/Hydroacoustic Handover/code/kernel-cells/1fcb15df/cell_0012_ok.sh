H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "^[A-Z_0-9]* *=" "$H/prepare/composition_run_j/prereg.py" | cut -c1-250
grep -n "def receivers" -A25 "$H/prepare/run_j_windows.py" | head -40