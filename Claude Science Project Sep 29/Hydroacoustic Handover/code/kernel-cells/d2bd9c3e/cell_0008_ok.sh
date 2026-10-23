cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 1,120p prepare/per_impact_lnl.py
echo =====DRIVER
cat prepare/run_j_driver.py
echo =====CORESET
sed -n 1,30p prepare/core_set_windows.py