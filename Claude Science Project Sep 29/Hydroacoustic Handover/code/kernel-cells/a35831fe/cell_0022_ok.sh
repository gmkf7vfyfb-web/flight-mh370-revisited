cd "hyd/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"; python -c "
import json;d=json.load(open('windows_run_j/run.json'));print(json.dumps(d)[:2500])"; echo; head -5 windows_run_j/coverage.csv; echo; grep -rn -i "lat" searches_run_j/geometry/run.json | head; python -c "
import json;d=json.load(open('searches_run_j/geometry/run.json'));print(json.dumps(d)[:2000])"