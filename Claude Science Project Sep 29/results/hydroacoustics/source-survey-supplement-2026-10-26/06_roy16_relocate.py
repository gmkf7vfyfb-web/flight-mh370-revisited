"""Independent seismic location of Royer 2016 event 16 (Java earthquake, Royer: 8.052 S 107.622 E, 01:15:48.0).
P and S onsets picked by the AIC picker (Maeda 1985 form) in fixed windows chosen by eye on a 2-8 Hz (P) or
1-6 Hz (S) record section; grid search over latitude/longitude (0.02 deg) and fixed depths with iasp91
travel times (TauP), origin time solved by weighted least squares. Weights: P 0.5 s, S 2.0 s."""
import sys, glob, os, json, numpy as np, pandas as pd
sys.path.insert(0,'scripts'); import geom
from obspy import read, UTCDateTime as U
from obspy.taup import TauPyModel
from scipy.signal import butter, sosfiltfilt
from scipy.interpolate import RegularGridInterpolator
st=pd.read_csv('data/stations.csv').set_index('station')
chan={'.'.join(os.path.basename(f).split('.')[:2]):f for f in glob.glob('data/raw/*.20140308.mseed')}
t_ref=U('2014-03-08T01:10:00')
WIN={('GE.CISI','P'):(325,348),('GE.UGM','P'):(352,375),('AU.XMIS','P'):(360,380),('AU.XMI','P'):(360,380),
     ('AU.XMIS','S'):(398,418),('AU.XMI','S'):(398,418),('GE.UGM','S'):(385,405)}
def aic(x):
    n=len(x); k=np.arange(1,n-1); c=np.cumsum(x**2); v1=c[k-1]/k; v2=(c[-1]-c[k-1])/(n-k)
    return k, k*np.log(v1+1e-30)+(n-k-1)*np.log(v2+1e-30)
picks=[]
for (s,ph),(a,b) in WIN.items():
    tr=read(chan[s]).merge(fill_value=0)[0].slice(t_ref+a-20,t_ref+b+10).copy(); fs=tr.stats.sampling_rate
    band=(2,8) if ph=='P' else (1,6)
    x=sosfiltfilt(butter(4,[band[0],min(band[1],0.45*fs)],btype='band',fs=fs,output='sos'),tr.data.astype(float)-tr.data.mean())
    k,av=aic(x[:int((b-a+20)*fs)]); j=k[np.argmin(av)]
    picks.append(dict(station=s,phase=ph,pick_utc=str(tr.stats.starttime+j/fs)[:23],sigma_s=0.5 if ph=='P' else 2.0))
PK=pd.DataFrame(picks)
mod=TauPyModel('iasp91'); deps=np.array([5,10,20,35,50,70,100.]); dists=np.arange(0,20.01,0.05)
TP=np.zeros((len(dists),len(deps))); TS=TP.copy()
for j,d in enumerate(deps):
    for i,x in enumerate(dists):
        a=mod.get_travel_times(d,max(x,0.01),phase_list=['p','P','Pn','s','S','Sn'])
        TP[i,j]=min(q.time for q in a if q.name[0] in 'Pp'); TS[i,j]=min(q.time for q in a if q.name[0] in 'Ss')
fP=RegularGridInterpolator((dists,deps),TP); fS=RegularGridInterpolator((dists,deps),TS)
tobs=np.array([U(x)-U('2014-03-08T01:15:00') for x in PK.pick_utc]); w=1/PK.sigma_s.values**2
stl=st.loc[PK.station,['lat','lon']].values
la=np.arange(-10,-6.49,0.02); lo=np.arange(105.5,109.51,0.02); LA,LO=np.meshgrid(la,lo,indexing='ij')
res=[]
for dep in [5,10,20,35,50,70]:
    T=np.zeros(LA.shape+(len(PK),))
    for k,(sla,slo) in enumerate(stl):
        d=geom.geod.inv(np.full(LA.size,slo),np.full(LA.size,sla),LO.ravel(),LA.ravel())[2]/1000/111.195
        T[...,k]=(fP if PK.phase.iloc[k]=='P' else fS)(np.c_[d,np.full(d.size,dep)]).reshape(LA.shape)
    t0=((tobs-T)*w).sum(-1)/w.sum(); chi=(((tobs-T-t0[...,None])**2)*w).sum(-1)
    i=np.unravel_index(np.argmin(chi),chi.shape); res.append(dict(depth_km=dep,lat=float(la[i[0]]),lon=float(lo[i[1]]),origin_s_after_0115=float(t0[i]),chi2=float(chi[i]),chi=chi,T=T[i]))
best=min(res,key=lambda r:r['chi2']); ok=best['chi']<=best['chi2']+4.0
dR=[geom.dist_az(a,b,-8.052,107.622)[0] for a,b in zip(LA[ok],LO[ok])]
out=dict(picks=PK.to_dict('records'),best=dict((k,v) for k,v in best.items() if k not in('chi','T')),
         by_depth=[dict((k,v) for k,v in r.items() if k not in('chi','T')) for r in res],
         region_dchi2_4=dict(lat_min=float(LA[ok].min()),lat_max=float(LA[ok].max()),lon_min=float(LO[ok].min()),lon_max=float(LO[ok].max()),
                             min_dist_to_royer_km=float(min(dR)),max_dist_to_royer_km=float(max(dR))),
         dist_best_to_royer_km=float(geom.dist_az(best['lat'],best['lon'],-8.052,107.622)[0]),
         origin_minus_royer_s=float(best['origin_s_after_0115']-48.0),
         residuals_s=dict(zip(PK.station+' '+PK.phase,(tobs-best['T']-best['origin_s_after_0115']).round(2).tolist())))
json.dump(out,open('data/roy16_relocation.json','w'),indent=1); print(json.dumps({k:v for k,v in out.items() if k!='picks'},indent=1))
