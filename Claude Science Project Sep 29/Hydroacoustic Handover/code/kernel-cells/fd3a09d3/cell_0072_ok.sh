python - <<'EOF'
import numpy as np, json
EX='/Users/pete/Downloads/mh370-exchange/end-of-flight/'
res={}
for st in ['run-j-waypoints','run-j-free','run-j-descent-climb','run-j-repro-radar']:
    sd=EX+'run-j/'+st+'/seed-1/'; cols=open(sd+'COLUMNS.txt').read().split(); X=np.load(sd+'impacts32.npy',mmap_mode='r')
    lat=np.asarray(X[:,cols.index('latitude_deg')],float); w=np.asarray(X[:,cols.index('weight')],float); ad=np.asarray(X[:,cols.index('arc_distance_nm')],float)
    ok=np.isfinite(lat)&np.isfinite(w); lat,w,ad=lat[ok],w[ok],ad[ok]; w=w/w.sum()
    r=dict(rows_outside_old=float(np.mean((lat<-38.46)|(lat>-31.64))), mass_outside_old=float(w[(lat<-38.46)|(lat>-31.64)].sum()),
           rows_outside_new=float(np.mean((lat<-41)|(lat>-20))), mass_outside_new=float(w[(lat<-41)|(lat>-20)].sum()),
           mass_beyond_pm30=float(w[np.abs(ad)>30].sum()), mass_beyond_pm60=float(w[np.abs(ad)>60].sum()), mass_east_60=float(w[ad>60].sum()), mass_west_60=float(w[ad<-60].sum()))
    res[st]={k:round(v,4) for k,v in r.items()}; print(st, res[st])
s=np.load(EX+'run-j-supplement/reduced/impacts-ruleB.npz'); lat=s['latitude_deg'].astype(float); w=np.exp(s['lnw:comb/D0'].astype(float)); ok=np.isfinite(lat)&np.isfinite(w); lat,w=lat[ok],w[ok]; w/=w.sum()
print('supplement D0: mass outside old', round(float(w[(lat<-38.46)|(lat>-31.64)].sum()),4), 'outside new', round(float(w[(lat<-41)|(lat>-20)].sum()),6), 'rows outside new', round(float(np.mean((lat<-41)|(lat>-20))),5))
json.dump(res, open('/tmp/clamp_gap.json','w'), indent=1)
EOF