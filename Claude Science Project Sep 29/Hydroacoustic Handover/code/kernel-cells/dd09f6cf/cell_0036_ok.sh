python -c "import pyproj;print(pyproj.__version__)" 2>&1 | tail -1; sed -n 1,60p lib/compact_impacts.py | cut -c1-220; python - <<'E'
import json;r=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/run.json'));print(list(r.keys())[:30]); print({k:r[k] for k in r if 'epoch' in k.lower() or 't0' in k.lower()})
E