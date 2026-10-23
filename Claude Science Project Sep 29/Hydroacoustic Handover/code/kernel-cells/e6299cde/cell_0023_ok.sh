cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry
python - <<'EOF'
import numpy as np
z=np.load('sample.npz'); E=z['E_j']; src=z['source']; w=z['w_D0']
for s in (0,1):
    m=src==s; print(s, m.sum(), 'finite E', np.isfinite(E[m]).mean(), 'w share', w[m].sum())
m=np.isfinite(E); 
o=np.argsort(E[m]); c=np.cumsum(w[m][o]); c/=c[-1]; print('E med (finite only) %.3e GJ'%(np.interp(0.5,c,E[m][o])/1e9), 'q5 %.2e q95 %.2e'%(np.interp(0.05,c,E[m][o])/1e9, np.interp(0.95,c,E[m][o])/1e9))
EOF
cd "$OLDPWD/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('geometry.py').read()
s=s.replace('''def wq(x, w, qs):
    o = np.argsort(x); x, w = x[o], w[o]''','''def wq(x, w, qs):
    m = np.isfinite(x) & (w > 0); x, w = x[m], w[m]
    o = np.argsort(x); x, w = x[o], w[o]''')
open('geometry.py','w').write(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python geometry.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry 2>&1 | tail -1
python -c "
import json;e=json.load(open('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry/energy.json'))
for o in e: print(o, {k:'%.2e'%v for k,v in e[o]['E_j_q'].items()})"