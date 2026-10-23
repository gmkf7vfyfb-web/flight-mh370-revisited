
FR=3.25/12.0   # 03:15 UTC between 5 Apr 00Z (idx) and 12Z
def pos_at_0315(P, i00, i12):
    a=P[:,i00,:]; b=P[:,i12,:]; return a+(b-a)*FR   # NaN if either not afloat
def ring_frac(lat,lon,center=HX,r0=70,r1=110):
    ok=np.isfinite(lat); d=hav(center[0],center[1],lat,lon); return np.where(ok,(d>=r0)&(d<r1),False), ok
# forward from L points: fraction in ring at 03:15Z 5 Apr, also within 110 km disc
fwd=[]
for m,a in SL.items():
    for ri,r in enumerate(rel):
        s=a[a['rel']==ri]; p=pos_at_0315(s['pos'],6,7)
        inr,ok=ring_frac(p[:,1],p[:,0]); d=hav(HX[0],HX[1],p[:,1],p[:,0])
        fwd.append(dict(model=m,point=r['point'],branch=r['branch'],n=len(s),afloat=float(ok.mean()),
                        n_ring_70_110=int(inr.sum()),frac_ring=float(inr.sum()/len(s)),n_disc_110=int(np.nansum(d<110)),
                        med_dist_km=float(np.nanmedian(d)),q01_dist_km=float(np.nanquantile(d,0.01)),min_dist_km=float(np.nanmin(d))))
fwdf=pd.DataFrame(fwd); print(fwdf.round(5).to_string())
