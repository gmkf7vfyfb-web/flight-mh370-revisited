import xarray as xr
g=xr.open_dataset("https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/ice_surface_elevation/netcdf/GEBCO_2026.nc")
print(repr(g.attrs.get("id"))); print(repr(g.attrs.get("identifier_product_doi")))