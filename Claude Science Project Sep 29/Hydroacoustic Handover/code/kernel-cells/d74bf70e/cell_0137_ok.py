import xarray as xr, os, time
os.environ["OMP_NUM_THREADS"]="2"
t0=time.time()
g=xr.open_dataset("https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/ice_surface_elevation/netcdf/GEBCO_2026.nc")
print(g); 
t=xr.open_dataset("https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/type_identifier_grid/netcdf/gebco_2026_tid.nc"); print(list(t.data_vars), dict(t.sizes))
w=xr.open_dataset("https://www.ncei.noaa.gov/thredds-ocean/dodsC/woa23/DATA/temperature/netcdf/95A4/1.00/woa23_95A4_t16_01.nc", decode_times=False)
print(list(w.data_vars)[:8], dict(w.sizes), float(w.depth.max()))
print(time.time()-t0)