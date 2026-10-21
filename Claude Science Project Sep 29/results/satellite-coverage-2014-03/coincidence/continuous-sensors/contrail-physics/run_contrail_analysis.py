"""MH370 contrail formation / persistence along run J posterior routes (ERA5, Schmidt-Appleman).
Usage: python run_contrail_analysis.py <era5.nc from era5_extract.py> <outdir>
Reads run J routes (read-only) and the Geoscience Australia radar workbook path below.
Writes contrail-probability-along-route.csv (posterior part) for regression check."""
import sys, glob, numpy as np, pandas as pd, xarray as xr
from scipy.interpolate import RegularGridInterpolator as RGI
sys.path.insert(0, __file__.rsplit('/',1)[0]); import contrail_lib as cl
nc, outdir = sys.argv[1], sys.argv[2]
R = "/Users/pete/Downloads/mh370-exchange/core/run-j"
FAMS = {'run-j-waypoints':0.9982,'run-j-free':0.0013,'run-j-repro-radar':0.0003,'run-j-descent-climb':0.0002}
E = xr.open_dataset(nc).load().sortby('latitude')
tE = (E.time.values-np.datetime64('2014-03-07T00:00'))/np.timedelta64(1,'s')
lp = np.log(E.level.values*100.0)
I = {v:RGI((tE,lp,E.latitude.values,E.longitude.values),E[v].values.astype(float)) for v in ['temperature','specific_humidity']}
LAT=[];LON=[];W=[]
for f,pf in FAMS.items():
    a=np.stack([np.load(x) for x in sorted(glob.glob(f"{R}/{f}/bto-bfo/seed-*/routes.npy"))])
    ns=a.shape[0]; a=a.reshape(-1,38,2); LAT.append(a[:,:,0]); LON.append(a[:,:,1]); W.append(np.full(a.shape[0],pf/(ns*2000)))
LAT=np.concatenate(LAT).astype(float); LON=np.concatenate(LON).astype(float); W=np.concatenate(W)
K=np.arange(2,38); tk=18*3600+1*60+49+600*K
lat=LAT[:,K]; lon=LON[:,K]; tt=np.broadcast_to(tk,lat.shape); NP=lat.shape
FLS=np.arange(300,401,10); ETAS=[0.30,0.35]; HUM=['raw','teoh2022','teoh2024']
res={}
for fl in FLS:
    p=float(cl.fl_to_pressure(fl)); P=np.column_stack([tt.ravel(),np.full(tt.size,np.log(p)),lat.ravel(),lon.ravel()])
    T=I['temperature'](P).reshape(NP); q=I['specific_humidity'](P).reshape(NP); rhi=cl.vapour_pressure(q,p)/cl.e_ice(T)
    rh={'raw':rhi,'teoh2022':cl.rhi_correct_teoh2022(rhi),'teoh2024':cl.rhi_correct_teoh2024(rhi,lat,T)}
    for h in HUM:
        for eta in ETAS:
            s,_=cl.sac(T,rh[h]*cl.e_ice(T),p,eta); res[(int(fl),eta,h)]=(s,s&(rh[h]>=1))
# posterior altitude weights: core trace altitude at 18:42:40, FL410 -> FL400 result, <FL300 -> no formation
alts=[];aw=[]
for f,pf in FAMS.items():
    a=np.stack([np.load(x) for x in sorted(glob.glob(f"{R}/{f}/bto-bfo/seed-*/trace.npy"))])[:,:,-1,2].ravel(); alts.append(a); aw.append(np.full(a.size,pf/a.size))
alts=np.concatenate(alts); aw=np.concatenate(aw); flb=np.round(alts/1000)*10
wfl={int(fl):float(aw[flb==fl].sum()) for fl in FLS}; wfl[400]+=float(aw[flb>400].sum())
fmt=lambda t:f"{'2014-03-07' if t<86400 else '2014-03-08'}T{(t//3600)%24:02d}:{t%3600//60:02d}:{t%60:02d}Z"
wm=lambda x:(x*W[:,None]).sum(0); rows=[]
for h in HUM:
    for eta in ETAS:
        cases=[(f'FL{fl}',{int(fl):1.0}) for fl in FLS]+[('FL300-FL400 uniform',{int(fl):1/len(FLS) for fl in FLS}),('posterior altitude',wfl)]
        for cn,wd in cases:
            pf=sum(w*wm(res[(f,eta,h)][0]) for f,w in wd.items()); pp=sum(w*wm(res[(f,eta,h)][1]) for f,w in wd.items())
            af=sum(w*float((res[(f,eta,h)][0].any(1)*W).sum()) for f,w in wd.items())
            for j in range(len(K)): rows.append(dict(time_utc=fmt(int(tk[j])),altitude_case=cn,propulsion_efficiency=eta,humidity=h,p_form=round(float(pf[j]),4),p_persist=round(float(pp[j]),4),p_any_form_1822_0011=round(af,4)))
pd.DataFrame(rows).to_csv(f"{outdir}/check-posterior-main.csv",index=False)
print('wrote',len(rows))
