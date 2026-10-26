"""Plane-wave fit of the 01:26 UTC 8 Mar 2014 arrival across the Reunion (PF + G) network.
2-8 Hz Hilbert envelope at 0.1 s, smoothed 2 s; log-envelope cross-correlation against G.RER over
01:25:50-01:28:30 (lags +/-15 s); stations with correlation > 0.6 kept; least-squares plane wave; bootstrap
(2000 resamples) for back-azimuth spread. Envelope lags are coarse; the fit is indicative only."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0,'scripts'); import geom
from obspy import read, read_inventory, UTCDateTime as U
from scipy.signal import butter, sosfiltfilt, hilbert
inv=read_inventory('data/resp/reunion_PF_channels.xml'); co={f'{n.code}.{s.code}':(s.latitude,s.longitude,s.elevation) for n in inv for s in n}
st=read('data/raw/reunion_PF_20140308_0120_0135.mseed'); st.merge(fill_value=0)
env={}
for tr in st:
    k=f'{tr.stats.network}.{tr.stats.station}'
    if k not in co or k in env: continue
    fs=tr.stats.sampling_rate; y=sosfiltfilt(butter(4,[2,8],btype='band',fs=fs,output='sos'),tr.data.astype(float)-tr.data.mean())
    e=np.abs(hilbert(y)); m=int(fs/10); e=np.sqrt((e[:len(e)//m*m].reshape(-1,m)**2).mean(1)); env[k]=(tr.stats.starttime,np.convolve(e,np.ones(20)/20,'same'))
t0r,er=env['G.RER']; i0=int((U('2014-03-08T01:25:50')-t0r)*10); n=int(160*10); ref=np.log(er[i0:i0+n]+1e-12)
rows=[]
for k,(t0,e) in env.items():
    j0=int((U('2014-03-08T01:25:50')-t0)*10); best=(-9,0)
    for L in range(-150,151):
        s=e[j0+L:j0+L+n]
        if len(s)<n: continue
        c=np.corrcoef(ref,np.log(s+1e-12))[0,1]; best=max(best,(c,L))
    rows.append(dict(station=k,lat=co[k][0],lon=co[k][1],elev_m=co[k][2],lag_s=best[1]/10,cc=best[0]))
Lg=pd.DataFrame(rows); Lg=Lg[Lg.cc>0.6].reset_index(drop=True)
lat0,lon0=-21.17,55.74; x=(Lg.lon-lon0)*111.32*np.cos(np.radians(lat0)); y=(Lg.lat-lat0)*111.32; G=np.c_[x,y,np.ones(len(Lg))]
def fit(i): s,*_=np.linalg.lstsq(G[i],Lg.lag_s.values[i],rcond=None); return s
s=fit(np.arange(len(Lg))); baz=np.degrees(np.arctan2(-s[0],-s[1]))%360
rng=np.random.default_rng(1); bs=np.array([np.degrees(np.arctan2(-q[0],-q[1]))%360 for q in (fit(rng.integers(0,len(Lg),len(Lg))) for _ in range(2000))])
summit=Lg.elev_m>=1900
out=dict(n_stations=len(Lg),baz_deg=float(baz),app_vel_km_s=float(1/np.hypot(s[0],s[1])),rms_s=float(np.sqrt(np.mean((Lg.lag_s-G@s)**2))),
         baz_boot_2p5=float(np.percentile(bs,2.5)),baz_boot_97p5=float(np.percentile(bs,97.5)),
         mean_lag_summit_s=float(Lg.lag_s[summit].mean()),mean_lag_below1900m_s=float(Lg.lag_s[~summit].mean()),n_summit=int(summit.sum()),
         baz_from_reunion_to_royer_C2_deg=float(geom.dist_az(lat0,lon0,-26.469,80.952)[1]))
Lg.to_csv('data/reunion_array_lags.csv',index=False); json.dump(out,open('data/reunion_array.json','w'),indent=1); print(json.dumps(out,indent=1))
