sleep 60
cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
python - <<EOF
import numpy as np, json, glob, pathlib, os
bad=[]; tot={}; nrows=0
for f in sorted(glob.glob('$OUT/draws/*/seed-*.npz')):
    try:
        z=np.load(f); m=json.loads(str(z['meta'])); assert len(z.files)==133, len(z.files)
        for k in m['sums']:
            n=m['sums'][k]['n_draws']; assert len(z[f'{k}/idx'])==n and len(z[f'{k}/E'])==n
            tot[k]=tot.get(k,0)+n
        _ = z['D0/p0.5/lat'][:]  # force decompress
        nrows+=m['res']['n']
    except Exception as e:
        bad.append((f,str(e)[:80]))
print('bad', bad); print('rows', nrows); print('strata draws per key', tot)
EOF
du -sh $OUT/draws; tail -qn1 $OUT/logs/draw-*.log