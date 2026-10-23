cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
PYTHONPATH=. python - <<'EOF'
import numpy as np
EX='/Users/pete/Downloads/mh370-exchange/'
z=np.load(EX+'searched-areas/run-j-supplement/arc-grid.npz'); arc=z['arc']; n=z['n']; s0,w0,st=float(z['south']),float(z['west']),float(z['step'])
lons=w0+st*np.arange(arc.shape[1])
r=np.load(EX+'searched-areas/run-j-supplement/reduced-impact-columns.npz'); print(r.files)
s=np.load(EX+'end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz'); la=s['latitude_deg'].astype(float); lo=s['longitude_deg'].astype(float); ad=r['arc_distance_nm_interp'].astype(float)
for lat in np.arange(-41,-19.9,0.5):
    i=int(round((lat-s0)/st)); ok=n[i]>0; m=ok.sum()
    out=[lat, int(m)]
    if m>=5:
        A=np.vstack([np.ones(m), arc[i][ok]]).T; c,res,_,_=np.linalg.lstsq(A, lons[ok], rcond=None); pred=A@c
        out += ['grid fit lon0=%.3f dlon/dNM=%.5f rms=%.4f span=[%.0f,%.0f]'%(c[0],c[1],np.sqrt(np.mean((pred-lons[ok])**2)), arc[i][ok].min(), arc[i][ok].max())]
    sel=np.abs(la-lat)<0.25; k=sel.sum()
    if k>=20:
        A=np.vstack([np.ones(k), ad[sel]]).T; c,_,_,_=np.linalg.lstsq(A, lo[sel], rcond=None); pred=A@c
        out += ['supp n=%d lon0=%.3f dlon/dNM=%.5f rms=%.4f span=[%.0f,%.0f]'%(k,c[0],c[1],np.sqrt(np.mean((pred-lo[sel])**2)), ad[sel].min(), ad[sel].max())]
    print(*out)
EOF