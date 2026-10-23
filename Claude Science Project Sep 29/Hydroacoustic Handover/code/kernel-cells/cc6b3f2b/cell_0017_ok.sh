cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -i "H01W\|H08S" data/stations.csv | head -8; head -1 data/stations.csv
grep -n "BOTTOM\s*=\|bottom\s*=\s*dict\|cp=" prepare/air9_tl_validation.py prepare/imos_stageB_tl.py | head -5
grep -n "FG\s*=\|fg\s*=\s*dict" prepare/air9_tl_validation.py | head -3
cat /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt | head -30
ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/