set +e
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "=== kraken_tl.py header"; sed -n '1,40p' "$H/prepare/kraken_tl.py" | cut -c1-160
echo "=== external deps across prepare"; grep -rhoE '^(import|from) [a-zA-Z_0-9]+' "$H"/prepare/*.py "$H"/prepare/*/*.py | sort | uniq -c | sort -rn | head -30
echo "=== inputs dir"; ls /Users/pete/Downloads/mh370-inputs/hydroacoustics 2>/dev/null; du -sh /Users/pete/Downloads/mh370-inputs/hydroacoustics/* 2>/dev/null
echo "=== ocean transport calibration paths"; ls /Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration | head; 
echo "=== bathy/ssp sources used"; grep -rn -i -E 'gebco|woa|\.nc\b' "$H/prepare/imos_stageB_tl.py" "$H/prepare/kraken_tl.py" "$H/prepare/exploratory/run_ims_tl.py" | cut -c1-200 | head -12
echo "=== run_j_driver paths"; grep -n -E 'Downloads|exchange|WORKERS|threads|argparse|add_argument' "$H/prepare/run_j_driver.py" | head -20