mv repo/tools ./tools && ls tools/Kraken/kraken.exe tools/KrakenField/field.exe
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
PYTHONPATH=. python - <<'EOF'
import numpy as np
z=np.load('/Users/pete/Downloads/mh370-exchange/searched-areas/run-j-supplement/arc-grid.npz'); arc=z['arc']; s0,w0,st=float(z['south']),float(z['west']),float(z['step'])
n=z['n']
for lat in (-41.0,-40.5,-40.0,-35.0):
    i=int(round((lat-s0)/st)); row=arc[i]; print(lat, 'first 12:', np.round(row[:12],1), 'n:', n[i,:12])
    k=np.where(np.diff(np.sign(row))!=0)[0]; print('  sign changes at lon', (w0+st*k)[:5])
print('n stats', n.min(), n.max(), (n==0).mean())
EOF