cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
head -5 levels_run_j/eta_50.csv; wc -l levels_run_j/eta_50.csv; head -5 injection_run_j/eta50_by_lat_band.csv
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/levels-rerun-v2/
head -5 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/levels-rerun-v2/eta_50*.csv 2>/dev/null
grep -n -i "eta_50\|η₅₀\|eta50\|6e-4\|6 × 10⁻⁴\|6.0e-04" "../../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md" "../../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-imos-ram-grid.md" 2>/dev/null | cut -c1-400 | head -20