import glob
f='/Users/pete/Downloads/mh370-ocean-data/glorys12/glorys12v1_uo_vo_surface_15-120E_50-0S_20140307-20140430.nc'
try:
    import xarray as xr
except ImportError:
    import subprocess,sys; subprocess.run([sys.executable,'-m','pip','install','-q','xarray','netCDF4','h5netcdf']); import xarray as xr
ds=xr.open_dataset(f)
print(ds)
