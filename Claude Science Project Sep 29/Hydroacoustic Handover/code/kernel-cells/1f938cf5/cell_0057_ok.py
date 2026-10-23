
inv_rows=[]
INV={}
rngI=np.random.default_rng(99)
def R7_of_az(az): return 1591.3+5.9*(az-AZ)
for cls in ['recorder-detached','fuselage-section']:
    o=RES['at_haixun'][cls]; n=len(o['dx'])
    rr=2.0*np.sqrt(rngI.uniform(size=n)); th=rngI.uniform(0,2*np.pi,size=n)
    ex=-o['dx']+rr*np.cos(th); ny=-o['dy']+rr*np.sin(th)          # impact offset from HX, km (east, north)
    la=HX[0]+np.degrees(ny*1e3/sm.RE); lo=HX[1]+np.degrees(ex*1e3/(sm.RE*np.cos(np.radians(HX[0]))))
    az1,_,s=gw.inv(np.full(n,H01W[1]),np.full(n,H01W[0]),lo,la); az1%=360; rng_km=s/1e3
    dist=np.hypot(ex,ny); INV[cls]=dict(ex=ex,ny=ny,la=la,lo=lo,az=az1,rng=rng_km,dist=dist)
    beyond=rng_km>=R7_of_az(az1)
    strip_w=(rng_km>=R7_of_az(az1)-60)&(rng_km<=R7_of_az(az1)+250)&(abs(az1-AZ)<=1.0)
    strip_c=strip_w&(abs(az1-AZ)<=0.5)
    inv_rows.append(dict(cls=cls,dist_p50=np.percentile(dist,50),dist_p90=np.percentile(dist,90),dist_p99=np.percentile(dist,99),dist_max=dist.max(),
                         frac_in_strip_wide=strip_w.mean(),frac_in_strip_core=strip_c.mean(),frac_beyond_arc_on_bearing=beyond.mean(),
                         min_gap_to_arc_km=float(np.min(R7_of_az(az1)-rng_km))))
INVT=pd.DataFrame(inv_rows); print(INVT.round(3).to_string())
# forward: Kadri branch resting points near Haixun?
for br in ('T','C'):
    for cls in ['recorder-detached','fuselage-section']:
        o=RES[f'kadri_{br}'][cls]
        d=gw.inv(o['lon'],o['lat'],np.full(N,HX[1]),np.full(N,HX[0]))[2]/1e3
        d0=gw.inv(o['lon0'],o['lat0'],np.full(N,HX[1]),np.full(N,HX[0]))[2]/1e3
        print(br,cls,'min rest dist to HX km',round(d.min(),2),'p1',round(np.percentile(d,1),2),'frac<=2km',(d<=2).mean(),'impact min dist',round(d0.min(),2), 'impact time range',
              [hm((t-T0)/60) for t in np.percentile(T0+0,[0])] if False else '')
