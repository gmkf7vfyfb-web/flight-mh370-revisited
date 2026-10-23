cd /Users/pete/Downloads/mh370-exchange
python - <<'EOF'
import json, numpy as np
r=json.load(open('end-of-flight/run-j/run-j-waypoints/seed-1/run.json')); c=r['compact']
print({k:(v if k!='derived_columns' else '...') for k,v in c.items()})
X=np.load('end-of-flight/run-j/run-j-waypoints/seed-1/impacts32.npy', mmap_mode='r'); print(X.shape, X.dtype)
cols=open('end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt').read().split()
for k in ('latitude_deg','longitude_deg','arc_distance_nm','weight','t_impact_s','mass_kg'):
    i=cols.index(k); v=np.asarray(X[:200000,i],float); print(k, np.nanmin(v), np.nanmedian(v), np.nanmax(v))
z=np.load('end-of-flight/run-j/run-j-waypoints/seed-1/tau90_v1.npz'); print(z.files, {k:z[k].shape for k in z.files})
EOF
grep -n "compact-reader\|compact_impacts" "/Users/pete/.."/dev/null hydroacoustics/run-j/*/README.txt 2>/dev/null | head -5
ls hydroacoustics/run-j/; ls hydroacoustics/run-j/primary-tau-eof | head; grep -n "compact" hydroacoustics/run-j/primary-tau-eof/README.txt | head -5