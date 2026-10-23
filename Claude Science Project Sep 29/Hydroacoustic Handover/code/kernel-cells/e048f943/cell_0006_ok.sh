cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics
ls prepare/ | tr '\n' ' '; echo; echo
wc -l prepare/per_impact_lnl.py prepare/run_j_windows.py prepare/imos_noise.py prepare/blackman_noise.py prepare/tl_grid_table.py prepare/tl_grid_evidence.py prepare/lhyd.py 2>&1
ls results-data/tl_grid_run_j/ results-data/windows_run_j/ 2>&1
echo ---
cd ../../../../..; cd repo/"Claude Science Project Sep 29"
grep -n "^## 2026-10-2[12]" coordination/architecture.md | tail -20