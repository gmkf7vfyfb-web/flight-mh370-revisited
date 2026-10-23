
import numpy as np, json, os
OD=os.path.expanduser('~/Downloads/mh370-ocean-data')
aj=json.load(open(f'{OD}/ausseabed/grid/ausseabed_mh370_150m.json'))
gj=json.load(open(f'{OD}/gebco/grid/gebco_2026.json'))
A=np.memmap(f'{OD}/ausseabed/grid/{aj["elevation_file"]}',dtype='<f4',mode='r',shape=(aj['nlat'],aj['nlon']))
G=np.memmap(f'{OD}/gebco/grid/{gj["elevation_file"]}',dtype='<i2',mode='r',shape=(gj['nlat'],gj['nlon']))
T=np.memmap(f'{OD}/gebco/grid/{gj["tid_file"]}',dtype='u1',mode='r',shape=(gj['nlat'],gj['nlon']))
R=6378137.0
def merc(lat,lon):
    return R*np.radians(lon), R*np.log(np.tan(np.pi/4+np.radians(lat)/2))
def aus(lat,lon):
    x,y=merc(np.asarray(lat,float),np.asarray(lon,float))
    i=np.rint((y-aj['y0_m'])/aj['step_m']).astype(int); j=np.rint((x-aj['x0_m'])/aj['step_m']).astype(int)
    ok=(i>=0)&(i<aj['nlat'])&(j>=0)&(j<aj['nlon'])
    out=np.full(np.shape(x),np.nan); out[ok]=A[i[ok],j[ok]]; return out
def geb(lat,lon):
    i=np.rint((np.asarray(lat)-gj['lat0'])/gj['step_deg']).astype(int); j=np.rint((np.asarray(lon)-gj['lon0'])/gj['step_deg']).astype(int)
    return G[i,j].astype(float), T[i,j]
def depth(lat,lon):
    a=aus(lat,lon); g,t=geb(lat,lon)
    d=np.where(np.isfinite(a),-a,-g); src=np.where(np.isfinite(a),'AusSeabed150','GEBCO2026')
    return d,src,-a,-g,t
# sanity: compare grids on a patch around Haixun
la,lo=np.meshgrid(np.linspace(-26.3,-25.4,60),np.linspace(101.0,101.9,60),indexing='ij')
d,src,da,dg,t=depth(la,lo)
m=np.isfinite(da)
print('patch AusSeabed coverage',m.mean(), 'mean(aus-geb)',np.nanmean(da-dg),'sd',np.nanstd(da-dg),'TID values',np.unique(t,return_counts=True))
