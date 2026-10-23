
def kadri_impacts_s(branch,n,rng,sig_az=0.5,bto_sd=63.0,alt_max_ft=40000.0):
    t_rx={'T':52*60+3,'C':54*60+30}[branch]; t_arc=19*60+29
    az=AZ+sig_az*rng.normal(size=n)
    eps=bto_sd*rng.normal(size=n); h=rng.uniform(0,alt_max_ft,size=n)
    R7a=1591.3+5.9*(az-AZ)-0.197*eps-(1591.3-1582.5)*(h/35000.0)
    v=rng.uniform(0,250,size=n)/1000.0
    Dt=(t_rx-t_arc)-R7a/c_km
    dr=c_km*Dt/(1+c_km/np.maximum(v,1e-9)); dT=Dt/(1+v/c_km)
    la,lo,_=gw.fwd(np.full(n,H01W[1]),np.full(n,H01W[0]),az,(R7a+dr)*1e3)
    return lo, la, T0+t_arc+dT
sens=[]
rngS=np.random.default_rng(5)
for br in ('T','C'):
    la,lo,tt=kadri_impacts_s(br,N,rngS); rows=sample_rows(N,rngS)
    rs=run_case(br,la,lo,tt,rows,glorys,rngS,N)
    for cls in ['recorder-detached','fuselage-section']:
        o=rs[cls]
        d=gw.inv(o['lon'],o['lat'],np.full(N,HX[1]),np.full(N,HX[0]))[2]/1e3
        d0=gw.inv(o['lon0'],o['lat0'],np.full(N,HX[1]),np.full(N,HX[0]))[2]/1e3
        sens.append(dict(branch=br,cls=cls,n=N,impact_min_dist_km=d0.min(),rest_min_dist_km=d.min(),frac_rest_le2km=(d<=2).mean(),n_rest_le2km=int((d<=2).sum()),frac_impact_le2km=(d0<=2).mean()))
SENS=pd.DataFrame(sens); print(SENS.round(5).to_string())
