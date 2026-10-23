import cartopy, os
os.makedirs("cartopy_data", exist_ok=True); cartopy.config['data_dir']=os.path.abspath("cartopy_data")
try:
    import cartopy.io.shapereader as shp; p=shp.natural_earth('50m','physical','land'); print("land ok")
    ok=True
except Exception as e: print("land fail", type(e).__name__, str(e)[:200]); ok=False