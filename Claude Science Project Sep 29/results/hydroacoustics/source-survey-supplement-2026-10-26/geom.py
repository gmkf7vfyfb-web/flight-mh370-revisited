"""Path geometry for T phases recorded at island/coastal seismometers.
GEBCO_2026 15" grid (read-only memmap from Pete's Downloads). WGS84 geodesics (pyproj).
Conversion point = first point along the path, walking from the station toward the source, where the
water is >= ZCONV m deep. Water leg = source -> conversion point at C_T km/s; seismic leg = conversion
point -> station at V_SEIS km/s. Path class on the water leg follows the project's arc_line_of_sight.py:
 blocked: land or water < 200 m more than 20 km from the conversion point (and more than 20 km from the source);
 large attenuation: >= 10 km of water < 1000 m, more than 100 km from the conversion point;
 clear: neither. This is a geometric screen, not a transmission-loss result."""
import json, numpy as np, pyproj
G='/Users/pete/Downloads/mh370-ocean-data/gebco/grid'
gh=json.load(open(f'{G}/gebco_2026.json'))
EL=np.memmap(f"{G}/{gh['elevation_file']}",dtype='<i2',mode='r',shape=(gh['nlat'],gh['nlon']))
geod=pyproj.Geod(ellps='WGS84')
C_T=1.48; V_SEIS=6.0; ZCONV=1000.0
ARC_C,ARC_R=(0.570,64.252),44.501
def z(la,lo):
    la=np.asarray(la); lo=np.asarray(lo)%360
    i=np.clip(np.rint((la-gh['lat0'])/gh['step_deg']).astype(int),0,gh['nlat']-1)
    j=np.rint((lo-gh['lon0'])/gh['step_deg']).astype(int)
    out=np.full(la.shape,np.nan)
    ok=(j>=0)&(j<gh['nlon'])&(la>=gh['lat0']-0.01)&(la<=gh['lat0']+gh['nlat']*gh['step_deg'])
    out[ok]=EL[i[ok],j[ok]]
    return out
def dist_az(la1,lo1,la2,lo2):
    az12,az21,d=geod.inv(lo1,la1,lo2,la2); return d/1000., az12%360, az21%360
def path(src_lat,src_lon,sta_lat,sta_lon,step_km=1.0):
    """Returns dict with distances, class, conversion point, back-azimuth at station."""
    _,baz_sta,D=None,None,None
    az_sta2src,az_src2sta,d=geod.inv(sta_lon,sta_lat,src_lon,src_lat); D=d/1000.
    n=max(int(D/step_km),2)
    pts=np.array(geod.npts(sta_lon,sta_lat,src_lon,src_lat,n))   # from station to source
    lo=np.r_[sta_lon,pts[:,0],src_lon]; la=np.r_[sta_lat,pts[:,1],src_lat]
    s=np.linspace(0,D,len(lo))  # km from station
    zz=z(la,lo)
    if np.all(np.isnan(zz)): return dict(D=D,baz=az_sta2src%360,cls='no bathymetry',seis_km=np.nan,water_km=np.nan,conv_lat=np.nan,conv_lon=np.nan,shallow_km=np.nan,obst_lat=np.nan,obst_lon=np.nan,src_depth_m=np.nan)
    deep=np.where(-zz>=ZCONV)[0]
    if len(deep)==0:
        return dict(D=D,baz=az_sta2src%360,cls='no deep water',seis_km=D,water_km=0.,conv_lat=np.nan,conv_lon=np.nan,shallow_km=np.nan,obst_lat=np.nan,obst_lon=np.nan,src_depth_m=float(-zz[-1]))
    k=deep[0]; seis=s[k]; water=D-seis
    w=s>=seis  # water leg
    dc=s-seis; ds=D-s
    blk=w&((zz>-200)|np.isnan(zz))&(dc>20)&(ds>20)
    sh=w&(zz>-1000)&(dc>100)&(ds>20)
    shallow_km=sh.sum()*(D/(len(s)-1))
    if blk.any():
        cls='blocked'; ob=np.where(blk)[0][0]
    elif shallow_km>=10:
        cls='large attenuation'; ob=np.where(sh)[0][0]
    else:
        cls='clear'; ob=None
    return dict(D=D,baz=az_sta2src%360,cls=cls,seis_km=seis,water_km=water,conv_lat=la[k],conv_lon=lo[k],shallow_km=shallow_km,
                obst_lat=la[ob] if ob is not None else np.nan,obst_lon=lo[ob] if ob is not None else np.nan,src_depth_m=float(-zz[-1]))
def t_travel(p):
    """Predicted T travel time (s) for a path dict."""
    if not np.isfinite(p['water_km']): return np.nan
    return p['water_km']/C_T + p['seis_km']/V_SEIS
def arc_points(lat_from=-20.0,lat_to=-40.0,step=0.5):
    def dest(lat,lon,az,d):
        la,lo,az,d=map(np.radians,(lat,lon,az,d))
        la2=np.arcsin(np.sin(la)*np.cos(d)+np.cos(la)*np.sin(d)*np.cos(az))
        lo2=lo+np.arctan2(np.sin(az)*np.sin(d)*np.cos(la),np.cos(d)-np.sin(la)*np.sin(la2))
        return np.degrees(la2),np.degrees(lo2)
    az=np.linspace(90,180,90001); la,lo=dest(*ARC_C,az,ARC_R)
    tg=np.round(np.arange(lat_from,lat_to-1e-9,-step),2)
    return [(float(la[np.argmin(abs(la-t))]),float(lo[np.argmin(abs(la-t))])) for t in tg]
