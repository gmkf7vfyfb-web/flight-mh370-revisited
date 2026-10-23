cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python3 -c "
import json
for f in ['results-data/stageA/summary.json','results-data/stageA/summary_union.json']:
    d=json.load(open(f)); print('==',f)
    for k in ['days','targets','n_inj','excluded','n_background','thresholds']:
        print(' ',k,'=',json.dumps(d.get(k))[:400])
"
echo "=== mh370_windows_extended_null.csv ==="; head -3 results-data/stageA/mh370_windows_extended_null.csv; wc -l results-data/stageA/mh370_windows_extended_null.csv
echo "=== imos_detectors.py docstring ==="; sed -n 1,45p prepare/imos_detectors.py