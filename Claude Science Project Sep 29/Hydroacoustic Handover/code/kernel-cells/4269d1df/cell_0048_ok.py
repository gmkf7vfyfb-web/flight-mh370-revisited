
import numpy as np, json
meta=json.load(open('jobsnap/meta.json')); rel=meta['L']
HX=(-25.975,101.461)
def hav(lat1,lon1,lat2,lon2):
    p1,p2=np.radians(lat1),np.radians(lat2); dl=np.radians(lon2-lon1)
    a=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2; return 2*6371.0088*np.arcsin(np.sqrt(a))
def az(lat1,lon1,lat2,lon2):
    p1,p2=np.radians(lat1),np.radians(lat2); dl=np.radians(lon2-lon1)
    return (np.degrees(np.arctan2(np.sin(dl)*np.cos(p2), np.cos(p1)*np.sin(p2)-np.sin(p1)*np.cos(p2)*np.cos(dl)))+360)%360
dtL=np.dtype([('rel','u1'),('env','u1'),('cls','u1'),('fate','u1'),('bt','<f4'),('blon','<f4'),('blat','<f4'),('pos','<f4',(9,2))])
SL={m:np.fromfile(f'hpc/scp-e3770710e2f9c1ed/hpc/0d37c2df-178b-41c2-ae15-2bb5437a8d9b/snapL-{m}.bin',dtype=dtL) for m in ('globcurrent','glorys12')}
tl=['15 Mar 00Z','22 Mar 00Z','29 Mar 00Z','3 Apr 00Z','4 Apr 00Z','4 Apr 12Z','5 Apr 00Z','5 Apr 12Z','6 Apr 00Z']
rowsF=[]
for m,a in SL.items():
    assert len(a)==12*100008
    for ri,r in enumerate(rel):
        s=a[a['rel']==ri]
        for k in (4,5,6,7):
            lo,la=s['pos'][:,k,0],s['pos'][:,k,1]; ok=np.isfinite(lo)
            d=hav(HX[0],HX[1],la[ok],lo[ok]); dsrc=hav(r['lat'],r['lon'],la[ok],lo[ok])
            rowsF.append(dict(model=m,point=r['point'],branch=r['branch'],time=tl[k],afloat=ok.mean(),
                cen_lat=float(np.median(la[ok])),cen_lon=float(np.median(lo[ok])),disp_from_release_med_km=float(np.median(dsrc)),
                dist_haixun_med_km=float(np.median(d)),dist_haixun_q05=float(np.quantile(d,.05)),dist_haixun_q95=float(np.quantile(d,.95)),
                frac_lt30=float((d<30).mean()),frac_30_70=float(((d>=30)&(d<70)).mean()),frac_70_110=float(((d>=70)&(d<110)).mean()),frac_gt110=float((d>=110).mean()),
                az_from_haixun_med=float(np.median(az(HX[0],HX[1],la[ok],lo[ok])))))
fw=pd.DataFrame(rowsF)
pd.set_option('display.width',250)
print(fw[(fw.time=='5 Apr 00Z')].round(3).to_string())
