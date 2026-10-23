H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "OHASISBIO\|RX_ORDER" "$H/prepare/run_j_windows.py" | head; grep -n "^OHASISBIO" -A12 "$H/prepare/run_j_windows.py"
ls -R "$H/results-data/digitised/royer-2016" | head -80; cat "$H/results-data/digitised/MANIFEST.csv" | grep -i royer | head