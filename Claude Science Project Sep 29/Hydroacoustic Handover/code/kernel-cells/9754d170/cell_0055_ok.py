
import importlib
for m in ['gsw','pyproj','obspy','fitz','scipy']:
    try: importlib.import_module(m); print(m,'ok')
    except Exception as e: print(m,'missing')
