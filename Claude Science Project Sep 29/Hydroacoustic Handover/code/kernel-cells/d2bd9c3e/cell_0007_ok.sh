cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls prepare/ | tr '\n' ' '; echo; ls data/ results-data/ | head -60
echo ---- search_windows docstring
sed -n 1,80p prepare/search_windows.py
echo ---- files
ls prepare/search_windows_mixture* prepare/core_set_windows.py prepare/per_impact_lnl.py prepare/run_j_driver.py
wc -l prepare/search_windows.py prepare/core_set_windows.py prepare/search_windows_mixture*.py prepare/per_impact_lnl.py prepare/run_j_driver.py