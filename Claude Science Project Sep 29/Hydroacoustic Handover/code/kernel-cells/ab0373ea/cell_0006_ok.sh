P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 235,282p "$P"/tl_grid_table.py
echo ====
sed -n 96,130p "$P"/run_j_levels.py | grep -n "RD\|KEYS\|RECEIVERS\|BANDS\|Z_REF\|ETAS\|THR\|N_DRAWS" 
sed -n 480,532p "$P"/run_j_levels.py
echo ====
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/ /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/levels | head -40
python -c "import json;d=json.load(open('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/run.json'));print({k:v for k,v in d.items() if k!='keys'}); print(list(d['keys'])[:3])"
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_grid_run_j" "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/levels_run_j"