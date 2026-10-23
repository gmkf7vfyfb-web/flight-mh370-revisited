from pyproj import Geod
import run_j_windows as R
g=Geod(ellps="WGS84"); rx=R.receivers()
tp=json.load(open(RD/"tl_grid_run_j"/"table_points.json")); pts=sorted([(v["lat"],v["lon"]) for v in tp.values() if v["offset_nm"]==0])
la=np.array([p[0] for p in pts]); lo=np.array([p[1] for p in pts])
def dkm(st,lat,lon): return g.inv(lon,lat,np.full_like(np.atleast_1d(lon),rx[st][1],dtype=float),np.full_like(np.atleast_1d(lat),rx[st][0],dtype=float))[2]/1000
dA=dkm("H01W",la,lo); dB=dkm("H08S",la,lo)
def locus(tA,tB,c=1.482):
    lag=tB-tA; L=(dB-dA)/c; cr=np.where(np.diff(np.sign(L-lag))!=0)[0]
    out=[]
    for i in cr:
        lat=float(np.interp(lag,[L[i],L[i+1]],[la[i],la[i+1]])); lon=float(np.interp(lat,la,lo))
        d1=float(dkm("H01W",np.array([lat]),np.array([lon]))[0]); d2=float(dkm("H08S",np.array([lat]),np.array([lon]))[0])
        az1=g.inv(rx["H01W"][1],rx["H01W"][0],lon,lat)[0]%360; az2=g.inv(rx["H08S"][1],rx["H08S"][0],lon,lat)[0]%360
        ti=[tA-d1/cc for cc in (1.482,1.494,1.470)]
        out.append(dict(lag=lag,lat=lat,lon=lon,d1=d1,d2=d2,az1=az1,az2=az2,t=hms(ti[0]),t_lo=hms(ti[2]),t_hi=hms(ti[1])))
    return out
for nm,a,b in [("E","00:52:04.35","01:10:00.5"),("F","00:54:26.95","01:12:49.3"),("G","00:52:04.35","01:12:49.3"),("Gcand","00:52:04","01:12:49")]:
    print(nm, locus(unix(a),unix(b)))
print(rx["H01W"], rx["H08S"])
print("lag range", ((dB-dA)/1.482).min(), ((dB-dA)/1.482).max())