cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 148,200p prepare/imos_detectors.py
echo "=== prereg calibration_files ==="; python3 -c "
import json;d=json.load(open('data/imos/preregistration.json'));print(json.dumps(d['calibration_files'],indent=1)[:500]); print(json.dumps(d['loggers'],indent=1)[:600])"
echo "=== noise_summary keys ==="; python3 -c "
import json;d=json.load(open('results-data/imos1d/noise_summary.json'));print(list(d.keys())[:10]);
k=list(d.keys())[0];print(k, list(d[k].keys())[:30] if isinstance(d[k],dict) else type(d[k]))"