python3 -c "import cartopy, cartopy.__version__ as v; print('cartopy', cartopy.__version__)" 2>&1 | tail -1; /Users/pete/.claude-science/conda/envs/python/bin/python -c "
try:
    import cartopy; print('cartopy', cartopy.__version__)
except Exception as e: print('no cartopy:', type(e).__name__)
try:
    import geopandas; print('geopandas ok')
except Exception as e: print('no geopandas')
"