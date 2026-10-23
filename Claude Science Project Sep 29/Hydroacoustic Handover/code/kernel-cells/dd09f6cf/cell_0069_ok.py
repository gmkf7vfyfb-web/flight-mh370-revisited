import xarray as xr
cur=xr.open_dataset('ocean/globcurrent_2014.nc'); win=xr.open_dataset('ocean/wind_l4_2014.nc')
U=np.nan_to_num(cur['uo'].values[:,0]); Vv=np.nan_to_num(cur['vo'].values[:,0]); clat,clon=cur['latitude'].values,cur['longitude'].values; ct=cur['time'].values+np.timedelta64(12,'h')
WU=np.nan_to_num(win['eastward_wind'].values); WV=np.nan_to_num(win['northward_wind'].values); wlat,wlon,wt=win['latitude'].values,win['longitude'].values,win['time'].values
def bil(F,la0,lo0,st,la,lo):
    y=np.clip((la-la0)/st,0,F.shape[-2]-1.001); x=np.clip((lo-lo0)/st,0,F.shape[-1]-1.001); i=y.astype(int); j=x.astype(int); fy=y-i; fx=x-j
    return (1-fy)*((1-fx)*F[i,j]+fx*F[i,j+1])+fy*((1-fx)*F[i+1,j]+fx*F[i+1,j+1])
def track(lat0,lon0,alpha=0.012,n=256,seed=1):
    rg=np.random.default_rng(seed); la=lat0+(rg.random(n)-0.5)*0.25; lo=lon0+(rg.random(n)-0.5)*0.25
    t=np.datetime64('2014-03-08T00:30'); out={}
    while t<=np.datetime64('2014-04-28T04:30'):
        if (t-np.datetime64('2014-03-07T04:30'))%np.timedelta64(1,'D')==np.timedelta64(0): out[str(t)[:10]]=(la.copy(),lo.copy())
        th=(t-ct[0])/np.timedelta64(1,'h')/24; k0=int(np.clip(np.floor(th),0,len(ct)-2)); f=float(np.clip(th-k0,0,1))
        uc=(1-f)*bil(U[k0],clat[0],clon[0],0.25,la,lo)+f*bil(U[k0+1],clat[0],clon[0],0.25,la,lo); vc=(1-f)*bil(Vv[k0],clat[0],clon[0],0.25,la,lo)+f*bil(Vv[k0+1],clat[0],clon[0],0.25,la,lo)
        kw=int(np.clip(round((t-wt[0])/np.timedelta64(1,'h')),0,len(wt)-1)); uw=bil(WU[kw],wlat[0],wlon[0],0.125,la,lo); vw=bil(WV[kw],wlat[0],wlon[0],0.125,la,lo)
        sd=np.sqrt(2*100*3600.); dy=(vc+alpha*vw)*3600+sd*rg.standard_normal(n); dx=(uc+alpha*uw)*3600+sd*rg.standard_normal(n)
        la=la+np.degrees(dy/6371000); lo=lo+np.degrees(dx/(6371000*np.cos(np.radians(la)))); t+=np.timedelta64(1,'h')
    return out
trk=track(-25.732,101.369)
for k in ['2014-03-08','2014-03-18','2014-03-28','2014-04-03','2014-04-13','2014-04-24']:
    la,lo=trk[k]; print(k,'median %.2f %.2f  spread lat %.2f lon %.2f'%(np.median(la),np.median(lo),np.std(la),np.std(lo)))