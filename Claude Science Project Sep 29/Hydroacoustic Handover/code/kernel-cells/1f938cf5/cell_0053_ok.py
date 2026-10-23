
CLASSES=['recorder-detached','fuselage-section','engine','landing-gear']
CLS_LABEL={'recorder-detached':'Recorder, detached (dense compact)','fuselage-section':'Recorder retained in aft fuselage section',
           'engine':'Engine','landing-gear':'Landing gear'}
c_km=1.48
def kadri_impacts(branch,n,rng,sig_az=0.5):
    t_rx={'T':52*60+3,'C':54*60+30}[branch]; t_arc=19*60+29
    az=AZ+sig_az*rng.normal(size=n); R7a=1591.3+5.9*(az-AZ)     # 7th-arc range vs azimuth (kadri_geom_output.txt)
    v=rng.uniform(0,250,size=n)/1000.0                            # km/s
    Dt=(t_rx-t_arc)-R7a/c_km
    dr=np.where(v>0, c_km*Dt/(1+c_km/np.maximum(v,1e-9)),0.0); dT=Dt/(1+v/c_km)
    la,lo,_=gw.fwd(np.full(n,H01W[1]),np.full(n,H01W[0]),az,(R7a+dr)*1e3)
    return lo, la, T0+t_arc+dT, dict(az=az,v=v*1e3,dr=dr)  # lat, lon, unix time
def run_case(name,lat0,lon0,t0,rows,ocean,rng,N):
    track=np.degrees(np.arctan2(rows.velocity_east_mps.values,rows.velocity_north_mps.values))
    fam=rows['latent:debris_class'].values.astype(int); res={}
    for cls in CLASSES:
        o=sm.settle(lat0,lon0,t0,rows.vh.values,track,fam,cls,ocean,wind,rng)
        dx,dy=sm.offsets_km(lat0,lon0,o['lat'],o['lon']); o['dx']=dx; o['dy']=dy; o['D']=np.hypot(dx,dy); o['fam']=fam
        o['lat0']=np.asarray(lat0); o['lon0']=np.asarray(lon0); res[cls]=o
    return res
N=40000; rng=np.random.default_rng(20261018)
RES={}
rowsA=sample_rows(N,rng)
RES['runJ_L']=run_case('runJ_L',rowsA.latitude_deg.values.astype(float),rowsA.longitude_deg.values.astype(float),T0+rowsA.t_impact_s.values,rowsA,glorys,rng,N)
for br in ('T','C'):
    la,lo,tt,meta=kadri_impacts(br,N,rng); rows=sample_rows(N,rng)
    RES[f'kadri_{br}']=run_case(br,la,lo,tt,rows,glorys,rng,N); RES[f'kadri_{br}']['meta']=meta
rowsH=sample_rows(N,rng)
RES['at_haixun']=run_case('HX',np.full(N,HX[0]),np.full(N,HX[1]),T0+rowsH.t_impact_s.values,rowsH,glorys,rng,N)
# J0011 planned-descent rows as a separate prior set
J0=Lm[Lm.stratum=='run-j-joined-v2/J0011']; p0=(J0.w0/J0.w0.sum()).values
rows0=J0.iloc[rng.choice(len(J0),size=N,p=p0)]
RES['J0011_L']=run_case('J0011',rows0.latitude_deg.values.astype(float),rows0.longitude_deg.values.astype(float),np.full(N,T0+1800.),rows0,glorys,rng,N)
def stats(o,m=None):
    m=np.ones(len(o['D']),bool) if m is None else m; D=o['D'][m]
    return dict(n=int(m.sum()),nan=int(np.isnan(D).sum()),p50=np.nanpercentile(D,50),p90=np.nanpercentile(D,90),p99=np.nanpercentile(D,99),
                depth_p50=np.nanmedian(o['depth'][m]),descent_min_p50=np.nanmedian(o['descent_s'][m])/60,floated=o['floated'][m].mean(),below_p50=np.nanmedian(o['below_m'][m]))
tab=[]
for case in ['runJ_L','J0011_L','kadri_T','kadri_C','at_haixun']:
    for cls in CLASSES:
        o=RES[case][cls]
        tab.append(dict(case=case,cls=cls,family='all',**stats(o)))
        for f,fn in enumerate(['intact','broken','fragmented']):
            tab.append(dict(case=case,cls=cls,family=fn,**stats(o,o['fam']==f)))
TAB=pd.DataFrame(tab); TAB['ocean']='GLORYS12V1'
print(TAB[TAB.family=='all'].round(2).to_string())
