
try:
    from geographiclib.geodesic import Geodesic
except ImportError:
    import subprocess,sys; subprocess.run([sys.executable,'-m','pip','install','-q','geographiclib']); from geographiclib.geodesic import Geodesic
Gd=Geodesic.WGS84
H01W=(-34.8903,114.1426); AZ=306.18; CX=(-25.732,101.369); HX=(-25.975,101.461)
inv=Gd.Inverse(*H01W,*CX); R7=inv['s12']/1e3; print('R7',R7, 'az',inv['azi1'])
ih=Gd.Inverse(*H01W,*HX); print('Haixun range',ih['s12']/1e3,'az',ih['azi1'],'dist to crossing',Gd.Inverse(*HX,*CX)['s12']/1e3)
def dest(p,az,km):
    r=Gd.Direct(p[0],p[1],az,km*1e3); return r['lat2'],r['lon2']
pts={}
pts['Haixun first contact (25.975 S 101.461 E)']=HX
for k in (2,3):
    pts[f'Haixun second contact, {k} km west']=dest(HX,270,k)
pts['Bearing x 7th arc (25.732 S 101.369 E)']=CX
pts['Kadri R7=1586 km point']=(-25.764,101.408)
rows=[]
for name,(la_,lo_) in pts.items():
    d,src,da,dg,t=depth(np.array([la_]),np.array([lo_]))
    rr=np.sqrt(np.random.default_rng(0).uniform(0,1,4000))*2.0; th=np.random.default_rng(1).uniform(0,360,4000)
    dl=[dest((la_,lo_),a,r) for a,r in zip(th,rr)]
    dd,ss,_,_,_=depth(np.array([x[0] for x in dl]),np.array([x[1] for x in dl]))
    rows.append(dict(site=name,lat=round(la_,4),lon=round(lo_,4),depth_m=round(float(d[0]),1),source=str(src[0]),
                     ausseabed_m=round(float(da[0]),1) if np.isfinite(da[0]) else None, gebco_m=round(float(dg[0]),1),gebco_tid=int(t[0]),
                     disc2km_min=round(float(dd.min())),disc2km_p50=round(float(np.median(dd))),disc2km_max=round(float(dd.max())),
                     disc2km_aus_frac=round(float((ss=='AusSeabed150').mean()),3)))
import pandas as pd
site_df=pd.DataFrame(rows); print(site_df.to_string())
