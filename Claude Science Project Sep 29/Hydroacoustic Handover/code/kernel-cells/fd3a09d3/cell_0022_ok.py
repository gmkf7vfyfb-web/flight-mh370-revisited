
s = np.load(EX/'end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz')
lat = s['latitude_deg'].astype(float); lon = s['longitude_deg'].astype(float)
for k in ['lnw:comb/D0','lnw:comb/D2','lnw:comb/D3','lnw:comb/D4','lnw:alone/D0']:
    w = np.exp(s[k].astype(float)); ok=np.isfinite(w)&np.isfinite(lat); 
    print(k, wq(lat[ok],w[ok],[0.005,0.01,0.5,0.99,0.995]).round(2), 'mass north of 25S', float(w[ok][lat[ok]>-25].sum()/w[ok].sum()), 'north of 20S', float(w[ok][lat[ok]>-20].sum()/w[ok].sum()))
print('lat range', lat.min(), lat.max(), 'technique', np.unique(s['technique'], return_counts=True))
# sign check on run J: lon relative to arc
sd = EX/'end-of-flight/run-j/run-j-free/seed-1'; cols=open(sd/'COLUMNS.txt').read().split(); X=np.load(sd/'impacts32.npy',mmap_mode='r')
la=np.asarray(X[:5000,cols.index('latitude_deg')],float); lo=np.asarray(X[:5000,cols.index('longitude_deg')],float); ad=np.asarray(X[:5000,cols.index('arc_distance_nm')],float)
al=np.array([arc_lon(v)[0] for v in la]); print('corr sign(ad) vs sign(lon-arc_lon):', np.mean(np.sign(ad)==np.sign(lo-al)))
