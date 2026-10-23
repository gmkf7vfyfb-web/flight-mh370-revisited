cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "option\|loglik\|weight\|push\|dive\|p_dive\|surviv" prepare/per_impact_lnl.py | head -60
echo ======
R=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
ls $R; ls $R/run-j-waypoints | head -5; ls $R/run-j-waypoints/seed-1; cat $R/run-j-waypoints/seed-1/COLUMNS.txt
ls $R/summary 2>/dev/null | head; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/ | head -30