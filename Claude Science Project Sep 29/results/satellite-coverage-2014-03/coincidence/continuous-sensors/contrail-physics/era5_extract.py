"""Extract ERA5 (ARCO public zarr) upper-air fields for the MH370 contrail study.
Box 12N-42S, 80-106E; hours 7 Mar 2014 16:00 to 8 Mar 01:00 UTC."""
import fsspec, xarray as xr, numpy as np, time
from concurrent.futures import ThreadPoolExecutor
base="https://gcp-public-data-arco-era5.storage.googleapis.com/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
ds=xr.open_zarr(fsspec.get_mapper(base, client_kwargs={"trust_env":True}), chunks=None, consolidated=True)
times=np.arange(np.datetime64('2014-03-07T16:00'), np.datetime64('2014-03-08T02:00'), np.timedelta64(1,'h'))
lev=[100,125,150,175,200,225,250,300,350]
v3=['temperature','specific_humidity','u_component_of_wind','v_component_of_wind','fraction_of_cloud_cover','specific_cloud_ice_water_content']
v2=['high_cloud_cover','total_cloud_cover','medium_cloud_cover']
box=dict(latitude=slice(12,-42), longitude=slice(80,106))
def get(v,t):
    for k in range(4):
        try:
            a=ds[v].sel(time=t).sel(**box)
            if 'level' in a.dims: a=a.sel(level=lev)
            return v,t,a.load()
        except Exception as e:
            err=e; time.sleep(3)
    raise err
t0=time.time()
jobs=[(v,t) for v in v3+v2 for t in times]
out={}
with ThreadPoolExecutor(8) as ex:
    for v,t,a in ex.map(lambda x:get(*x), jobs):
        out.setdefault(v,[]).append(a)
dd=xr.Dataset({v:xr.concat(out[v],'time') for v in out})
dd.attrs['source']=base; dd.attrs['extracted']='ERA5 hourly reanalysis via ARCO-ERA5 public zarr (Carver & Merose 2023)'
dd.to_netcdf('contrail/data/era5_upper_air_20140307.nc')
print('done', time.time()-t0, {v:dd[v].shape for v in dd})
