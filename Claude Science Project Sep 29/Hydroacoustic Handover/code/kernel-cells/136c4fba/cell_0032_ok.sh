cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls data/imos/ ; echo "=== recordings.csv ==="; head -3 data/imos/recordings.csv; wc -l data/imos/recordings.csv
python3 -c "
import pandas as pd
r=pd.read_csv('data/imos/recordings.csv',parse_dates=['start_logger'])
print(r.columns.tolist()); print(r.groupby(['logger','role']).size())
"
echo "=== preregistration.json keys ==="; python3 -c "
import json;d=json.load(open('data/imos/preregistration.json'));print(list(d.keys()))"
echo "=== parse_meta / clock_err ==="; sed -n '/^def parse_meta/,/^def clock_err/p' prepare/imos_preregistration.py | head -30