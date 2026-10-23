H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
cat "$H/results-data/composition_run_j/v2/coincidence_locus.csv"; cat "$H/results-data/composition_run_j/v2/coincidence_summary.json" | head -c 3000; echo
grep -n "locus" "$H/prepare/composition_run_j/reduce.py" | head -20; ls "$H/prepare/composition_run_j" "$H/prepare/searches_run_j"; ls "$H/data" "$H/data/imos" | head -40