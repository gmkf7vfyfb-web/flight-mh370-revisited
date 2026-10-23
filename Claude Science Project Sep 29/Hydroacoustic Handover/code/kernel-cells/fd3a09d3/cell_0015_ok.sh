cd /Users/pete/Downloads/mh370-exchange
grep -n -i -B2 -A12 "arc-grid" searched-areas/run-j-supplement/README.md | head -60
echo ==== bin; ls end-of-flight/bin; 
python - <<'EOF'
import numpy as np, json
z=np.load('searched-areas/run-j-supplement/arc-grid.npz'); print(float(z['south']),float(z['west']),float(z['step']),int(z['rows']),int(z['cols']))
a=z['arc']; print(np.nanmin(a),np.nanmax(a), np.isnan(a).mean())
r=json.load(open('end-of-flight/run-j/run-j-waypoints/seed-1/run.json')); print(list(r.keys())[:30]); print({k:r[k] for k in r if k in ('prior_track','config','base_config','impact_columns_dtype','n_rows','rows')})
EOF
head -c 600 end-of-flight/run-j/README.md; echo; grep -n -i "impacts32\|compact\|float32\|dtype\|scale" end-of-flight/run-j/README.md | head -20