"""Download pinned-date ERA5 subset from Google's public ARCO mirror.

Source documentation: https://github.com/google-research/arco-era5
The archive chunks each variable as a full global hour (37 pressure levels).
Read one chunk at a time; retain a 0.5-degree subsample of the 0.25-degree grid.
"""
from pathlib import Path
import json
import numpy as np
import xarray as xr
from core import sha256

ROOT=Path(__file__).resolve().parent
STORE='gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3'

def pressure_altitude_ft(p):
    p=np.asarray(p)*100
    # ICAO standard pressure altitude, not instantaneous geometric height.
    return np.where(p>=22632.06,44330.77*(1-(p/101325)**.1902632),11000-6341.62*np.log(p/22632.06))/.3048

def main():
    out=ROOT/'inputs/era5';out.mkdir(exist_ok=True)
    ds=xr.open_zarr(STORE,chunks=None,storage_options={'token':'anon'},consolidated=True)
    hours=list(range(3,8))+list(range(18,26))
    levels=[125,150,175,200,225,250,300,350,400,450,500]
    lat=np.arange(-60,60.01,.5);lon=np.arange(40,160.01,.5)
    variables=['u_component_of_wind','v_component_of_wind','temperature']
    files=[]
    for hour in hours:
        path=out/f'hour_{hour:02d}.npz'
        stamp=np.datetime64('2014-03-07T00:00:00')+np.timedelta64(hour,'h')
        if not path.exists():
            values={}
            for var in variables:
                print(f'ERA5 {stamp} {var}',flush=True)
                a=ds[var].sel(time=stamp,level=levels,latitude=lat,longitude=lon).transpose('level','latitude','longitude').values
                if not np.isfinite(a).all():raise ValueError('ERA5 has missing values')
                values[var]=a.astype('float32')
            np.savez_compressed(path,latitude=lat,longitude=lon,level=levels,time_s=hour*3600.,**values)
        files.append({'path':str(path.relative_to(ROOT)),'sha256':sha256(path)})
    order=np.argsort(pressure_altitude_ft(levels));ns=[];es=[];ts=[]
    for hour in hours:
        with np.load(out/f'hour_{hour:02d}.npz') as z:
            ns.append(z['v_component_of_wind'][order]/.5144444444)
            es.append(z['u_component_of_wind'][order]/.5144444444)
            ts.append(z['temperature'][order])
    target=ROOT/'inputs/era5_weather.npz'
    np.savez_compressed(target,time_s=np.array(hours)*3600.,altitude_ft=pressure_altitude_ft(levels)[order],latitude_deg=lat,longitude_deg=lon,north_kt=np.stack(ns),east_kt=np.stack(es),temperature_k=np.stack(ts))
    (out/'manifest.json').write_text(json.dumps({'store':STORE,'source_documentation':'https://github.com/google-research/arco-era5','hours_since_2014_03_07_00_utc':hours,'variables':variables,'levels_hpa':levels,'retained_grid_deg':.5,'source_grid_deg':.25,'altitude_coordinate':'ICAO pressure altitude','interpolation':'linear time/pressure-altitude/latitude/longitude','unqueried_time_gap_hours':[7,18],'files':files,'assembled_sha256':sha256(target)},indent=2))
    print('ERA5 complete',flush=True)

if __name__=='__main__':main()
