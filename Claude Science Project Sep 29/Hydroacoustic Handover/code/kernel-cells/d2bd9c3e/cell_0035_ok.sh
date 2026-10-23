cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import numpy as np, json, sys; sys.path.insert(0,'.'); import run_j_windows as R
z=np.load('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows/run-j-free/seed-1.npz'); m=json.loads(str(z['meta']))
for k in ['D0/p0.5','D2/p0.5','D3/p0.5','D4/p0.5','D0/p0','D0/p1']:
    s=m['sums'][k]; print(k, 'Z=%.4g ESS=%.0f'%(s['sum'], s['sum']**2/s['sum2']), {f:'%.3f'%(v[0]/s['sum']) for f,v in s['fam'].items()})
    for nm in ['impact','H01W/SOFAR','H08S/SOFAR','3376/SOFAR','H01W/AGW']:
        print('   ',nm,[R.hms(v) for v in m['quant'][k][nm]])
print(m['beyond']['D0/p0.5/impact'], m['res']['logon'])
EOF